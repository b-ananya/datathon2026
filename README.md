# Walkability: Predicting and Analyzing Pedestrian Risks on Seattle Sidewalks

The safest route is not always the shortest one, especially for people with mobility challenges. **Walkability** helps surface hidden accessibility barriers, supporting safer navigation for users and providing insights that can inform more inclusive urban design.
Walkability is a web application that evaluates the accessibility risk of walking routes using real-world hazard data and machine learning. A machine learning model analyzes nearby accessibility hazards using geospatial indexing and gradient boosting to predict route severity.

From a data analytics level, Walkability integrates accessibility data, public infrastructure datasets, and points of interest such as hospitals and transit access. Through visual components such as
heatmaps, clustered markers, severity grids, and neighborhood risk comparisons, displayed on an interactive map, users can view localized hotspots of accessibility hazards on sidewalks. 

https://walkability.framer.website/

## Features

- Interactive Google Maps walking routes  
- Real accessibility hazard visualization  
- Machine learning–based route severity prediction  
- Color-coded routes based on predicted risk  
- Secure backend API for predictions and API key handling  


## Requirements

- Python 3.9+
- Google Maps API key  
  - Maps JavaScript API enabled  
  - Directions API enabled  

---

## Setup Instructions

## 1. Clone the Repository
- bash
- git clone
- cd seattle-sidewalks

  
## 2. Create and Activate a Virtual Environment
- Windows (PowerShell):
  - python -m venv venv
  - venv\Scripts\activate

- macOS / Linux:
  - python3 -m venv venv
  - source venv/bin/activate


## 3. Install Python Dependencies
- pip install fastapi uvicorn python-dotenv pandas numpy scikit-learn


## 4. Set Up Environment Variables
- Create a .env file in the project root:
- GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

- Make sure your Google Cloud project has:
 - Maps JavaScript API enabled
 - Directions API enabled

## 5. Running the Application

1. Start the Backend Server
From the project root:
uvicorn backend.app:app --reload

2. Open the App in Your Browser
