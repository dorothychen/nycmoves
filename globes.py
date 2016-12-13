# globes.py
#
# config variables and stuff to import into other scripts
# all dirs and paths relative to main project directory

import os, sys, json
import shapely.geometry
import pandas as pd

from multiprocessing import Pool, Process, cpu_count


citibike_dir = 'data_citibike'
taxi_dir = 'data_taxi'

zone_files = {
    "nta": {
        "filename": "zones_nta.geojson",
        "id": "ntacode",
        "name": "ntaname"
        },
    "taxi": {
        "filename": "zones_taxi.geojson",
        "id": "LocationID",
        "name": "zone"
        },
    "zipcode": {
        "filename": "zones_zipcode.geojson",
        "id": "ZIPCODE",
        "name": "PO_NAME"
        }
}

raw_dir = "raw"
days_dir = "days"
flow_dir = "flow"
dest_count_dir = "dest_counts"

connections_dir = "vis_connections"

zones_prefix = "zones_"

""" Transform coordinates into zone numbers
PARAM OPTIONS (string): nta, taxi, zipcode
"""
def getZoneShapes(definition):
    try:
        zone_filename = zone_files[definition]["filename"]
        zone_id = zone_files[definition]["id"]
    except: 
        raise Error(definition + " is not a valid zone type")

    shapes = []
    with open(zone_filename) as zone_file:
        data = json.load(zone_file)
        zone_data = data['features']
        for zone in zone_data:
            shape = {}
            shape["id"] = zone['properties'][zone_id]
            shape["object"] = shapely.geometry.shape(zone['geometry'])
            shapes.append(shape)
    return shapes


""" Given zone type info, return a dictionary of zoneID => name
Defaults to taxi zones
"""
def zoneIdToName(ZONE_TYPE="taxi", ID_KEY="LocationID", NAME_KEY="zone"):
    zone_filename = "zones_" + ZONE_TYPE + ".geojson"
    with open(zone_filename) as zone_file:
            zone_geojson = json.load(zone_file)
            zone_geojson = map(lambda x: x["properties"], zone_geojson["features"])
    zone_data = {-1: "None"}
    for zone in zone_geojson:
        zone_data[zone[ID_KEY]] = zone[NAME_KEY]
    return zone_data

""" Given zone type info, return a dictionary of zoneID => borough
Defaults to taxi zones
"""
def zoneIdToBorough(ZONE_TYPE="taxi", ID_KEY="LocationID", BOROUGH_KEY="borough"):
    zone_filename = "zones_" + ZONE_TYPE + ".geojson"
    with open(zone_filename) as zone_file:
            zone_geojson = json.load(zone_file)
            zone_geojson = map(lambda x: x["properties"], zone_geojson["features"])
    zone_data = {-1: "None"}
    for zone in zone_geojson:
        zone_data[zone[ID_KEY]] = zone[BOROUGH_KEY]
    return zone_data



FEATURE_COLS = ['pickup_day', 'pickup_hour', 'pickup_zone_taxi']
CLASS_COLS = ['dropoff_zone_taxi']

""" get df for filename
"""
def get_df_features(filename):
    print filename
    df = pd.read_csv(filename, parse_dates=['pickup_datetime', 'dropoff_datetime'])
    df["pickup_day"] = df['pickup_datetime'].apply(lambda t: t.weekday())
    df["pickup_hour"] = df['pickup_datetime'].apply(lambda t: t.hour)

    df = df[FEATURE_COLS + CLASS_COLS]
    return df

""" get full df
"""
def getFullDf():
    num_cores = cpu_count()/2
    print "using " + str(num_cores) + " cores"
    pool = Pool(processes=num_cores)

    filenames = [os.path.join(taxi_dir, days_dir, f) for f in os.listdir(os.path.join(taxi_dir, days_dir)) if f.endswith('csv')]

    # get X, y dataframes in parallel
    dfs = pool.map(get_df_features, filenames)

    # concatenate dataframe array into single df
    df = pd.concat(dfs)
    return df

