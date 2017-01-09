import os
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_assets import Environment, Bundle
import pandas as pd

app = Flask(__name__)
APP_ROOT = os.path.dirname(__file__)
DEST_COUNT_FILE = "zones_2016-02-13.csv";
NET_FLOW_FILE = "flow.csv"

assets = Environment(app)

# relative to static dir
js_net_flow = Bundle(
    'thirdparty/nouislider.min.js',
    'js/map.js',
    'js/netflow.js',
    output='generated/js_net_flow.js')
assets.register('js_net_flow', js_net_flow)

js_dest_counts = Bundle(
    'thirdparty/nouislider.min.js',
    'js/map.js',
    'js/destcounts.js',
    output='generated/js_dest_counts.js')
assets.register('js_dest_counts', js_dest_counts)

js_custom = Bundle(
    'thirdparty/nouislider.min.js',
    'js/map.js',
    'js/custom.js',
    output='generated/custom.js')
assets.register('js_custom', js_custom)

css_all = Bundle(
    'scss/map.scss',
    'thirdparty/nouislider.css',
    filters='pyscss',
    output='generated/css_all.css')
assets.register('css_all', css_all)


@app.route('/')
def index():
    return redirect(url_for('net_flow'))

@app.route('/net-flow')
def net_flow():
    return render_template('map.html', mode="NET_FLOW")

@app.route('/dest-count')
def dest_count():
    return render_template('map.html', mode="DEST_COUNT")

@app.route('/top-activity')
def top_activity():
    return redirect(url_for('custom'))

@app.route('/custom')
def custom():
    return render_template('map.html', mode="CUSTOM")


if __name__ == "__main__":
    app.run(debug=True)