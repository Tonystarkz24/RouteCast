import streamlit as st
import requests

st.title("🌦 RouteCast AI")

city = st.text_input("Enter City")

if st.button("Check Weather"):

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

    geo_response = requests.get(url).json()

    if "results" in geo_response:

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,wind_speed_10m"
        )

        weather = requests.get(weather_url).json()

        temp = weather["current"]["temperature_2m"]
        wind = weather["current"]["wind_speed_10m"]

        st.success(f"Temperature: {temp}°C")
        st.info(f"Wind Speed: {wind} km/h")

    else:
        st.error("City not found")