from route_manager import (
    load_routes,
    delete_route,
    save_selected_route
)

import streamlit as st

st.title("🛣 My Routes")

routes = load_routes()

if len(routes) == 0:
    st.info("No routes saved yet.")

for index, route in enumerate(routes):

    with st.container():

        st.markdown(f"### 🛣 {route['name']}")

        st.write(f"🌍 Country: {route['country']}")
        st.write(f"📍 Start: {route['start']}")
        st.write(f"🎯 Destination: {route['destination']}")
        st.write(f"🕒 Departure Time: {route['time']}")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗺 View Route",
                key=f"view_{index}"
            ):

                save_selected_route(route)

                st.switch_page(
                    "pages/Route_Details.py"
                )

        with col2:

            if st.button(
                "🗑 Delete",
                key=f"delete_{index}"
            ):

                delete_route(index)

                st.rerun()

        st.divider()