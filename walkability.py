import pandas as pd # type: ignore
import numpy as np # type: ignore
from sklearn.ensemble import GradientBoostingRegressor # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score # type: ignore
from sklearn.neighbors import BallTree # type: ignore

# - `type` – GeoJSON feature type
# - `geometry/type` – Geometry format (Point)
# - `geometry/coordinates/0` – Longitude
# - `geometry/coordinates/1` – Latitude
# - `properties/attribute_id` – Unique identifier for each accessibility observation
# - `properties/label_type` – Type of accessibility issue (e.g., SurfaceProblem, Obstacle, CurbRamp)
# - `properties/neighborhood` – Neighborhood name
# - `properties/severity` – Severity rating of the accessibility issue
# - `properties/is_temporary` – Whether the issue is temporary or permanent


# Model Goal: Input 

df = pd.read_csv("src/Datathon/Access_to_Everyday_Life_Dataset.csv") 
df = df.dropna(subset=['properties/severity'])  # drop all rows with blank severity

df['severity_norm'] = df['properties/severity'] / df['properties/severity'].max()  # normalize severities to 0-1 score (dividing by max severity (5))

coords_rad = np.deg2rad(df[['geometry/coordinates/1', 'geometry/coordinates/0']].values)    # create 2D array of lat, lon coordinates in radians


# use BallTree to find all hazards within a 20 meter radius of a coordinate
tree = BallTree(coords_rad, metric='haversine')
radius_rad = 20 / 6371000


# for every coordinate, count how many hazards are nearby (20m radius)
# for every coordinate, calculate average severity of the nearby hazards
counts = []
avg_severity = []
for coord in coords_rad:
    idx = tree.query_radius([coord], r=radius_rad)[0] 
    counts.append(len(idx))
    if len(idx) > 0:
        avg_severity.append(df.iloc[idx]['severity_norm'].mean())
    else:
        avg_severity.append(0.0)


# combine counts and average severity into a dataframe of features
features_df = pd.DataFrame({
    'nearby_count': counts,
    'nearby_avg_severity': avg_severity
})

# Given whats happening around a location, how risky is that location
X = features_df     # features (inputs: nearby hazard counts (20m), average severities of nearby hazards)
                    # One row: At this location, there are N nearby hazards with an average severity of S
y = df['severity_norm']    # target, what model is trying to predict. The correct output for each row of X


# Split into training set and testing set
# 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize the Gradient Boosting Regressor
model = GradientBoostingRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    random_state=42
)
model.fit(X_train, y_train)     # train model based on training data


# Predict a route severity risk based on list of coordinates on a route
def predict_route_severity_risk(route_coords):
    route_coords_rad = np.deg2rad(np.array(route_coords))
    nearby_counts = []
    nearby_avg_sev = []

    for coord in route_coords_rad:
        idx = tree.query_radius([coord], r=radius_rad)[0]
        nearby_counts.append(len(idx))
        if len(idx) > 0:
            nearby_avg_sev.append(df.iloc[idx]['severity_norm'].mean())
        else:
            nearby_avg_sev.append(0.0)

    route_features = pd.DataFrame({
        'nearby_count': nearby_counts,
        'nearby_avg_severity': nearby_avg_sev
    })

    return model.predict(route_features).mean()