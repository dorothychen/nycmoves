# zones_to_mvmt.py
# 
# modify trip by trip dataframes to inflow/outflow per zone every <increment> seconds

# time increments, in seconds
from os import path, listdir
import pandas as pd
import sys

from globes import taxi_dir, zones_prefix, diffs_prefix, getZoneShapes

INCREMENT = 30
shapes = getZoneShapes()
shapeIds = map(lambda s: s['id'], shapes)
columns = shapeIds

""" Given a grouping of rows with the same minute (or other timeframe), 
    return single-line df with the counts of dropoffs per zone in that time 
"""
def getDropoffRow(t, tgroup, zone_type):    
    countZones = tgroup.groupby(by=[zone_type]).size()
    items = {}
    for k, v in countZones.iteritems():
        items[k] = v
    return pd.DataFrame(items, columns=columns, index=[t])


def handleDf(df):
    # group by the time, by minute
    dropoff_groups = df.groupby(df['dropoff_datetime'].map(lambda t: "{:02d}:{:02d}".format(t.hour, t.minute)))
    pickup_groups = df.groupby(df['pickup_datetime'].map(lambda t: "{:02d}:{:02d}".format(t.hour, t.minute)))

    # positive values for the # of dropoffs per zone
    dropoff_frames = [getDropoffRow(t, tgroup, 'dropoff_zone') for t, tgroup in dropoff_groups]
    dropoff_all = pd.concat(dropoff_frames)
    dropoff_all = dropoff_all.fillna(value=0)

    # subtract from the pickup times
    pickup_frames = [getDropoffRow(t, tgroup, 'pickup_zone') for t, tgroup in pickup_groups]
    pickup_all = pd.concat(pickup_frames)
    pickup_all = pickup_all.fillna(value=0)

    return dropoff_all - pickup_all

def toMvmt():
    for filename in listdir(taxi_dir):
        if filename.endswith(".csv") and zones_prefix in filename and "01-01" in filename:
            df = pd.read_csv(path.join(taxi_dir, filename), parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)
            diffs_df = handleDf(df)
            diffs_df.to_csv(path.join(taxi_dir, diffs_prefix + filename))
            

if __name__ == "__main__":
    toMvmt()