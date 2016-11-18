import os, sys
import pandas as pd 
from globes import taxi_dir, zones_prefix, diffs_prefix

if __name__ == "__main__":
    for filename in os.listdir(taxi_dir):
        if filename.endswith(".csv") and diffs_prefix in filename and "01-01" in filename:
            df = pd.read_csv(os.path.join(taxi_dir, filename), index_col=0)
            groups = df.groupby(df.index.map(lambda t: t[:2])).sum()
            groups.to_csv("testout.csv")