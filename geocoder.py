import requests
from urllib.parse import quote

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
        "User-Agent": "RouteCastAI/1.0 (contact@routecast.ai)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display_name": data[0]["display_name"]
                }
    except Exception:
        pass

    # Fallback to Open-Meteo Geocoding API if Nominatim times out or fails
    try:
        encoded_place = quote(place.strip())
        fallback_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_place}&count=1"
        res = requests.get(fallback_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "results" in data and len(data["results"]) > 0:
                item = data["results"][0]
                country_name = item.get("country", country)
                return {
                    "lat": float(item["latitude"]),
                    "lon": float(item["longitude"]),
                    "display_name": f"{item['name']}, {country_name}"
                }
    except Exception:
        pass

    return None