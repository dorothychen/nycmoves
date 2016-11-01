from os import path
import pandas as pd
import time

taxi_dir = 'data_taxi'
taxi_filenames = [
    'yellow_tripdata_2016-01.csv', 
    'yellow_tripdata_2016-02.csv', 
    'yellow_tripdata_2016-03.csv', 
    'yellow_tripdata_2016-04.csv', 
    'yellow_tripdata_2016-05.csv', 
    'yellow_tripdata_2016-06.csv'
    ]

taxi_datatypes = {
    'VendorID': int,
    'tpep_pickup_datetime': str,
    'tpep_dropoff_datetime': str,
    'passenger_count': int,
    'trip_distance': float,
    'pickup_longitude': float,
    'pickup_latitude': float,
    'RatecodeID': int,
    'store_and_fwd_flag': str,
    'dropoff_longitude': float,
    'dropoff_latitude': float,
    'payment_type': int,
    'fare_amount': float,
    'extra': float,
    'mta_tax': float,
    'tip_amount': float,
    'tolls_amount': float,
    'improvement_surcharge': float,
    'total_amount': float}

def save_as_hdf5(filename, prefix):
    starttime = time.clock()
    df = pd.read_csv(path.join(taxi_dir, filename), dtype=taxi_datatypes)
    year = filename[16:20]
    month = filename[21:23]
    df.to_hdf(path.join(taxi_dir, prefix + '_' + str(year) + '_' + str(month) + '.h5'), 'data',
        format='table', 
        mode='w',
        complevel=4)   
    print "completed " + filename + " in " + str(time.clock() - starttime) + " seconds."

if __name__ == "__main__":
    for filename in taxi_filenames:
        save_as_hdf5(filename, 'taxi')


