import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

DATA_PATH = "src/Datathon/Access_to_Everyday_Life_Dataset.csv"
EARTH_RADIUS = 6_371_000  # meters
RADII_METERS = [10, 25, 50]   # distances to consider around each point
DECAY_METERS = 20.0 

csv_path = os.path.join(os.path.dirname(__file__), "Datathon", "Access_to_Everyday_Life_Dataset.csv")
df = pd.read_csv(csv_path)
df = df.dropna(subset=["properties/severity"])
df["severity_norm"] = df["properties/severity"] / 5.0


coords = df[["geometry/coordinates/1", "geometry/coordinates/0"]].values
coords_rad = np.deg2rad(coords)
tree = BallTree(coords_rad, metric="haversine")




MAX_RADIUS_RAD = max(RADII_METERS) / EARTH_RADIUS


def _true_local_risk(i: int) -> float:
   point = coords_rad[i]
   idx = tree.query_radius([point], r=MAX_RADIUS_RAD)[0]
   idx = idx[idx != i]  # exclude self


   if len(idx) == 0:
       return 0.0


   dists = np.linalg.norm(coords_rad[idx] - point, axis=1) * EARTH_RADIUS
   weights = np.exp(-dists / DECAY_METERS)
   severities = df.iloc[idx]["severity_norm"].values
   return float(np.sum(severities * weights))


df["true_local_risk"] = [_true_local_risk(i) for i in range(len(df))]


def _build_features(point_rad):
   features = []
   for r in RADII_METERS:
       idx = tree.query_radius([point_rad], r=r / EARTH_RADIUS)[0]
       if len(idx) == 0:
           features.extend([0, 0.0, 0.0])
       else:
           sev = df.iloc[idx]["severity_norm"].values
           features.extend([len(idx), float(sev.mean()), float(sev.max())])
   return features


X = np.array([_build_features(coords_rad[i]) for i in range(len(df))])
y = df["true_local_risk"].values


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(
   X_scaled, y, test_size=0.2, random_state=42
)


model = GradientBoostingRegressor(
   n_estimators=400,
   learning_rate=0.05,
   max_depth=4,
   subsample=0.8,
   random_state=42
)


model.fit(X_train, y_train)


def predict_local_risk(lat: float, lon: float) -> float:
   point_rad = np.deg2rad([[lat, lon]])[0]
   features = _build_features(point_rad)
   features_scaled = scaler.transform([features])
   return float(model.predict(features_scaled)[0])


def predict_route_severity_risk(route_coords: list[list[float]]) -> float:


   if not route_coords:
       return 0.0
   risks = [predict_local_risk(lat, lon) for lat, lon in route_coords]
   return float(np.mean(risks))


