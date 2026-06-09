from route_manager import load_selected_route
from route_service import get_route
from weather_service import get_weather, calculate_risk_score, generate_route_advice

import streamlit as st
import folium
import openrouteservice.convert

from streamlit_folium import st_folium

st.title("🗺 Route Details")

route = load_selected_route()

if route is None:
    st.warning("No route selected.")
    st.stop()

start_lat = route["start_lat"]
start_lon = route["start_lon"]
dest_lat = route["dest_lat"]
dest_lon = route["dest_lon"]

st.subheader(f"🛣 {route['name']}")

st.write(f"📍 Start: {route['start']}")
st.write(f"🎯 Destination: {route['destination']}")
st.write(f"🌍 Country: {route['country']}")
st.write(f"🕒 Planned Time: {route['time']}")

with st.spinner("Calculating real road route..."):
    route_data = get_route(start_lon, start_lat, dest_lon, dest_lat)

if "routes" not in route_data:
    st.error("Routing failed")
    st.json(route_data)
    st.stop()

route_info = route_data["routes"][0]

distance_km = round(route_info["summary"]["distance"] / 1000, 2)
duration_min = round(route_info["summary"]["duration"] / 60)

col1, col2 = st.columns(2)

with col1:
    st.metric("📏 Distance", f"{distance_km} km")

with col2:
    st.metric("🚗 Estimated Travel", f"{duration_min} min")

encoded_geometry = route_info["geometry"]

decoded = openrouteservice.convert.decode_polyline(encoded_geometry)

route_points = []

for coord in decoded["coordinates"]:
    lon = coord[0]
    lat = coord[1]
    route_points.append([lat, lon])

# Sample weather points along the route
sample_count = 5
step = max(1, len(route_points) // sample_count)

sample_points = route_points[::step][:sample_count]

weather_results = []

with st.spinner("Analyzing weather along route..."):
    for point in sample_points:
        lat = point[0]
        lon = point[1]

        weather = get_weather(lat, lon)

        if weather is not None:
            weather["lat"] = lat
            weather["lon"] = lon
            weather_results.append(weather)

if len(weather_results) == 0:
    st.warning("Could not fetch weather along route.")
    st.stop()

risk_score = calculate_risk_score(weather_results)
advice_list = generate_route_advice(risk_score, weather_results)

st.divider()

st.subheader("⚠️ Route Risk Analysis")

st.metric("Route Risk Score", f"{risk_score}/100")

st.subheader("🤖 AI Route Advice")

for advice in advice_list:
    st.write(advice)

# Map
center_lat = (start_lat + dest_lat) / 2
center_lon = (start_lon + dest_lon) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11
)

folium.Marker(
    [start_lat, start_lon],
    popup=f"Start: {route['start']}",
    tooltip="Start",
    icon=folium.Icon(color="green")
).add_to(m)

folium.Marker(
    [dest_lat, dest_lon],
    popup=f"Destination: {route['destination']}",
    tooltip="Destination",
    icon=folium.Icon(color="red")
).add_to(m)

folium.PolyLine(
    route_points,
    weight=6,
    color="blue",
    opacity=0.8
).add_to(m)

# Weather markers
for index, weather in enumerate(weather_results, start=1):
    rain = weather["rain"]

    if rain >= 60:
        marker_color = "red"
    elif rain >= 30:
        marker_color = "orange"
    else:
        marker_color = "green"

    popup_text = (
        f"Weather Point {index}<br>"
        f"Temp: {weather['temperature']}°C<br>"
        f"Rain: {weather['rain']}%<br>"
        f"UV: {round(weather['uv'], 1)}<br>"
        f"Wind: {weather['wind']} km/h"
    )

    folium.Marker(
        [weather["lat"], weather["lon"]],
        popup=popup_text,
        tooltip=f"Weather Point {index}",
        icon=folium.Icon(color=marker_color)
    ).add_to(m)

st.subheader("🛣 Route Map with Weather Points")

st_folium(
    m,
    width=1000,
    height=600
)

st.divider()

st.subheader("🌦 Weather Along Route")

for index, weather in enumerate(weather_results, start=1):
    st.write(f"### Point {index}")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Temp", f"{weather['temperature']}°C")

    with col2:
        st.metric("Rain", f"{weather['rain']}%")

    with col3:
        st.metric("UV", round(weather["uv"], 1))

    with col4:
        st.metric("Wind", f"{weather['wind']} km/h")