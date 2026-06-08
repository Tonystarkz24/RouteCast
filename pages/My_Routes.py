from route_manager import load_routes
import streamlit as st

st.title("🛣 My Routes")

routes = load_routes()

if len(routes) == 0:
    st.info("No routes saved yet.")

for route in routes:

    st.subheader(route["name"])

    st.write(
        f"📍 {route['start']} ➜ {route['destination']}"
    )

    st.write(
        f"🕒 Departure Time: {route['time']}"
    )

    st.divider()