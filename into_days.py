from os import path, listdir
from datetime import datetime
from pandas import read_csv

taxi_dir = "data_taxi"
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


if __name__ == "__main__":
    for filename in listdir(raw_data_path):
        if 'tripdata' in filename and filename.endswith(".csv"):
            df = read_csv(path.join(raw_data_path, filename))
            write_days(df)