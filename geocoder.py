import requests

def get_coordinates(place, country):

    query = f"{place}, {country}"

    url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={query}&count=1"
    )

    data = requests.get(url).json()

    if "results" not in data:
        return None

    return {
        "lat": data["results"][0]["latitude"],
        "lon": data["results"][0]["longitude"]
    }