import requests
from config import ORS_API_KEY

def get_route(start_lon, start_lat, end_lon, end_lat):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

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

    response = requests.post(
        url,
        json=body,
        headers=headers
    )

    return response.json()