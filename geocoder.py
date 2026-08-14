import requests
from urllib.parse import quote

COUNTRY_CODES = {
    "Sri Lanka": "lk",
    "India": "in",
    "Australia": "au",
    "United Kingdom": "gb",
    "United States": "us"
}


def search_locations(place, country, limit=5):
    """Search for multiple candidate locations to prevent geocoding ambiguity."""
    country_code = COUNTRY_CODES.get(country, "")
    candidates = []

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{place}, {country}",
        "format": "json",
        "limit": limit,
        "countrycodes": country_code
    }
    headers = {
        "User-Agent": "RouteCastAI/1.0 (contact@routecast.ai)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                for item in data:
                    candidates.append({
                        "lat": float(item["lat"]),
                        "lon": float(item["lon"]),
                        "display_name": item["display_name"]
                    })
                return candidates
    except Exception:
        pass

    # Fallback to Open-Meteo Geocoding API
    try:
        encoded_place = quote(place.strip())
        fallback_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_place}&count={limit}"
        res = requests.get(fallback_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "results" in data and len(data["results"]) > 0:
                for item in data["results"]:
                    country_name = item.get("country", country)
                    candidates.append({
                        "lat": float(item["latitude"]),
                        "lon": float(item["longitude"]),
                        "display_name": f"{item['name']}, {country_name}"
                    })
                return candidates
    except Exception:
        pass

    return candidates


def get_coordinates(place, country):
    """Get the primary coordinates for a location string."""
    results = search_locations(place, country, limit=5)
    if results:
        return results[0]
    return None
