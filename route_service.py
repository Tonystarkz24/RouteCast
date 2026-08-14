import requests
from config import ORS_API_KEY


def get_osrm_fallback_route(start_lon, start_lat, end_lon, end_lat):
    """Fallback router using free OSRM API if OpenRouteService times out or fails."""
    try:
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&alternatives=true"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "routes" in data and data["routes"]:
                parsed_routes = []
                for r in data["routes"]:
                    coords = [[c[1], c[0]] for c in r["geometry"]["coordinates"]]
                    parsed_routes.append({
                        "summary": {
                            "distance": r["distance"],
                            "duration": r["duration"]
                        },
                        "points": coords
                    })
                return {"routes": parsed_routes, "source": "OSRM"}
    except Exception:
        pass
    return None


def get_route(start_lon, start_lat, end_lon, end_lat, profile="driving-car"):

    valid_profiles = ["driving-car", "cycling-regular", "foot-walking"]
    if profile not in valid_profiles:
        profile = "driving-car"

    url = f"https://api.openrouteservice.org/v2/directions/{profile}"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start_lon, start_lat],
            [end_lon, end_lat]
        ],
        "alternative_routes": {
            "target_count": 3,
            "weight_factor": 1.4,
            "share_factor": 0.6
        },
        "instructions": False,
        "geometry": True,
        "elevation": False,
        "extra_info": [],
        "attributes": [],
        "geometry_simplify": False
    }

    try:
        response = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=25
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Fallback to OSRM if OpenRouteService times out or errors
    fallback_res = get_osrm_fallback_route(start_lon, start_lat, end_lon, end_lat)
    if fallback_res:
        return fallback_res

    return {"error": "Routing services are currently busy or unavailable. Please try again in a moment."}

