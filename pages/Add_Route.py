from route_manager import save_route
import streamlit as st

st.title("➕ Add Route")

route_name = st.text_input("🛣 Route Name")

country = st.selectbox(
    "🌍 Country",
    [
        "Sri Lanka",
        "India",
        "Australia",
        "United Kingdom",
        "United States"
    ]
)

start_city = st.text_input("📍 Start City")

destination = st.text_input("🎯 Destination City")

travel_time = st.time_input("🕒 Travel Time")

if st.button("Save Route"):

    route = {
        "name": route_name,
        "country": country,
        "start": start_city,
        "destination": destination,
        "time": str(travel_time)
    }

    save_route(route)

    st.success("✅ Route Saved Successfully!")