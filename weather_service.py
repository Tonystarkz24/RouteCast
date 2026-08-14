import requests


def get_hourly_forecast(lat, lon):
    """Fetch 48-hour forecast data for a specific coordinate to support overnight routes."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,"
        "precipitation_probability,"
        "uv_index,"
        "wind_speed_10m"
        "&forecast_days=2"
    )

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        if data and "hourly" in data:
            return data["hourly"]
    except Exception:
        pass
    return None


def extract_weather_at_hour(hourly_data, lat, lon, target_hour):
    """Extract weather metrics at a specific hour from hourly dataset."""
    if not hourly_data or "time" not in hourly_data:
        return None

    times = hourly_data.get("time", [])
    if not times:
        return None

    closest_index = min(max(0, target_hour), len(times) - 1)

    try:
        return {
            "lat": lat,
            "lon": lon,
            "temperature": hourly_data["temperature_2m"][closest_index],
            "rain": hourly_data["precipitation_probability"][closest_index],
            "uv": hourly_data["uv_index"][closest_index],
            "wind": hourly_data["wind_speed_10m"][closest_index],
            "hourly": hourly_data,
        }
    except (IndexError, KeyError):
        return None



def get_weather(lat, lon, journey_time):
    """Get weather forecast at specific lat, lon, and journey_time string."""
    hourly_data = get_hourly_forecast(lat, lon)
    if not hourly_data:
        return None

    try:
        target_hour = int(str(journey_time).split(":")[0])
    except (ValueError, AttributeError, IndexError):
        target_hour = 12

    return extract_weather_at_hour(hourly_data, lat, lon, target_hour)


def calculate_risk_score(weather_list, transport_mode="🚗 Car / Vehicle"):
    """Calculate vehicle-aware risk score based on mode profile."""
    if len(weather_list) == 0:
        return 0

    mode_str = str(transport_mode).lower()

    if "bike" in mode_str or "motorcycle" in mode_str or "scooter" in mode_str:
        rain_weight, uv_weight, wind_weight = 1.1, 4.5, 1.0
    elif "walk" in mode_str or "pedestrian" in mode_str:
        rain_weight, uv_weight, wind_weight = 1.0, 4.0, 0.6
    elif "bus" in mode_str or "transit" in mode_str:
        rain_weight, uv_weight, wind_weight = 0.7, 3.0, 0.4
    else:  # Car / Vehicle default
        rain_weight, uv_weight, wind_weight = 0.5, 2.0, 0.3

    try:
        avg_rain = sum(w["rain"] for w in weather_list) / len(weather_list)
        max_uv = max(w["uv"] for w in weather_list)
        max_wind = max(w["wind"] for w in weather_list)

        risk = (avg_rain * rain_weight) + (max_uv * uv_weight) + (max_wind * wind_weight)
        return min(round(risk), 100)
    except (KeyError, TypeError, ValueError):
        return 50


def generate_route_advice(risk, weather_list, transport_mode="🚗 Car / Vehicle"):
    """Generate human-like vehicle-tailored weather advice."""
    advice = []

    if len(weather_list) == 0:
        advice.append("⚠️ Unable to generate advice due to missing weather data.")
        return advice

    mode_str = str(transport_mode).lower()
    is_two_wheeler = "bike" in mode_str or "motorcycle" in mode_str or "scooter" in mode_str
    is_pedestrian = "walk" in mode_str or "bus" in mode_str

    try:
        max_rain = max(w["rain"] for w in weather_list)
        max_uv = max(w["uv"] for w in weather_list)
        avg_temp = sum(w["temperature"] for w in weather_list) / len(weather_list)
        max_wind = max(w["wind"] for w in weather_list)

        if risk >= 70:
            advice.append("⚠️ High route risk! Prepare protective gear or delay travel if possible.")
        elif risk >= 40:
            advice.append("🌦 Moderate route risk. Exercise caution along the route.")
        else:
            advice.append("✅ Route conditions look safe for your trip.")

        if max_rain >= 50:
            if is_two_wheeler:
                advice.append("🌧 High rain chance! Wear a waterproof suit/raincoat and check tire grip.")
            elif is_pedestrian:
                advice.append("🌧 High rain chance! Carry a sturdy umbrella and wear waterproof shoes.")
            else:
                advice.append("🌧 High rain chance along route. Check wipers and keep safe braking distance.")

        if max_uv >= 6:
            if is_two_wheeler or is_pedestrian:
                advice.append("☀️ High UV Index! Apply SPF 50+ sunscreen and wear anti-UV sleeves/sunglasses.")
            else:
                advice.append("☀️ Bright sunlight expected. Use sunglasses and AC.")

        if max_wind >= 28:
            if is_two_wheeler:
                advice.append("💨 Strong crosswinds detected! Ride at moderate speed and hold handlebars firmly.")

        if avg_temp >= 30:
            advice.append("👕 Warm weather expected. Carry water to stay hydrated.")
        elif avg_temp <= 21:
            advice.append("🧥 Cool temperatures along route. Wear warm layer/jacket.")

    except (KeyError, TypeError, ValueError):
        advice.append("⚠️ Error processing weather data for advice.")

    return advice


def find_best_departure_time(hourly_forecasts_with_coords, current_hour, transport_mode="🚗 Car / Vehicle"):
    """
    Find the best departure time by evaluating vehicle-aware weather risk across candidate hours.
    """
    if len(hourly_forecasts_with_coords) == 0:
        return {"hour": current_hour, "risk": 50}

    candidate_hours = range(max(0, current_hour - 3), min(24, current_hour + 4))

    best_hour = current_hour
    lowest_risk = 999.0

    for h in candidate_hours:
        weather_at_h = []
        for item in hourly_forecasts_with_coords:
            if "hourly" in item and item["hourly"]:
                w = extract_weather_at_hour(item["hourly"], item["lat"], item["lon"], h)
            else:
                w = item
            if w:
                weather_at_h.append(w)

        if weather_at_h:
            risk = calculate_risk_score(weather_at_h, transport_mode)
            if risk < lowest_risk:
                lowest_risk = risk
                best_hour = h

    if lowest_risk == 999.0:
        lowest_risk = 50

    return {"hour": best_hour, "risk": lowest_risk}
