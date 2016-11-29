# globes.py
#
# config variables and stuff to import into other scripts
# all dirs and paths relative to main project directory

import json
import shapely.geometry

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

