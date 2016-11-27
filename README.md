### NYC Moves

Neighborhood geoJSON file from https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas/cpf4-rkhq/data.

converted with ogr2ogr (ogr2ogr -f GeoJSON -t_srs crs:84 [name].geojson [name].shp)
    http://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/
taxi_zones ffrom todd schneider github
zip codes from https://data.cityofnewyork.us/Business/Zip-Code-Boundaries/i8iw-xf4u

export LD_LIBRARY_PATH=/path_to/geos/lib:$LD_LIBRARY_PATH

strip prefix: for f in *.csv; do mv "$f" "${f#zones_}"; done

###### TODO
- add number of passengers to calculations
- slider for times
- tooltip on hover over each neighborhood
- track total # ppl in transit (and thus not on the map)

##### Dependencies
Install the python dependencies with `pip install -r requirements.txt`. The shapely package requires the GEOS library, which can be installed via brew, apt-get, yum, or the [official website](https://trac.osgeo.org/geos/).
