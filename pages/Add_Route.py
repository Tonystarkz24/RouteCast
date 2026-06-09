from route_manager import save_route
from geocoder import get_coordinates
import streamlit as st

st.title("➕ Add Route")

st.markdown("Create and save your daily travel routes.")

# Route Information

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
    "📍 Start Location",
    placeholder="Example: Wellawatte"
)

destination = st.text_input(
    "🎯 Destination Location",
    placeholder="Example: Malabe"
)

travel_time = st.time_input(
    "🕒 Travel Time"
)

# Save Button

if st.button("💾 Save Route", use_container_width=True):

    # Validation

    if not route_name.strip():
        st.warning("Please enter a route name.")
        st.stop()

    if not start_city.strip():
        st.warning("Please enter a start location.")
        st.stop()

    if not destination.strip():
        st.warning("Please enter a destination location.")
        st.stop()

    with st.spinner("🔍 Searching locations..."):

        start_coords = get_coordinates(
            start_city,
            country
        )

        dest_coords = get_coordinates(
            destination,
            country
        )

    # Error Handling

    if start_coords is None:
        st.error(
            f"❌ Could not find '{start_city}' in {country}"
        )
        st.stop()

    if dest_coords is None:
        st.error(
            f"❌ Could not find '{destination}' in {country}"
        )
        st.stop()

    # Route Object

    route = {

        "name": route_name,

        "country": country,

        "start": start_city,
        "start_display": start_coords["display_name"],
        "start_lat": start_coords["lat"],
        "start_lon": start_coords["lon"],

        "destination": destination,
        "dest_display": dest_coords["display_name"],
        "dest_lat": dest_coords["lat"],
        "dest_lon": dest_coords["lon"],

        "time": str(travel_time)
    }

    save_route(route)

    st.success("✅ Route Saved Successfully!")

    st.divider()

    st.subheader("📋 Route Summary")

    st.write(f"🛣 Route Name: **{route_name}**")

    st.write(f"🌍 Country: **{country}**")

    st.write(
        f"📍 Start Location Found: **{start_coords['display_name']}**"
    )

    st.write(
        f"🎯 Destination Found: **{dest_coords['display_name']}**"
    )

    st.write(f"🕒 Travel Time: **{travel_time}**")

    with st.expander("📌 Saved Coordinates"):

        st.write(
            f"Start Coordinates: ({start_coords['lat']}, {start_coords['lon']})"
        )

        st.write(
            f"Destination Coordinates: ({dest_coords['lat']}, {dest_coords['lon']})"
        )