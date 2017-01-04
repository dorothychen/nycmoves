## imports
import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

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

def gridSearchRandomForest(X, y):
    parameters = {'n_estimators':[1, 2, 4, 8, 20, 50, 100], 'max_depth':[10, 20, 50]}
    reg = RandomForestRegressor()
    grid = GridSearchCV(reg, parameters, n_jobs=15, verbose=4)
    grid.fit(X, y)
    print grid.cv_results_

    return grid

if __name__ == "__main__":
    pass

