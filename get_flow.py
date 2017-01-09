# get_flow.py
# 
# modify trip by trip dataframes to inflow/outflow per zone every hour

import pandas as pd
import os, sys,time
from multiprocessing import Pool, Process, cpu_count
from globes import taxi_dir, days_dir, zones_prefix, flow_dir, getZoneShapes

ZONE_TYPE = "taxi"

shapes = getZoneShapes(ZONE_TYPE)
shapeIds = map(lambda s: s['id'], shapes)
columns = shapeIds

ZONE_IDS = [-1] + range(1, 264)
INDEX = ['day', 'hour']

# flag for if this script outputs the total taxi activity per zone, or the net flow
# FLOW_TYPE = "NET_FLOW" | "TOTAL_ACTIVITY"
FLOW_TYPE = "NET_FLOW"

""" Given a grouping of rows with the same minute (or other timeframe), 
    return single-line df with the counts of dropoffs per zone in that time 
"""
def getRow(t, tgroup, zone_type):    
    countZones = tgroup.groupby(by=[zone_type]).size()
    items = {}
    for k, v in countZones.iteritems():
        items[k] = v
    return pd.DataFrame(items, columns=columns, index=[t])

""" 
"""
def _dayToFlow(df):
    df['dropoff_zone_taxi'] = df['dropoff_zone_taxi'].fillna(-1).astype("int")
    df['pickup_zone_taxi'] = df['pickup_zone_taxi'].fillna(-1).astype("int")

    df['pickup_day'] = df['pickup_datetime'].apply(lambda t: t.weekday())
    day_groups = df.groupby('pickup_day', as_index=False);

    nets = []
    for day, day_group in day_groups:
        # group by the time, by hour
        dropoff_groups = day_group.groupby(day_group['dropoff_datetime'].map(lambda t: t.hour))
        pickup_groups = day_group.groupby(day_group['pickup_datetime'].map(lambda t: t.hour))

        # positive values for the # of dropoffs per zone
        dropoff_frames = [getRow(t, tgroup, 'dropoff_zone_' + ZONE_TYPE) for t, tgroup in dropoff_groups]
        dropoff_all = pd.concat(dropoff_frames)
        dropoff_all = dropoff_all.fillna(value=0)
        
        # subtract from the pickup times
        pickup_frames = [getRow(t, tgroup, 'pickup_zone_' + ZONE_TYPE) for t, tgroup in pickup_groups]
        pickup_all = pd.concat(pickup_frames)
        pickup_all = pickup_all.fillna(value=0)

        if FLOW_TYPE == "NET_FLOW":
            net = dropoff_all - pickup_all
        elif FLOW_TYPE == "TOTAL_ACTIVITY":
            net = dropoff_all + pickup_all
        net['hour'] = net.index
        net['day'] = day
        nets.append(net)

    net_flows = pd.concat(nets).fillna(0)
    net_flows = net_flows.set_index(INDEX)
    return net_flows

def dayToFlow(filename):
    filepath = os.path.join(taxi_dir, days_dir, filename)
    df = pd.read_csv(filepath, parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)
    
    starttime = time.time()
    net_flows = _dayToFlow(df)
    print filename + " processed in " + str(time.time() - starttime) + " seconds"
    return net_flows

""" Given a list of filenames, get the total dropoff zone counts for each pickup zones across all files
"""
def get_agg_flows(filenames):
    num_cores = cpu_count()/2
    print "using " + str(num_cores) + " cores"
    pool = Pool(processes=num_cores)

    nets_arr = pool.map(dayToFlow, filenames)
    print "num days to aggregate: %d" % len(nets_arr)

    # aggregate destination counts
    X = pd.DataFrame(0, index=[0], columns=INDEX + ZONE_IDS)
    X = X.set_index(INDEX)
    for df in nets_arr:
        X = X.add(df, fill_value=0)
        X = X.fillna(0)
    
    if FLOW_TYPE == "NET_FLOW":
        X.to_csv(os.path.join(taxi_dir, flow_dir, "netflow.csv"), mode='w')
    elif FLOW_TYPE == "TOTAL_ACTIVITY":
        X.to_csv(os.path.join(taxi_dir, flow_dir, "total_activity.csv"), mode='w')



if __name__ == "__main__":
    print "Creating csv of zone flow"
    filenames = [filename for filename in os.listdir(os.path.join(taxi_dir, days_dir)) if filename.endswith(".csv")]
    get_agg_flows(filenames)