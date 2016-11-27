import pandas as pd
import os, sys

def to_json(filename):
    df = pd.read_csv(filename, index_col=0)
    df.index.name = "datetime"
    json_filename = os.path.splitext(filename)[0] + '.json'
    
    print json_filename
    df.to_json(json_filename, orient='index')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: utils.py <to-json> <input filename>"
    
    elif len(sys.argv) == 3 and sys.argv[1] == "to-json":
        filename = sys.argv[2]
        to_json(filename)
