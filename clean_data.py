import sys
import os
from datetime import datetime
from pandas import read_csv

from globes import taxi_dir, raw_dir, days_dir

dates_read = []
title_line = ["pickup_datetime", "dropoff_datetime", "trip_distance", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude", "fare_amount", "passenger_count"]

def write_days(df):
    df.columns = map(str.lower, df.columns)
    df = df.rename(columns={"tpep_pickup_datetime": "pickup_datetime", "tpep_dropoff_datetime": "dropoff_datetime", "lpep_pickup_datetime": "pickup_datetime", "lpep_dropoff_datetime": "dropoff_datetime"})
    df = df[title_line]

    groups = df.groupby(df['pickup_datetime'].map(lambda x: x[:10]))
    for name, group in groups:
        filename = name + ".csv"
        group.to_csv(os.path.join(taxi_dir, days_dir, filename), mode='a')
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
    df.to_csv(os.path.join(taxi_dir, days_dir, filename), mode='w')
    print filename + " from " + str(old_len) + " to " + str(len(df))

def sort_data(filename, df):
    old_len = len(df)
    df = df.sort_values(by='pickup_datetime')
    df.to_csv(os.path.join(taxi_dir, days_dir, filename), mode='w')
    print filename + " from " + str(old_len) + " to " + str(len(df))


def rename_zones(filename, df):
    old_len = len(df)
    df = df.rename(columns={"pickup_zone": "pickup_zone_nta", "dropoff_zone": "dropoff_zone_nta"})
    df.to_csv(os.path.join(taxi_dir, days_dir, filename), mode='w')
    print filename + " from " + str(old_len) + " to " + str(len(df))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: clean_data.py <into-days | clean | sort | rename-zones>"
        exit()

    option = sys.argv[1]
    if option == "into-days":
        for filename in os.listdir(os.path.join(taxi_dir, raw_dir)):
            if 'tripdata' in filename and filename.endswith(".csv"):
                df = read_csv(os.path.join(taxi_dir, raw_dir, filename), index_col=0)
                write_days(df)
                
                # delete original downloaded file to free up space
                os.remove(os.path.join(taxi_dir, raw_dir, filename))

    elif option == "clean":
        for filename in os.listdir(os.path.join(taxi_dir, days_dir)):
            if filename.endswith('.csv'):
                 df = read_csv(os.path.join(taxi_dir, days_dir, filename), index_col=0)
                 clean_data(filename, df)

    elif option == "sort":
        for filename in os.listdir(os.path.join(taxi_dir, days_dir)):
            if filename.endswith(".csv"):
                df = read_csv(os.path.join(taxi_dir, days_dir, filename), parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)
                sort_data(filename, df)

    elif option == "rename-zones":
        for filename in os.listdir(os.path.join(taxi_dir, days_dir)):
            if filename.endswith(".csv"):
                df = read_csv(os.path.join(taxi_dir, days_dir, filename), index_col=0)
                rename_zones(filename, df)

    else:
        print "usage: clean_data.py <into-days | clean | rename-zones>"



