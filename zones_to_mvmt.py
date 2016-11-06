# zones_to_mvmt.py
# 
# modify trip by trip dataframes to inflow/outflow per zone every <increment> seconds

# time increments, in seconds
from os import path, listdir
from pandas import read_csv
import sys

from globes import taxi_dir, zones_prefix

INCREMENT = 30

def handleDf(df):
    pass

def toMvmt():
    for filename in listdir(taxi_dir):
        if filename.endswith(".csv") and zones_prefix in filename:
            df = read_csv(path.join(taxi_dir, filename))
            handleDf(df)
            
            

if __name__ == "__main__":
    toMvmt()