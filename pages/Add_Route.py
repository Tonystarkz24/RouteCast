from route_manager import save_route
from geocoder import search_locations
import streamlit as st

st.title("➕ Add Route")

st.markdown("Create and save your daily travel routes with accurate location search.")

# Route Information

route_name = st.text_input(
    "🛣 Route Name",
    placeholder="Example: Commute to SLIIT"
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

transport_mode = st.selectbox(
    "🚗 Transport Mode",
    [
        "🚗 Car / Vehicle",
        "🚴 Bicycle",
        "🚶 Walking"
    ]
)

profile_map = {
    "🚗 Car / Vehicle": "driving-car",
    "🚴 Bicycle": "cycling-regular",
    "🚶 Walking": "foot-walking"
}

start_city = st.text_input(
    "📍 Start Location",
    placeholder="Example: Wellawatte"
)

destination = st.text_input(
    "🎯 Destination Location",
    placeholder="Example: SLIIT Malabe"
)

travel_time = st.time_input(
    "🕒 Departure Time"
)

st.divider()

# Search Candidates Step
if "start_candidates" not in st.session_state:
    st.session_state["start_candidates"] = []
if "dest_candidates" not in st.session_state:
    st.session_state["dest_candidates"] = []

if st.button("🔍 Search Locations", use_container_width=True):
    if not start_city.strip() or not destination.strip():
        st.warning("Please enter both Start and Destination locations before searching.")
    else:
        with st.spinner("Searching for matching locations..."):
            st.session_state["start_candidates"] = search_locations(start_city, country, limit=5)
            st.session_state["dest_candidates"] = search_locations(destination, country, limit=5)

start_candidates = st.session_state.get("start_candidates", [])
dest_candidates = st.session_state.get("dest_candidates", [])

selected_start_coords = None
selected_dest_coords = None

if start_candidates and dest_candidates:
    st.subheader("📍 Confirm Exact Locations")

    start_options = [c["display_name"] for c in start_candidates]
    dest_options = [c["display_name"] for c in dest_candidates]

    chosen_start_name = st.selectbox("Select Start Location Match:", start_options)
    chosen_dest_name = st.selectbox("Select Destination Location Match:", dest_options)

    selected_start_coords = next(c for c in start_candidates if c["display_name"] == chosen_start_name)
    selected_dest_coords = next(c for c in dest_candidates if c["display_name"] == chosen_dest_name)

# Save Button

if st.button("💾 Save Route", use_container_width=True, type="primary"):

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

    if not selected_start_coords or not selected_dest_coords:
        with st.spinner("🔍 Fetching coordinates..."):
            s_c = search_locations(start_city, country, limit=5)
            d_c = search_locations(destination, country, limit=5)
            if not s_c:
                st.error(f"❌ Could not find '{start_city}' in {country}")
                st.stop()
            if not d_c:
                st.error(f"❌ Could not find '{destination}' in {country}")
                st.stop()
            selected_start_coords = s_c[0]
            selected_dest_coords = d_c[0]

    # Route Object
    route = {
        "name": route_name,
        "country": country,
        "mode": transport_mode,
        "profile": profile_map.get(transport_mode, "driving-car"),
        "start": start_city,
        "start_display": selected_start_coords["display_name"],
        "start_lat": selected_start_coords["lat"],
        "start_lon": selected_start_coords["lon"],
        "destination": destination,
        "dest_display": selected_dest_coords["display_name"],
        "dest_lat": selected_dest_coords["lat"],
        "dest_lon": selected_dest_coords["lon"],
        "time": str(travel_time)
    }

    save_route(route)

    st.success("✅ Route Saved Successfully!")

    st.divider()

    st.subheader("📋 Route Summary")
    st.write(f"🛣 Route Name: **{route_name}**")
    st.write(f"🌍 Country: **{country}**")
    st.write(f"🚗 Mode: **{transport_mode}**")
    st.write(f"📍 Start Found: **{selected_start_coords['display_name']}**")
    st.write(f"🎯 Destination Found: **{selected_dest_coords['display_name']}**")
    st.write(f"🕒 Departure Time: **{travel_time}**")

    with st.expander("📌 Saved Coordinates"):
        st.write(
            f"Start Coordinates: ({selected_start_coords['lat']}, {selected_start_coords['lon']})"
        )
        st.write(
            f"Destination Coordinates: ({selected_dest_coords['lat']}, {selected_dest_coords['lon']})"
        )