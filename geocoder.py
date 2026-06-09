import requests

COUNTRY_CODES = {
    "Sri Lanka": "lk",
    "India": "in",
    "Australia": "au",
    "United Kingdom": "gb",
    "United States": "us"
}

def get_coordinates(place, country):
    country_code = COUNTRY_CODES.get(country, "")

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{place}, {country}",
        "format": "json",
        "limit": 1,
        "countrycodes": country_code
    }

    headers = {
        "User-Agent": "RouteCastAI/1.0"
    }

    response = requests.get(url, params=params, headers=headers)

    data = response.json()

    if len(data) == 0:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
        "display_name": data[0]["display_name"]
    }