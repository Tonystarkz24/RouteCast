from route_manager import load_selected_route

import streamlit as st
import requests
import folium

from streamlit_folium import st_folium

st.title("🗺 Route Details")

route = load_selected_route()

if route is None:
    st.warning("No route selected.")
    st.stop()

country = route["country"]

st.subheader(route["name"])

st.write(f"🌍 Country: {country}")
st.write(f"📍 Start: {route['start']}")
st.write(f"🎯 Destination: {route['destination']}")
st.write(f"🕒 Time: {route['time']}")

# Improved geocoding
start_search = f"{route['start']}, {country}"
dest_search = f"{route['destination']}, {country}"

start_url = f"https://geocoding-api.open-meteo.com/v1/search?name={start_search}&count=1"
dest_url = f"https://geocoding-api.open-meteo.com/v1/search?name={dest_search}&count=1"

start_data = requests.get(start_url).json()
dest_data = requests.get(dest_url).json()

if "results" not in start_data:
    st.error(f"Could not find {start_search}")
    st.stop()

if "results" not in dest_data:
    st.error(f"Could not find {dest_search}")
    st.stop()

start_lat = start_data["results"][0]["latitude"]
start_lon = start_data["results"][0]["longitude"]

dest_lat = dest_data["results"][0]["latitude"]
dest_lon = dest_data["results"][0]["longitude"]

# Show what locations were found
st.success(
    f"Found: {start_data['results'][0]['name']} ➜ {dest_data['results'][0]['name']}"
)

# Center map
center_lat = (start_lat + dest_lat) / 2
center_lon = (start_lon + dest_lon) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=10
)

# Start marker
folium.Marker(
    [start_lat, start_lon],
    popup=f"Start: {route['start']}",
    tooltip="Start"
).add_to(m)

# Destination marker
folium.Marker(
    [dest_lat, dest_lon],
    popup=f"Destination: {route['destination']}",
    tooltip="Destination"
).add_to(m)

# Straight line route
folium.PolyLine(
    [
        [start_lat, start_lon],
        [dest_lat, dest_lon]
    ],
    weight=5
).add_to(m)

st_folium(
    m,
    width=1000,
    height=550
)