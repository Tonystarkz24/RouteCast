import requests
from config import ORS_API_KEY


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
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Network or timeout error: {str(e)}"}