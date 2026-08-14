import requests


def get_hourly_forecast(lat, lon):
    """Fetch 24-hour forecast data for a specific coordinate."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,"
        "precipitation_probability,"
        "uv_index,"
        "wind_speed_10m"
        "&forecast_days=1"
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

    closest_index = 0
    for i, time_string in enumerate(times):
        try:
            forecast_hour = int(time_string.split("T")[1].split(":")[0])
            if forecast_hour >= target_hour:
                closest_index = i
                break
        except (IndexError, ValueError):
            pass

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


def calculate_risk_score(weather_list):

    if len(weather_list) == 0:
        return 0

    try:
        avg_rain = sum(
            w["rain"] for w in weather_list
        ) / len(weather_list)

        max_uv = max(
            w["uv"] for w in weather_list
        )

        max_wind = max(
            w["wind"] for w in weather_list
        )

        risk = (
            (avg_rain * 0.6)
            + (max_uv * 4)
            + (max_wind * 0.5)
        )

        return min(round(risk), 100)
    except (KeyError, TypeError, ValueError):
        return 50  # Return moderate risk if data is malformed


def generate_route_advice(risk, weather_list):

    advice = []

    if len(weather_list) == 0:
        advice.append("⚠️ Unable to generate advice due to missing weather data.")
        return advice

    try:
        max_rain = max(
            w["rain"] for w in weather_list
        )

        max_uv = max(
            w["uv"] for w in weather_list
        )

        avg_temp = sum(
            w["temperature"] for w in weather_list
        ) / len(weather_list)

        if risk >= 70:
            advice.append(
                "⚠️ High route risk. Be prepared before travelling."
            )

        elif risk >= 40:
            advice.append(
                "🌦 Moderate route risk. Travel carefully."
            )

        else:
            advice.append(
                "✅ Route conditions look safe."
            )

        if max_rain >= 60:
            advice.append(
                "🌧 High rain chance along the route. Carry an umbrella."
            )

        if max_uv >= 7:
            advice.append(
                "☀️ UV is high. Use sunscreen, sunglasses, or a cap."
            )

        if avg_temp >= 30:
            advice.append(
                "👕 Warm weather expected. Wear light breathable clothes."
            )

        elif avg_temp <= 22:
            advice.append(
                "🧥 Cool weather expected. Wear a hoodie or thicker clothes."
            )

    except (KeyError, TypeError, ValueError):
        advice.append("⚠️ Error processing weather data for advice.")

    return advice


def find_best_departure_time(hourly_forecasts_with_coords, current_hour):
    """
    Find the best departure time by evaluating weather risk across candidate hours
    (±3 hours around current_hour, bounded between 0 and 23).
    """
    if len(hourly_forecasts_with_coords) == 0:
        return {"hour": current_hour, "risk": 50}

    # Evaluate candidate departure hours around current_hour
    candidate_hours = range(max(0, current_hour - 3), min(24, current_hour + 4))

    best_hour = current_hour
    lowest_risk = 999.0

    for h in candidate_hours:
        weather_at_h = []
        for item in hourly_forecasts_with_coords:
            # Check if item contains cached 'hourly' forecast object
            if "hourly" in item and item["hourly"]:
                w = extract_weather_at_hour(item["hourly"], item["lat"], item["lon"], h)
            else:
                # If item is already weather point dict without 'hourly', fallback
                w = item
            if w:
                weather_at_h.append(w)

        if weather_at_h:
            risk = calculate_risk_score(weather_at_h)
            if risk < lowest_risk:
                lowest_risk = risk
                best_hour = h

    if lowest_risk == 999.0:
        lowest_risk = 50

    return {"hour": best_hour, "risk": lowest_risk}