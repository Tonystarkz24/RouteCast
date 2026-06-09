from route_manager import save_route
from geocoder import get_coordinates
import streamlit as st

st.title("➕ Add Route")

st.write("Create a new travel route")

route_name = st.text_input(
    "🛣 Route Name",
    placeholder="Example: SLIIT Route"
)

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

start_city = st.text_input(
    "📍 Start City",
    placeholder="Example: Colombo"
)

destination = st.text_input(
    "🎯 Destination City",
    placeholder="Example: Malabe"
)

travel_time = st.time_input("🕒 Travel Time")

if st.button("💾 Save Route"):

    if not route_name:
        st.warning("Please enter a route name.")
        st.stop()

    if not start_city:
        st.warning("Please enter a start city.")
        st.stop()

    if not destination:
        st.warning("Please enter a destination city.")
        st.stop()

    with st.spinner("Finding locations..."):

        start_coords = get_coordinates(
            start_city,
            country
        )

        dest_coords = get_coordinates(
            destination,
            country
        )

    if start_coords is None:
        st.error(
            f"Could not find '{start_city}' in {country}"
        )
        st.stop()

    if dest_coords is None:
        st.error(
            f"Could not find '{destination}' in {country}"
        )
        st.stop()

    route = {
        "name": route_name,

        "country": country,

        "start": start_city,
        "start_lat": start_coords["lat"],
        "start_lon": start_coords["lon"],

        "destination": destination,
        "dest_lat": dest_coords["lat"],
        "dest_lon": dest_coords["lon"],

        "time": str(travel_time)
    }

    save_route(route)

    st.success("✅ Route Saved Successfully!")

    st.write("### Saved Route Information")

    st.write(f"🛣 Route: {route_name}")
    st.write(f"🌍 Country: {country}")

    st.write(
        f"📍 Start: {start_city} "
        f"({start_coords['lat']}, {start_coords['lon']})"
    )

    st.write(
        f"🎯 Destination: {destination} "
        f"({dest_coords['lat']}, {dest_coords['lon']})"
    )

    st.write(f"🕒 Travel Time: {travel_time}")