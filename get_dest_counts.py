# get_dest_counts.py
# 
# 

import pandas as pd
import os, sys, time
from globes import taxi_dir, days_dir, dest_count_dir, getFullDf

ZONE_COLS = [
    "pickup_day",
    "pickup_hour",
    "pickup_zone_taxi", 
    "dropoff_zone_taxi", 
    "pickup_borough", 
    "dropoff_borough"
]

def get_dest_counts(df=None):
    if df is None:
        df = getFullDf()
        df = df[ZONE_COLS]

    groups = df.groupby(["pickup_day", "pickup_hour", "pickup_zone_taxi"])
    df_arr = []
    for name, group in groups:
        print name
        counts = pd.DataFrame(group.groupby("dropoff_zone_taxi").size().rename("count"))
        counts = counts.reset_index()
        
        # reset index for pivoting
        n = len(counts.index)
        counts.index = [name] * n

        # pivot
        row = counts.pivot(columns="dropoff_zone_taxi", values="count")
        df_arr.append(row)

    new_df = pd.concat(df_arr)
    new_df.fillna(0)
    return new_df


if __name__ == "__main__":
    df = get_dest_counts()
    df.to_json(os.path.join(taxi_dir, dest_count_dir, "dest_counts.json"), orient="index")
    df.to_csv(os.path.join(taxi_dir, dest_count_dir, "dest_counts.csv"))



