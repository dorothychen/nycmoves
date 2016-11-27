##### predict.py ##### 


## load the df

import os, sys
import pandas as pd
from globes import taxi_dir, days_dir

filename = "zones_2016-01-20.csv"
filepath = os.path.join(taxi_dir, days_dir, filename)

df = pd.read_csv(filepath, parse_dates=['pickup_datetime', 'dropoff_datetime'], index_col=0)

## extract features from df
X = df[['pickup_datetime', 'passenger_count', 'pickup_zone_taxi', 'dropoff_zone_taxi']]
X['dropoff_zone_taxi'] = X['dropoff_zone_taxi'].fillna(-1).astype("int")
X['pickup_zone_taxi'] = X['pickup_zone_taxi'].fillna(-1).astype("int")
X['pickup_day'] = X['pickup_datetime'].apply(lambda t: t.weekday())
X['pickup_hour'] = X['pickup_datetime'].apply(lambda t: t.hour)

