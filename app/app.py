import os
from flask import Flask, render_template, request, jsonify, url_for
from flask_assets import Environment, Bundle
import pandas as pd

app = Flask(__name__)
APP_ROOT = os.path.dirname(__file__)
DEST_COUNT_FILE = "zones_2016-02-13.csv";
NET_FLOW_FILE = "flow.csv"

assets = Environment(app)

# relative to static dir
js_all = Bundle(
    'js/map.js',
    'js/netflow.js',
    'js/destcounts.js',
    output='generated/js_all.js')
assets.register('js_all', js_all)

jsx_all = Bundle(
    'js/map.jsx',
    'js/index.jsx',
    output="generated/jsx_all.jsx")
assets.register('jsx_all', jsx_all)

css_all = Bundle(
    'scss/map.scss',
    filters='pyscss',
    output='generated/css_all.css')
assets.register('css_all', css_all)

@app.route('/')
def index():
    return render_template('map.html')

def get_dest_count_data(days, hours):
    df = pd.read_csv(os.path.join(APP_ROOT, 'static', DEST_COUNT_FILE))
    df = df.loc[df['pickup_day'].isin(days)]
    df = df.loc[df['pickup_hour'].isin(hours)]
    df = df.groupby('pickup_zone').sum()

    # drop unneeded columns
    df = df.drop('pickup_day', 1)
    df = df.drop('pickup_hour', 1)
    return jsonify(df.to_json(orient="index"))

def get_net_flow_data(days, hours):
    df = pd.read_csv(os.path.join(APP_ROOT, 'static', NET_FLOW_FILE))
    df = df.loc[df['day'].isin(days)]
    df = df.loc[df['hour'].isin(hours)]

    # drop unneeded columns
    df = df.drop('day', 1)
    df = df.drop('hour', 1)

    df = df.sum()

    return jsonify(df.to_json(orient="index"))

@app.route('/api/get_color_data', methods=["GET"])
def get_color_data():
    """ color_data should map zoneid => {to_zoneid=>value, etc.}
    """
    hours = filter(lambda x: int(request.args['hours'].split(",")[x]) == 1, range(24))
    days = filter(lambda x: int(request.args['days'].split(",")[x]) == 1, range(7))
    mode = request.args["mode"]

    if mode == "NET_FLOW":
        return get_net_flow_data(days, hours)
    elif mode == "DEST_COUNT":
        return get_dest_count_data(days, hours)
    else:
        return jsonify({})



if __name__ == "__main__":
    app.run(debug=True)