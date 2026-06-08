from route_manager import save_route, load_routes
import streamlit as st
import requests

st.title("🌦 RouteCast AI")
st.write("AI-powered weather, outfit, and travel assistant")

city = st.text_input("Enter Destination City")

def get_advice(temp, rain, uv, wind):
    advice = []

    if rain >= 60:
        advice.append("🌧 High rain chance. Carry an umbrella or raincoat.")
    elif rain >= 30:
        advice.append("🌦 Medium rain chance. Better to carry a small umbrella.")
    else:
        advice.append("☀ Rain chance is low. Umbrella is optional.")

    if temp < 22:
        advice.append("🧥 Weather is cool. Wear a hoodie or thick clothes.")
    elif temp > 30:
        advice.append("👕 Weather is warm. Wear light-colored cotton clothes.")
    else:
        advice.append("👌 Normal comfortable clothes are fine.")

    if uv >= 7:
        advice.append("☀ UV is high. Use sunscreen, sunglasses, or a cap.")
    elif uv >= 4:
        advice.append("🌤 UV is moderate. Try to avoid long direct sunlight.")
    else:
        advice.append("✅ UV level is safe.")

    if wind >= 30:
        advice.append("💨 Wind is strong. Be careful with umbrellas.")

    return advice

st.header("📍 Save Daily Route")

route_name = st.text_input("Route Name")

destination = st.text_input("Destination City")

travel_time = st.time_input("Travel Time")

if st.button("Save Route"):

    route = {
        "name": route_name,
        "destination": destination,
        "time": str(travel_time)
    }

    save_route(route)

    st.success("Route Saved!")
if st.button("Get AI Weather Advice"):

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_data = requests.get(geo_url).json()

    if "results" in geo_data:
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,wind_speed_10m"
            f"&hourly=precipitation_probability,uv_index"
            f"&forecast_days=1"
        )
    
        weather_data = requests.get(weather_url).json()

        temp = weather_data["current"]["temperature_2m"]
        wind = weather_data["current"]["wind_speed_10m"]

        rain = max(weather_data["hourly"]["precipitation_probability"])
        uv = max(weather_data["hourly"]["uv_index"])

        st.subheader(f"Weather for {city}")

        st.metric("Temperature", f"{temp} °C")
        st.metric("Rain Chance", f"{rain}%")
        st.metric("UV Index", round(uv, 1))
        st.metric("Wind Speed", f"{wind} km/h")

        st.subheader("🤖 AI Advice")

        advice_list = get_advice(temp, rain, uv, wind)

        for advice in advice_list:
            st.write(advice)

    else:
        st.error("City not found. Try another city.")

        st.header("📋 Saved Routes")

routes = load_routes()

for route in routes:
    st.write(
        f"**{route['name']}** → {route['destination']} at {route['time']}"
    )