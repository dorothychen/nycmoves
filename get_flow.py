# get_flow.py
# 
# modify trip by trip dataframes to inflow/outflow per zone every <increment> seconds

# time increments, in seconds
import pandas as pd
import os, sys

from globes import taxi_dir, days_dir, zones_prefix, flow_dir, getZoneShapes

ZONE_TYPE = "taxi"

shapes = getZoneShapes(ZONE_TYPE)
shapeIds = map(lambda s: s['id'], shapes)
columns = shapeIds

""" By half hour
"""
def timeIndex(t):
    hour = "{:02d}".format(t.hour)
    half_hour = "00" if t.minute/30 == 0 else "30"
    return hour + ":" + half_hour

""" Given a grouping of rows with the same minute (or other timeframe), 
    return single-line df with the counts of dropoffs per zone in that time 
"""
def getRow(t, tgroup, zone_type):    
    countZones = tgroup.groupby(by=[zone_type]).size()
    items = {}
    for k, v in countZones.iteritems():
        items[k] = v
    return pd.DataFrame(items, columns=columns, index=[t])


def handleDf(df):
    # group by the time, by hour
    dropoff_groups = df.groupby(df['dropoff_datetime'].map(timeIndex))
    pickup_groups = df.groupby(df['pickup_datetime'].map(timeIndex))

    # positive values for the # of dropoffs per zone
    dropoff_frames = [getRow(t, tgroup, 'dropoff_zone_' + ZONE_TYPE) for t, tgroup in dropoff_groups]
    dropoff_all = pd.concat(dropoff_frames)
    dropoff_all = dropoff_all.fillna(value=0)

    # subtract from the pickup times
    pickup_frames = [getRow(t, tgroup, 'pickup_zone_' + ZONE_TYPE) for t, tgroup in pickup_groups]
    pickup_all = pd.concat(pickup_frames)
    pickup_all = pickup_all.fillna(value=0)

    return dropoff_all - pickup_all

def toMvmt(to_json=False):
    for filename in os.listdir(os.path.join(taxi_dir, days_dir)):
        if filename.endswith(".csv") and "01-03" in filename:
            df = pd.read_csv(os.path.join(taxi_dir, days_dir, filename), parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)
            diffs_df = handleDf(df)

            # output csv or json
            print os.path.splitext(filename)[0]
            diffs_df.to_csv(os.path.join(taxi_dir, flow_dir, filename))
            if to_json:
                df = pd.read_csv(os.path.join(taxi_dir, flow_dir, filename), index_col=0)
                df.index.name = "datetime"
                json_filename = os.path.splitext(filename)[0] + '.json'
                df.to_json(os.path.join(taxi_dir, flow_dir, json_filename), orient='index')
            

if __name__ == "__main__":
    if len(sys.argv) == 2:
        opt = sys.argv[1]
        if opt == "--json":
            print "Creating json of zone flow"
            toMvmt(to_json=True)
    else:
        print "Creating csv of zone flow"
        toMvmt()