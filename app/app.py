from flask import Flask, render_template
from flask_assets import Environment, Bundle

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)