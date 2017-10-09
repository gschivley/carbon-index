# Location data
The .csv file in this folder contains the following information:

- plant id
- state (2-letter abbreviation)
- lat/lon
- nerc region

## Method
Plant IDs, state, and lat/lon data are taken from EIA's bulk download data. They represent all facilities operating from 2001 through mid-2017. Facilities are placed in NERC regions using a spatial join with EIA's NERC shapefile (https://www.eia.gov/maps/layer_info-m.php).

Spatial joins are performed using QGIS. Original attempts to perform the spatial joins using GeoPandas assigned 36 facilities to multiple NERC regions. It isn't clear how or why this happened. A visual inspection showed that at least some of the plants are close to the border between NERC regions.