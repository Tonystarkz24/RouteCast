from route_manager import load_selected_route

import streamlit as st
import folium

from streamlit_folium import st_folium

st.title("🗺 Route Details")

route = load_selected_route()

if route is None:
    st.warning("No route selected.")
    st.stop()

# Route Information

st.subheader(f"🛣 {route['name']}")

col1, col2 = st.columns(2)

with col1:
    st.metric("🌍 Country", route["country"])

with col2:
    st.metric("🕒 Travel Time", route["time"])

st.write(f"📍 Start: {route['start']}")
st.write(f"🎯 Destination: {route['destination']}")

# Coordinates

start_lat = route["start_lat"]
start_lon = route["start_lon"]

dest_lat = route["dest_lat"]
dest_lon = route["dest_lon"]

with st.expander("📌 Route Coordinates"):

    st.write(
        f"Start Coordinates: ({start_lat}, {start_lon})"
    )

    st.write(
        f"Destination Coordinates: ({dest_lat}, {dest_lon})"
    )

# Map Center

center_lat = (start_lat + dest_lat) / 2
center_lon = (start_lon + dest_lon) / 2

# Create Map

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=10
)

# Start Marker

folium.Marker(
    [start_lat, start_lon],
    popup=f"Start: {route['start']}",
    tooltip=route['start'],
    icon=folium.Icon(color="green")
).add_to(m)

# Destination Marker

folium.Marker(
    [dest_lat, dest_lon],
    popup=f"Destination: {route['destination']}",
    tooltip=route['destination'],
    icon=folium.Icon(color="red")
).add_to(m)

# Route Line

folium.PolyLine(
    [
        [start_lat, start_lon],
        [dest_lat, dest_lon]
    ],
    weight=5,
    opacity=0.8
).add_to(m)

st.subheader("🛣 Route Map")

st_folium(
    m,
    width=1000,
    height=600
)

# Future Features Section

st.divider()

st.subheader("🚀 Upcoming Route Intelligence")

st.info(
    """
    Coming Next:
    
    • Real Road Routing
    • Distance Calculation
    • Estimated Travel Duration
    • Weather Along Route
    • Risk Score
    • Comfort Score
    • AI Travel Recommendations
    """
)