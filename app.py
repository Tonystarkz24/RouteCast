import streamlit as st
import requests
from route_manager import load_routes, save_selected_route
from weather_service import generate_route_advice, evaluate_saved_route_alerts, calculate_risk_score

st.set_page_config(page_title="RouteCast AI", page_icon="🏠", layout="wide")

st.title("🏠 RouteCast AI - Commuter Dashboard")
st.markdown("Your AI-powered weather-aware travel assistant for daily routes & commutes.")

st.divider()

# Saved Routes & Alerts
routes = load_routes()
route_alerts = evaluate_saved_route_alerts(routes)

if route_alerts:
    st.subheader("🔔 Daily Commute Weather Alerts & Notifications")
    for alert in route_alerts:
        with st.container(border=True):
            st.markdown(f"### 🚨 Weather Hazard Warning: **{alert['name']}** ({alert['start']} ➔ {alert['destination']})")
            a_col1, a_col2 = st.columns([3, 1])
            with a_col1:
                st.warning(f"🌧 **Rain Chance**: {alert['max_rain']}% at planned departure ({alert['time']}) | ⚠️ **Risk**: {alert['risk']}/100 | Mode: {alert['mode']}")
                for advice_item in alert['advice']:
                    st.write(f"- {advice_item}")
            with a_col2:
                if st.button("🗺 Compare 3 Routes", key=f"alert_btn_{alert['name']}", use_container_width=True, type="primary"):
                    save_selected_route(alert["route"])
                    st.switch_page("pages/Route_Details.py")
    st.divider()

# Saved Routes Quick Access Section
st.subheader("🛣 Your Daily Commute Routes")

if not routes:
    st.info("💡 No saved routes yet. Navigate to **Add Route** in the sidebar to add your daily work or school commute!")
else:
    display_routes = routes[:3]
    cols = st.columns(len(display_routes))
    for idx, r in enumerate(display_routes):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### 🛣 {r['name']}")

                st.write(f"📍 **From**: {r['start']}")
                st.write(f"🎯 **To**: {r['destination']}")
                st.write(f"🚗 **Mode**: {r.get('mode', '🚗 Car')}")
                st.write(f"🕒 **Time**: {r['time']}")

                if st.button(f"🗺 Compare 3 Routes", key=f"dash_view_{idx}", use_container_width=True, type="primary"):
                    save_selected_route(r)
                    st.switch_page("pages/Route_Details.py")


st.divider()

# Instant City Weather Advisory
st.subheader("🔍 Quick City Weather & Travel Advisory")

city = st.text_input("Enter Destination City", placeholder="Example: Colombo, Kandy, Sydney...")

if st.button("Get AI Weather Advice", use_container_width=True):
    if not city.strip():
        st.warning("Please enter a city name.")
        st.stop()

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url, timeout=10)
        geo_data = geo_res.json() if geo_res.status_code == 200 else {}

        if "results" in geo_data and len(geo_data["results"]) > 0:

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            display_city = f"{geo_data['results'][0]['name']}, {geo_data['results'][0].get('country', '')}"

            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,wind_speed_10m"
                f"&hourly=precipitation_probability,uv_index"
                f"&forecast_days=1"
            )

            weather_res = requests.get(weather_url, timeout=10)
            weather_data = weather_res.json() if weather_res.status_code == 200 else {}

            if "current" in weather_data and "hourly" in weather_data:
                from datetime import datetime
                cur_h = datetime.now().hour
                hourly_times = weather_data["hourly"].get("time", [])
                h_idx = min(max(0, cur_h), len(hourly_times) - 1)

                temp = weather_data["current"]["temperature_2m"]
                wind = weather_data["current"]["wind_speed_10m"]

                rain = weather_data["hourly"]["precipitation_probability"][h_idx]
                uv = weather_data["hourly"]["uv_index"][h_idx]

                st.subheader(f"Weather overview for {display_city}")

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Temperature", f"{temp} °C")
                with c2:
                    st.metric("Rain Chance (Current Hour)", f"{rain}%")
                with c3:
                    st.metric("UV Index", round(uv, 1))
                with c4:
                    st.metric("Wind Speed", f"{wind} km/h")

                st.subheader("🤖 AI Travel Advice")
                weather_summary = [{"temperature": temp, "rain": rain, "uv": uv, "wind": wind}]
                city_risk = calculate_risk_score(weather_summary)
                advices = generate_route_advice(city_risk, weather_summary)
                for a in advices:
                    st.write(a)
            else:
                st.error("Unable to retrieve forecast data.")

        else:
            st.error("City not found")
    except Exception as e:
        st.error(f"Network error: Unable to fetch weather data ({e})")