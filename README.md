# NYC Moves
### Analyzing and Predicting short-term movement between NYC neighborhoods
### Fall 2016 Independent Work (IW03)

##### Data Cleaning

- Using trip records from Jan 2016 through June 2016, available to download from the [NYC Transportation and Limousine Commission (TLC) website](http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml).
- **process_data.py:** Several small functions run via the command line to clean and modify data.
- **get_zones.py:** For each trip record, indicate the TLC zone of the pickup and drop-off locations.

##### Exploration

- **Data exploration.ipynb:** exploratory notebook on the taxi trip records; implementations of most of the *Exploration* section of my paper are here.
- **get_dest\_counts.py:** Build a csv file where for each hour, day of week, and pickup zone, counts the drop-offs in each drop-off zone. Output used in app.
- **get_flow.py:** Build a csv file where for each hour and day of week, counts the net taxi trips (drop-offs - pickups) in each zone. Output used in app.


##### Prediction

- **Regression.ipynb:** Using Random forests and SGD regression to predict a trip's drop-off location given its pickup datetime and location; primarily for playing around with scikit-learn.
- **grid_search.py:** Grid search and cross-validation functions for random forests and SGD; implementation of results in the *Prediction* section of my paper are here.

##### Other

- **globes.py:** Useful variable declarations and function definitions used in other files.
- **Network Analysis.ipynb:** Turn taxi trips into edges and neighborhoods into nodes; not used in paper.
- **zones_\*.geojson:** GeoJSON zone definitions.


##### Dependencies
Install the python dependencies with `pip install -r requirements.txt`. The shapely package requires the GEOS library, which can be installed via brew, apt-get, yum, or the [official website](https://trac.osgeo.org/geos/).

