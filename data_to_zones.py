# data_to_zones.py
# 
# transform lat/lng datapoints to zones as given by a geoJSON file

""" Load the hd5 files
"""

from os import path, listdir
from pandas import read_csv
import time
import sys
import json
import shapely.geometry

from globes import taxi_dir, zones_json, zones_dir, getZoneShapes, days_dir


""" Transform coordinates into zone numbers
"""
shapes = getZoneShapes()

def getShapeFromPoint(row):
    lat = float(row[0])
    lng = float(row[1])
    point = shapely.geometry.Point(lng,lat)
    for shape in shapes:
        if shape["object"].contains(point):
            print lat, lng, shape["id"]
            return shape["id"]
    return None

def getZones(df):
    time1 = time.clock()
    df['pickup_zone'] = df[['pickup_latitude', 'pickup_longitude']].apply(getShapeFromPoint, axis=1)
    time2 = time.clock()
    df['dropoff_zone'] = df[['dropoff_latitude', 'dropoff_longitude']].apply(getShapeFromPoint, axis=1)
    time3 = time.clock()
    print str(len(df)) + " lines in " + str(time2-time1)
    print str(len(df)) + " lines in " + str(time3-time2)
    return df

if __name__ == "__main__":
    dfs = []
    for filename in listdir(path.join(taxi_dir, days_dir)):
        if filename.endswith(".csv"):
            print filename
            df = read_csv(path.join(taxi_dir, days_dir, filename), index_col=0)
            df = getZones(df)
            df.to_csv(path.join(taxi_dir, zones_dir, filename))
