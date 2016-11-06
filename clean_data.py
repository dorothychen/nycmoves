import sys
from os import path, listdir
from datetime import datetime
from pandas import read_csv

from globes import taxi_dir

raw_data_path = taxi_dir + "/raw"

dates_read = []
title_line = ["pickup_datetime", "dropoff_datetime", "trip_distance", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude", "fare_amount"]

def write_days(df):
    df.columns = map(str.lower, df.columns)
    df = df.rename(columns={"tpep_pickup_datetime": "pickup_datetime", "tpep_dropoff_datetime": "dropoff_datetime", "lpep_pickup_datetime": "pickup_datetime", "lpep_dropoff_datetime": "dropoff_datetime"})
    df = df[title_line]

    groups = df.groupby(df['pickup_datetime'].map(lambda x: x[:10]))
    for name, group in groups:
        filename = name + ".csv"
        group.to_csv(path.join(taxi_dir, filename), mode='a')
        print filename

def is_float(x):
    try:
        float(x)
        return True
    except:
        return False

def clean_data(filename, df):
    old_len = len(df)
    df = df[df.pickup_latitude.apply(lambda x: is_float(x))]
    df.to_csv(path.join(taxi_dir, filename), mode='w')
    print filename + " from " + str(old_len) + " to " + str(len(df))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: clean_data.py <into-days | clean>"

    option = sys.argv[1]
    if option == "into-days":
        for filename in listdir(raw_data_path):
            if 'tripdata' in filename and filename.endswith(".csv"):
                df = read_csv(path.join(raw_data_path, filename))
                write_days(df)
    elif option == "clean":
        for filename in listdir(taxi_dir):
            if filename.endswith('.csv'):
                 df = read_csv(path.join(taxi_dir, filename))
                 clean_data(filename, df)
    else:
        print "usage: clean_data.py <into-days | clean>"        
