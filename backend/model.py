import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.neighbors import BallTree
import os

csv_path = os.path.join(os.path.dirname(__file__), "Datathon", "Access_to_Everyday_Life_Dataset.csv")
df = pd.read_csv(csv_path)

df = df.dropna(subset=['properties/severity'])
df['severity_norm'] = df['properties/severity'] / df['properties/severity'].max()
coords_rad = np.deg2rad(df[['geometry/coordinates/1', 'geometry/coordinates/0']].values)

tree = BallTree(coords_rad, metric='haversine')
radius_rad = 20 / 6371000

counts, avg_severity = [], []
for coord in coords_rad:
    idx = tree.query_radius([coord], r=radius_rad)[0]
    counts.append(len(idx))
    avg_severity.append(df.iloc[idx]['severity_norm'].mean() if len(idx) > 0 else 0.0)

features_df = pd.DataFrame({'nearby_count': counts, 'nearby_avg_severity': avg_severity})
X = features_df
y = df['severity_norm']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    random_state=42
)
model.fit(X_train, y_train)

def predict_route_severity_risk(route_coords):
    route_coords_rad = np.deg2rad(np.array(route_coords))
    nearby_counts, nearby_avg_sev = [], []

    for coord in route_coords_rad:
        idx = tree.query_radius([coord], r=radius_rad)[0]
        nearby_counts.append(len(idx))
        nearby_avg_sev.append(df.iloc[idx]['severity_norm'].mean() if len(idx) > 0 else 0.0)

    route_features = pd.DataFrame({
        'nearby_count': nearby_counts,
        'nearby_avg_severity': nearby_avg_sev
    })
    return model.predict(route_features).mean()