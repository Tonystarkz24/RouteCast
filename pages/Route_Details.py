import openrouteservice.convert
from route_manager import load_selected_route
from route_service import get_route

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

route_data = get_route(
    start_lon,
    start_lat,
    dest_lon,
    dest_lat
)

if "routes" not in route_data:
    st.error("Routing failed")
    st.json(route_data)
    st.stop()

route_info = route_data["routes"][0]

distance_km = round(
    route_info["summary"]["distance"] / 1000,
    2
)

duration_min = round(
    route_info["summary"]["duration"] / 60
)

st.subheader(route["name"])

col1, col2 = st.columns(2)

with col1:
    st.metric("📏 Distance", f"{distance_km} km")

with col2:
    st.metric("🚗 Travel Time", f"{duration_min} min")

encoded_geometry = route_info["geometry"]

decoded = openrouteservice.convert.decode_polyline(
    encoded_geometry
)

route_points = []

for coord in decoded["coordinates"]:

    lon = coord[0]
    lat = coord[1]

    route_points.append(
        [lat, lon]
    )

center_lat = (start_lat + dest_lat) / 2
center_lon = (start_lon + dest_lon) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11
)

folium.Marker(
    [start_lat, start_lon],
    popup="Start",
    icon=folium.Icon(color="green")
).add_to(m)

folium.Marker(
    [dest_lat, dest_lon],
    popup="Destination",
    icon=folium.Icon(color="red")
).add_to(m)

folium.PolyLine(
    route_points,
    weight=6,
    color="blue"
).add_to(m)

st_folium(
    m,
    width=1000,
    height=600
)