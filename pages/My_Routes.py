from route_manager import (
    load_routes,
    delete_route,
    save_selected_route
)

import streamlit as st

st.title("🛣 My Routes")
st.markdown("Manage your saved daily commute routes.")

routes = load_routes()

if len(routes) == 0:
    st.info("💡 No routes saved yet. Click **Add Route** in the sidebar to create your first commute route!")
else:
    for index, route in enumerate(routes):
        with st.container(border=True):
            st.markdown(f"### 🛣 {route['name']}")

            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **Start**: {route.get('start_display', route['start'])}")
                st.write(f"🎯 **Destination**: {route.get('dest_display', route['destination'])}")
            with c2:
                st.write(f"🚗 **Transport Mode**: {route.get('mode', '🚗 Car')}")
                st.write(f"🕒 **Planned Time**: {route['time']}")

            b_col1, b_col2 = st.columns(2)

            with b_col1:
                if st.button("🗺 Compare 3 Routes", key=f"view_{index}", use_container_width=True, type="primary"):
                    save_selected_route(route)
                    st.switch_page("pages/Route_Details.py")

            with b_col2:
                if st.button("🗑 Delete Route", key=f"delete_{index}", use_container_width=True):
                    delete_route(index)
                    st.rerun()