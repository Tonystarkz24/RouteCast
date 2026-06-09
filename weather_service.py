import requests


def get_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        "&hourly=precipitation_probability,uv_index"
        "&forecast_days=1"
    )

    data = requests.get(url).json()

    if "current" not in data:
        return None

    temp = data["current"]["temperature_2m"]
    humidity = data["current"]["relative_humidity_2m"]
    wind = data["current"]["wind_speed_10m"]

    rain = max(data["hourly"]["precipitation_probability"])
    uv = max(data["hourly"]["uv_index"])

    return {
        "temperature": temp,
        "humidity": humidity,
        "wind": wind,
        "rain": rain,
        "uv": uv
    }


def calculate_risk_score(weather_list):
    if len(weather_list) == 0:
        return 0

    avg_rain = sum(w["rain"] for w in weather_list) / len(weather_list)
    max_uv = max(w["uv"] for w in weather_list)
    max_wind = max(w["wind"] for w in weather_list)

    risk = (avg_rain * 0.6) + (max_uv * 4) + (max_wind * 0.5)

    return min(round(risk), 100)


def generate_route_advice(risk, weather_list):
    advice = []

    max_rain = max(w["rain"] for w in weather_list)
    max_uv = max(w["uv"] for w in weather_list)
    avg_temp = sum(w["temperature"] for w in weather_list) / len(weather_list)

    if risk >= 70:
        advice.append("⚠️ High route risk. Be prepared before travelling.")
    elif risk >= 40:
        advice.append("🌦 Moderate route risk. Travel carefully.")
    else:
        advice.append("✅ Route conditions look safe.")

    if max_rain >= 60:
        advice.append("🌧 High rain chance along the route. Carry an umbrella or raincoat.")

    if max_uv >= 7:
        advice.append("☀️ UV level is high. Use sunscreen, sunglasses, or a cap.")

    if avg_temp >= 30:
        advice.append("👕 Weather is warm. Wear light-colored breathable clothes.")
    elif avg_temp <= 22:
        advice.append("🧥 Weather is cool. Wear thicker clothes or a hoodie.")

    return advice