Walkability: Predicting and Analyzing Pedestrian Risks on Seattle Sidewalks

The safest route is not always the shortest one, especially for people with mobility challenges. Walkability helps surface hidden accessibility barriers, supporting safer navigation for users and providing insights that can inform more inclusive urban design.
Walkability is a web application that evaluates the accessibility risk of walking routes using real-world hazard data and machine learning. Users can enter a start and end location in Seattle to view a route annotated with known hazards and an overall predicted
severity score. The system uses a FastAPI backend with a JavaScript frontend built on Google Maps. A machine learning model analyzes nearby accessibility hazards using geospatial indexing and gradient boosting to predict route severity, which is visualized in
real time with color-coded routes and interactive markers. From a data analytics level, Walkability integrates accessibility data, public infrastructure datasets, and points of interest such as hospitals and transit access. Through visual components such as
heatmaps, clustered markers, severity grids, and neighborhood risk comparisons, displayed on an interactive map, users can view localized hotspots of accessibility hazards on sidewalks. 

https://walkability.framer.website/
