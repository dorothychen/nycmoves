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
        "id": "ntacode"
        },
    "taxi": {
        "filename": "zones_taxi.geojson",
        "id": "LocationID"
        },
    "zipcode": {
        "filename": "zones_zipcode.geojson",
        "id": "ZIPCODE"
        }
}

raw_dir = "raw"
days_dir = "days"
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