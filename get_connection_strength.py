import os, sys, time
import pandas as pd
from multiprocessing import Pool, Process, cpu_count
from globes import days_dir, taxi_dir, zoneIdToName, dest_count_dir, connections_dir

# ## graphing
# import matplotlib.pyplot as plt
# import matplotlib.style
# matplotlib.style.use('ggplot')

INDEX = [-1] + range(1, 264)

""" Given a dataframe, extract only the relevant feature columns
"""
def _get_features_df(df):
    ## extract features from df
    X = df[['passenger_count', 'pickup_zone_taxi', 'dropoff_zone_taxi']]

    ## get rid of SettingWithCopyWarning
    X.is_copy = False
    df.is_copy = False

    X['dropoff_zone_taxi'] = X['dropoff_zone_taxi'].fillna(-1).astype("int")
    X['pickup_zone_taxi'] = X['pickup_zone_taxi'].fillna(-1).astype("int")
    X['pickup_day'] = df['pickup_datetime'].apply(lambda t: t.weekday())
    X['pickup_hour'] = df['pickup_datetime'].apply(lambda t: t.hour)
    return X

""" Given df, return dataframe with dest counts for each pickup zone
"""
def _get_dests(df):
    X = _get_features_df(df)

    grouped = X.groupby('pickup_zone_taxi', as_index=False)
    rows = []
    for pickup_zone, group in grouped:
        x = pd.DataFrame(group.groupby('dropoff_zone_taxi', as_index=False).size().rename('count'))
        x = x.reset_index(level=0)
        x['pickup_zone'] = pickup_zone
        x = x.pivot(index='pickup_zone', columns='dropoff_zone_taxi', values='count')
        rows.append(x)
        
    dests = pd.concat(rows).fillna(0)
    return dests

""" Given a filename, get the corresponding dataframe and return the destination counts for 
    each pickup zone.
    Used as a helper function, applied on each day's worth of taxi data.
"""
def _agg_dests_helper(filename):
    # get the destination counts for each zone in a day
    filepath = os.path.join(taxi_dir, days_dir, filename)
    df = pd.read_csv(filepath, parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)

    starttime = time.time()
    dests = _get_dests(df)
    print filename + " processed in " + str(time.time() - starttime) + " seconds"

    return dests

""" Given a list of filenames, get the total dropoff zone counts for each pickup zones across all files
"""
def get_agg_dests(filenames):
    num_cores = cpu_count()/4
    print "using " + str(num_cores) + " cores"
    pool = Pool(processes=num_cores)

    dests_arr = pool.map(_agg_dests_helper, filenames)
    print "num days to aggregate: %d" % len(dests_arr)

    # aggregate destination counts
    all_dests = pd.DataFrame(0, index=INDEX, columns=INDEX)
    for dests in dests_arr:
        all_dests = all_dests + dests
        all_dests = all_dests.fillna(0)

    all_dests.to_csv(os.path.join(taxi_dir, dest_count_dir, filename), mode='w')

# """ Output bar graphs that show dropoff zone counts for each pickup zone.
#     Input: filename of csv file of total zone -> dest counts
# """
# def get_graphs(filename):
#     zone_data = zoneIdToName()
#     filepath = os.path.join(taxi_dir, dest_count_dir, filename)
#     df = pd.read_csv(filepath, index_col=0)

#     # iterate through each row (aka pickup zone)
#     for pickup_zone, row in df.iterrows():
#         if zone_data.get(pickup_zone):
#             row = row.sort_values(ascending=False)
#             row.index = row.index.astype(int)
            
#             # graph
#             plt.figure(1, figsize=(80,20))
#             ax = row.plot(kind="bar")
#             ax.set_title("2016-01 through 2016-06; trips from zone: " + zone_data[pickup_zone])
#             ax.set_xlabel("dropoff zone")
#             ax.set_ylabel("num dropoffs")
            
#             x_labels = get_zone_names(row.index)
#             ax.set_xticklabels(x_labels)

#             # save 
#             graph_path = os.path.join(connections_dir, "taxi" + str(pickup_zone) + '.png')
#             plt.savefig(graph_path, bbox_inches='tight')

""" Given filename for matrix of pickup zone -> dropoff zone counts, return a json file
    corresponding pickup zones to dropoff zones and counts
"""
def get_json(filename):
    df = pd.read_csv(filename, index_col=0)
    df.index.name = "pickup_zone"
    json_filename = os.path.splitext(filename)[0] + '.json'
    
    print json_filename
    df.to_json(json_filename, orient='index')


USAGE = "python get_connection_strength < --agg | --json [input filename] | --graphs [input filename]>"
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: " + USAGE
        exit()

    opt = sys.argv[1]
    if opt == "--agg":
        filenames = [filename for filename in os.listdir(os.path.join(taxi_dir, days_dir)) if filename.endswith(".csv")]
        get_agg_dests(filenames)
    elif opt == "--json" and len(sys.argv) >= 3:
        filename = sys.argv[2]
        get_json(filename)
    elif opt == "--graphs" and len(sys.argv) >= 3:
        filename = sys.argv[2]
        get_graphs(filename)
    else:
        print "usage: " + USAGE
    


