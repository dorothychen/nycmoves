""" Load the hd5 files
"""

from os import path, listdir
from pandas import read_csv
import sys
import json
import shapely.geometry


taxi_dir = 'data_taxi'
prefix = "taxi_zones"

""" Transform coordinates into zone numbers
"""

def getShapes():
    shapes = []
    with open("static/zones2.json") as zone_file:
        data = json.load(zone_file)
        zone_data = data['features']
        for zone in zone_data:
            shape = {}
            shape["id"] = zone['properties']['ntacode']
            shape["object"] = shapely.geometry.shape(zone['geometry'])
            shapes.append(shape)
    return shapes
            
shapes = getShapes()

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
    df['pickup_zone'] = df[['pickup_latitude', 'pickup_longitude']].apply(getShapeFromPoint, axis=1)
    df['dropoff_zone'] = df[['dropoff_latitude', 'dropoff_longitude']].apply(getShapeFromPoint, axis=1)
    return df

if __name__ == "__main__":
    dfs = []
    for filename in listdir(taxi_dir):
        if filename.endswith(".csv") and "_test" in filename:
            print filename
            df = read_csv(path.join(taxi_dir, filename))
            df = getZones(df)
            df.to_csv(path.join(taxi_dir, "zones_" + filename))
