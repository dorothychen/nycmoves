# globes.py
#
# config variables and stuff to import into other scripts
# all dirs and paths relative to main project directory

import json
import shapely.geometry

citibike_dir = 'data_citibike'
taxi_dir = 'data_taxi'
zones_json = 'zone_definitions.json'

raw_dir = "raw"
days_dir = "days"
zones_dir = "zones"
# diffs_pre = "diffs_"

def getZoneShapes():
    shapes = []
    with open(zones_json) as zone_file:
        data = json.load(zone_file)
        zone_data = data['features']
        for zone in zone_data:
            shape = {}
            shape["id"] = zone['properties']['ntacode']
            shape["object"] = shapely.geometry.shape(zone['geometry'])
            shapes.append(shape)
    return shapes