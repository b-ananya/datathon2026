let map;
let directionsService;
let directionsRenderer;
let infoWindow;
let obstacles = [];
let routeMarkers = [];
let routePolyline;

// -------------------- INIT MAP --------------------
async function init() {
    const res = await fetch("/maps-api-key");
    const data = await res.json();
    const key = data.key;

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&callback=initMap&libraries=geometry`;
    script.async = true;
    document.head.appendChild(script);
}

window.initMap = function () {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 47.6062, lng: -122.3321 },
        zoom: 13
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({ map });
    infoWindow = new google.maps.InfoWindow();

    loadObstacles();
};

// -------------------- LOAD HAZARDS --------------------
async function loadObstacles() {
    const res = await fetch("/data/obstacles.json");
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

// -------------------- CALCULATE ROUTE --------------------
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

// -------------------- SAMPLE ROUTE --------------------
function sampleRoute(route) {
    const path = route.overview_path;
    const sampled = [];
    let lastPoint = path[0];
    sampled.push([lastPoint.lat(), lastPoint.lng()]);
    let distAccum = 0;

    for (let i = 1; i < path.length; i++) {
        const current = path[i];
        distAccum += google.maps.geometry.spherical.computeDistanceBetween(lastPoint, current);
        if (distAccum >= 30) {
            sampled.push([current.lat(), current.lng()]);
            distAccum = 0;
            lastPoint = current;
        }
    }
    return sampled;
}

// -------------------- FETCH ROUTE SEVERITY --------------------
async function getRouteSeverity(points) {
    const res = await fetch("/predict-route-severity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points })
    });
    const data = await res.json();
    return data.severity;
}

// -------------------- ANALYZE ROUTE --------------------
async function analyzeRoute(route) {
    clearRouteMarkers();
    const sampledPoints = sampleRoute(route);
    const severity = await getRouteSeverity(sampledPoints);

    const color = severity * 5 >= 4 ? "red" :
                  severity * 5 >= 3 ? "orange" :
                  "yellow";

    if (routePolyline) routePolyline.setMap(null);

    routePolyline = new google.maps.Polyline({
        path: route.overview_path,
        strokeColor: color,
        strokeOpacity: 0.8,
        strokeWeight: 6,
        map: map
    });

    let sum = 0, count = 0, shown = 0;
    for (const obs of obstacles) {
        if (shown >= 2000) break;
        const onRoute = google.maps.geometry.poly.isLocationOnEdge(obs.position, routePolyline, 0.0001);
        if (!onRoute) continue;

        sum += obs.severity;
        count++;
        shown++;

        const marker = new google.maps.Marker({
            position: obs.position,
            map,
            icon: { url: getIcon(obs.severity), scaledSize: new google.maps.Size(26, 26) }
        });

        marker.addListener("click", () => {
            infoWindow.setContent(`<strong>Known Hazard</strong><br>Type: ${obs.label}<br>Severity: ${obs.severity}`);
            infoWindow.open(map, marker);
        });

        routeMarkers.push(marker);
    }

    const avg = count ? (sum / count).toFixed(2) : "No data";
    document.getElementById("result").innerText =
        `Hazards on route: ${count} | Average severity: ${avg} | Predicted severity: ${(severity*5).toFixed(2)}`;
}

// -------------------- HELPERS --------------------
function clearRouteMarkers() {
    for (const m of routeMarkers) m.setMap(null);
    routeMarkers = [];
}

function getIcon(severity) {
    const color = severity >= 4 ? "red" :
                  severity === 3 ? "orange" :
                  "yellow";
    return `https://maps.google.com/mapfiles/ms/icons/${color}-dot.png`;
}

// -------------------- START --------------------
init();