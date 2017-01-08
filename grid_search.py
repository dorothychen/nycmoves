## imports
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, make_scorer


from globes import taxi_dir, days_dir
from multiprocessing import Pool, Process, cpu_count

FEATURE_COLS = ['pickup_day', 
                'pickup_hour', 
                'pickup_latitude', 
                'pickup_longitude']

Y_COLS = ['dropoff_latitude', 
          'dropoff_longitude']

""" get feature and label rows from filename
"""
def getXyAll(filename):
    df = pd.read_csv(filename, parse_dates=['pickup_datetime', 'dropoff_datetime'])
    
    # get rid of zones that don't actually really exist THIS IS IMPORTANT
    df = df.loc[df['pickup_zone_taxi'] != -1]
    df = df.loc[df['dropoff_zone_taxi'] != -1]
    df = df.dropna()
    
    df["pickup_day"] = df['pickup_datetime'].apply(lambda t: t.weekday())
    df["pickup_hour"] = df['pickup_datetime'].apply(lambda t: t.hour)

    df_X = df[FEATURE_COLS]
    df_Y = df[Y_COLS]
    return df_X, df_Y

""" get feature and label rows from filename, only for Manhattan
"""
def getXyManhattan(filename):
    df = pd.read_csv(filename, parse_dates=['pickup_datetime', 'dropoff_datetime'])

    # get rid of zones that don't actually really exist THIS IS IMPORTANT
    df = df.loc[df['pickup_zone_taxi'] != -1]
    df = df.loc[df['dropoff_zone_taxi'] != -1]
    df = df.dropna()
    
    # keep only Manhattan pickups
    df = df.loc[df['pickup_borough'] == "Manhattan"]
    
    df["pickup_day"] = df['pickup_datetime'].apply(lambda t: t.weekday())
    df["pickup_hour"] = df['pickup_datetime'].apply(lambda t: t.hour)

    df_X = df[FEATURE_COLS]
    df_Y = df[Y_COLS]
    return df_X, df_Y   

""" get X, y in numpy arrays from relevant data
"""
def getDataNumpy(get_Xy_func):
    num_cores = cpu_count()/2
    print "using " + str(num_cores) + " cores"
    pool = Pool(processes=num_cores)

    filenames = [os.path.join(taxi_dir, days_dir, f) for f in os.listdir(os.path.join(taxi_dir, days_dir)) if f.endswith('csv')]
    
    # get X, y dataframes in parallel
    Xy_arr = pool.map(get_Xy_func, filenames)
    pool.terminate()

    # separate out to array of X dataframes and y dataframes
    dfs_X = map(lambda pair: pair[0], Xy_arr)
    dfs_y = map(lambda pair: pair[1], Xy_arr)

    # concatenate dataframe array into single df
    df_X = pd.concat(dfs_X)
    df_y = pd.concat(dfs_y)

    # convert df to numpy arrays
    X = df_X.as_matrix()
    y = df_y.as_matrix()

    print df_X.shape, df_y.shape
    print X.shape, y.shape

    return X, y

def RMSE(y, y_pred):
    rmsevalid = np.sqrt(mean_squared_error(y,y_pred, multioutput="raw_values"))
    return rmsevalid


def gridSearchRandomForest(X, y, err_func=None):
    parameters = {'n_estimators':[1, 2, 4, 8], 'max_depth':[10, 20]}
    reg = RandomForestRegressor()
    if err_func is None:
        grid = GridSearchCV(reg, parameters, cv=6, n_jobs=15, verbose=4)
    else:
        scorer = make_scorer(err_func, greater_is_better=False)
        grid = GridSearchCV(reg, parameters, cv=6, n_jobs=15, verbose=4, scoring=scorer)
    grid.fit(X, y)
    return grid

from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn import linear_model
from sklearn.model_selection import KFold
from operator import add

## alpha = 0.000100, eta0 = 0.001000, RMSE_sum = 0.064487, RMSE = 0.029309, 0.035178, R^2 = 0.267938
## fake grid search because of MultiOutputRegressor(linear_model.SGDRegressor()) not taking params properly
def gridSearchSGD(X, y, err_func):
    parameters = {"alpha":[0.01, 0.001, 0.0001, 0.00001], 
        "eta0":[0.1, 0.01, 0.001]}
    
    best_score = 10000
    best_alpha = None
    best_eta0 = None
    best_rmse = None
    best_r2 = None
    for alpha in parameters["alpha"]:
        for eta0 in parameters["eta0"]:

            kf = KFold(n_splits=6, shuffle=True)
            res = {
                "train_r2": 0.0,
                "valid_r2": 0.0,
                "train_rmse": [0.0, 0.0],
                "valid_rmse": [0.0, 0.0]
            }
            for train_index, test_index in kf.split(X):
                X_train, X_test = X[train_index], X[test_index] 
                y_train, y_test = y[train_index], y[test_index] 
                
                # scale data
                scaler = StandardScaler()
                scaler.fit(X_train)
                X_train = scaler.transform(X_train)
                X_test = scaler.transform(X_test)  # apply same transformation to test data
                
                reg = MultiOutputRegressor(linear_model.SGDRegressor(alpha=alpha, eta0=eta0, warm_start=True))
                reg.fit(X_train, y_train)
                res["train_r2"] += reg.score(X_train, y_train)
                res["valid_r2"] += reg.score(X_test, y_test)
                res["train_rmse"] = map(add,res["train_rmse"], RMSE(reg.predict(X_train),y_train))
                res["valid_rmse"] = map(add, res["valid_rmse"], RMSE(reg.predict(X_test),y_test))


            # average of error scores
            res["train_r2"] = res["train_r2"] / kf.get_n_splits(X) 
            res["valid_r2"] = res["valid_r2"] / kf.get_n_splits(X) 
            res["train_rmse"][0] = res["train_rmse"][0] / kf.get_n_splits(X) 
            res["train_rmse"][1] = res["train_rmse"][1] / kf.get_n_splits(X) 
            res["valid_rmse"][0] = res["valid_rmse"][0] / kf.get_n_splits(X) 
            res["valid_rmse"][1] = res["valid_rmse"][1] / kf.get_n_splits(X) 

            print " R^2 (train) = %0.3f, R^2 (valid) = %0.3f, RMSE (train) = %f, %f, RMSE (valid) = %f, %f" \
                % (res["train_r2"], res["valid_r2"], res["train_rmse"][0],res["train_rmse"][1], res["valid_rmse"][0],res["valid_rmse"][1])
            print ""

            if res["valid_rmse"][0] + res["valid_rmse"][1] < best_score:
                best_score = res["valid_rmse"][0] + res["valid_rmse"][1]
                best_rmse = res["valid_rmse"]
                best_r2 = res["valid_r2"]
                best_alpha = alpha
                best_eta0 = eta0

    print "BEST: alpha = %f, eta0 = %f, RMSE_sum = %f, RMSE = %f, %f, R^2 = %f" \
        % (best_alpha, best_eta0, best_score, best_rmse[0], best_rmse[1], best_r2)


def SGD_CV(X, y):
    kf = KFold(n_splits=6, shuffle=True)
    res = {
        "train_r2": 0.0,
        "valid_r2": 0.0,
        "train_rmse": [0.0, 0.0],
        "valid_rmse": [0.0, 0.0]
    }
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index] 
        y_train, y_test = y[train_index], y[test_index] 

        # scale data
        scaler = StandardScaler()
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)  # apply same transformation to test data

        reg = MultiOutputRegressor(linear_model.SGDRegressor(alpha=0.0001, eta0=0.001))
        reg.fit(X_train, y_train)
        res["train_r2"] += reg.score(X_train, y_train)
        res["valid_r2"] += reg.score(X_test, y_test)
        rmse_train = RMSE(reg.predict(X_train),y_train)
        rmse_valid = RMSE(reg.predict(X_test),y_test)
        print rmse_train, rmse_valid
        res["train_rmse"] = map(add,res["train_rmse"], rmse_train)
        res["valid_rmse"] = map(add,res["valid_rmse"], rmse_valid)

    # average of error scores
    # average of error scores
    res["train_r2"] = res["train_r2"] / kf.get_n_splits(X) 
    res["valid_r2"] = res["valid_r2"] / kf.get_n_splits(X) 
    res["train_rmse"][0] = res["train_rmse"][0] / kf.get_n_splits(X) 
    res["train_rmse"][1] = res["train_rmse"][1] / kf.get_n_splits(X) 
    res["valid_rmse"][0] = res["valid_rmse"][0] / kf.get_n_splits(X) 
    res["valid_rmse"][1] = res["valid_rmse"][1] / kf.get_n_splits(X) 

    print " R^2 (train) = %0.3f, R^2 (valid) = %0.3f, RMSE (train) = %f, %f, RMSE (valid) = %f, %f" \
        % (res["train_r2"], res["valid_r2"], res["train_rmse"][0],res["train_rmse"][1], res["valid_rmse"][0],res["valid_rmse"][1])
    print ""
    


def RandomForestCV(X, y):
    kf = KFold(n_splits=6, shuffle=True)
    res = {
        "train_r2": 0.0,
        "valid_r2": 0.0,
        "train_rmse": [0.0, 0.0],
        "valid_rmse": [0.0, 0.0]
    }
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index] 
        y_train, y_test = y[train_index], y[test_index] 

        reg = RandomForestRegressor(n_estimators=8, max_depth=20, n_jobs=-1, verbose=3, warm_start=True)
        reg.fit(X_train, y_train)
        res["train_r2"] += reg.score(X_train, y_train)
        res["valid_r2"] += reg.score(X_test, y_test)
        res["train_rmse"] = map(add,res["train_rmse"], RMSE(reg.predict(X_train),y_train))
        res["valid_rmse"] = map(add, res["valid_rmse"], RMSE(reg.predict(X_test),y_test))

    # average of error scores
    res["train_r2"] = res["train_r2"] / kf.get_n_splits(X) 
    res["valid_r2"] = res["valid_r2"] / kf.get_n_splits(X) 
    res["train_rmse"][0] = res["train_rmse"][0] / kf.get_n_splits(X) 
    res["train_rmse"][1] = res["train_rmse"][1] / kf.get_n_splits(X) 
    res["valid_rmse"][0] = res["valid_rmse"][0] / kf.get_n_splits(X) 
    res["valid_rmse"][1] = res["valid_rmse"][1] / kf.get_n_splits(X) 

    print " R^2 (train) = %0.3f, R^2 (valid) = %0.3f, RMSE (train) = %f, %f, RMSE (valid) = %f, %f" \
        % (res["train_r2"], res["valid_r2"], res["train_rmse"][0],res["train_rmse"][1], res["valid_rmse"][0],res["valid_rmse"][1])
    print ""

    
if __name__ == "__main__":
    pass

