let map;
let directionsService;
let directionsRenderer;

let obstacles = [];   // raw obstacle data
let routeMarkers = []; // markers shown on route
let infoWindow;

window.initMap = function () {
  console.log("initMap ran");

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 47.6062, lng: -122.3321 }, // Seattle
    zoom: 13
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({ map });

  infoWindow = new google.maps.InfoWindow();

  loadObstacles();
};

// -------------------- LOAD DATA (NO MARKERS YET)
async function loadObstacles() {
  const res = await fetch("data/obstacles.json");
  const data = await res.json();

  for (const f of data.features) {
    const p = f.properties;

    const lat = p["geometry/coordinates/1"];
    const lng = p["geometry/coordinates/0"];

    if (lat == null || lng == null) continue;

    obstacles.push({
      position: new google.maps.LatLng(lat, lng),
      label: p["properties/label_type"],
      severity: Number(p["properties/severity"])
    });
  }

  console.log("Loaded obstacles:", obstacles.length);
}

// -------------------- USER ROUTE
function calculateRoute() {
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;

  if (!start || !end) return;

  directionsService.route(
    {
      origin: start,
      destination: end,
      travelMode: google.maps.TravelMode.WALKING
    },
    (result, status) => {
      if (status !== "OK") {
        alert("Route failed: " + status);
        return;
      }

      directionsRenderer.setDirections(result);
      analyzeRoute(result.routes[0]);
    }
  );
}

// -------------------- ROUTE ANALYSIS
function analyzeRoute(route) {
  clearRouteMarkers();

  const path = route.overview_path;
  const polyline = new google.maps.Polyline({ path });

  let sum = 0;
  let count = 0;
  let shown = 0;

  for (const obs of obstacles) {
    if (shown >= 2000) break;

    const onRoute = google.maps.geometry.poly.isLocationOnEdge(
      obs.position,
      polyline,
      0.0001 // ~10–15 meters
    );

    if (!onRoute) continue;

    sum += obs.severity;
    count++;
    shown++;

    const marker = new google.maps.Marker({
      position: obs.position,
      map,
      icon: {
        url: getIcon(obs.severity),
        scaledSize: new google.maps.Size(26, 26)
      }
    });

    marker.addListener("click", () => {
      infoWindow.setContent(`
        <strong>Known Hazard</strong><br>
        Type: ${obs.label}<br>
        Severity: ${obs.severity}
      `);
      infoWindow.open(map, marker);
    });

    routeMarkers.push(marker);
  }

  const avg = count ? (sum / count).toFixed(2) : "No data";

  document.getElementById("result").innerText =
    `Hazards on route: ${count} | Average severity: ${avg}`;
}

// -------------------- HELPERS
function clearRouteMarkers() {
  for (const m of routeMarkers) m.setMap(null);
  routeMarkers = [];
}

function getIcon(severity) {
  const color =
    severity >= 4 ? "red" :
    severity === 3 ? "orange" :
    "yellow";

  return `https://maps.google.com/mapfiles/ms/icons/${color}-dot.png`;
}