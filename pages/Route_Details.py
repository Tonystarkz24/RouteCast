import math
from route_manager import load_selected_route
from route_service import get_route
from weather_service import (
    get_hourly_forecast,
    extract_weather_at_hour,
    calculate_risk_score,
    generate_route_advice,
    find_best_departure_time
)

import streamlit as st
import folium
import openrouteservice.convert
from streamlit_folium import st_folium


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate Haversine distance in kilometers between two coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def sample_points_by_distance(points, sample_count=5):
    """Sample points along a polyline at equal physical kilometer intervals."""
    if not points or len(points) <= sample_count:
        return points

    cum_distances = [0.0]
    total_dist = 0.0
    for i in range(1, len(points)):
        d = haversine_distance(points[i-1][0], points[i-1][1], points[i][0], points[i][1])
        total_dist += d
        cum_distances.append(total_dist)

    if total_dist == 0:
        step = max(1, len(points) // sample_count)
        return points[::step][:sample_count]

    target_intervals = [i * (total_dist / (sample_count - 1)) for i in range(sample_count)]
    sampled = []

    for target in target_intervals:
        best_idx = min(range(len(cum_distances)), key=lambda i: abs(cum_distances[i] - target))
        sampled.append(points[best_idx])

    return sampled


st.title("🗺 Route Details & Alternative Paths")

route = load_selected_route()

if route is None:
    st.warning("No route selected.")
    st.stop()

start_lat = route["start_lat"]
start_lon = route["start_lon"]
dest_lat = route["dest_lat"]
dest_lon = route["dest_lon"]
transport_mode = route.get("mode", "🚗 Car / Vehicle")
profile = route.get("profile", "driving-car")

st.subheader(f"🛣 {route['name']}")
st.write(f"📍 **Start**: {route.get('start_display', route['start'])}")
st.write(f"🎯 **Destination**: {route.get('dest_display', route['destination'])}")
st.write(f"🌍 **Country**: {route['country']} | 🚗 **Transport**: {transport_mode}")
st.write(f"🕒 **Planned Time**: {route['time']}")

with st.spinner("Calculating 3 alternative real-road routes & analyzing weather..."):
    route_data = get_route(start_lon, start_lat, dest_lon, dest_lat, profile=profile)

if "error" in route_data:
    st.error(f"❌ Routing Error: {route_data['error']}")
    st.info("The OpenRouteService API may be temporarily unavailable. Please try again.")
    st.stop()

if "routes" not in route_data or not route_data["routes"]:
    st.error("❌ Routing failed - unexpected response format")
    st.stop()

routes_list = route_data["routes"]
colors = ["#2563EB", "#9333EA", "#0D9488"]

evaluated_routes = []

try:
    dep_parts = str(route["time"]).split(":")
    dep_hour_val = int(dep_parts[0]) + (int(dep_parts[1]) / 60.0 if len(dep_parts) > 1 else 0.0)
except Exception:
    dep_hour_val = 12.0

for idx, r_info in enumerate(routes_list):
    if "points" in r_info:
        points = r_info["points"]
    else:
        encoded_geom = r_info["geometry"]
        decoded = openrouteservice.convert.decode_polyline(encoded_geom)
        points = [[coord[1], coord[0]] for coord in decoded["coordinates"]]

    dist_km = round(r_info["summary"]["distance"] / 1000, 2)
    duration_sec = r_info["summary"]["duration"]

    h = int(duration_sec // 3600)
    m = int((duration_sec % 3600) // 60)
    dur_str = f"{h} hr {m} mins" if h > 0 else f"{m} mins"

    # Haversine distance-based equal km sampling
    sampled_points = sample_points_by_distance(points, sample_count=5)

    # Time-synced segment weather forecasting
    duration_hours = duration_sec / 3600.0
    weather_list = []

    for p_idx, p in enumerate(sampled_points):
        segment_progress = p_idx / max(1, (len(sampled_points) - 1))
        arrival_hour = round(dep_hour_val + (segment_progress * duration_hours))
        w = extract_weather_at_hour(get_hourly_forecast(p[0], p[1]), p[0], p[1], arrival_hour)
        if w:
            w["lat"], w["lon"] = p[0], p[1]
            weather_list.append(w)


    risk = calculate_risk_score(weather_list, transport_mode)
    advice = generate_route_advice(risk, weather_list, transport_mode)

    try:
        cur_hour = int(str(route["time"]).split(":")[0])
    except (ValueError, AttributeError, IndexError):
        cur_hour = 12

    best_dep = find_best_departure_time(weather_list, cur_hour, transport_mode)

    evaluated_routes.append({
        "index": idx + 1,
        "label": "🏆 Best Route" if idx == 0 else f"🛣 Alternative {idx + 1}",
        "distance": dist_km,
        "duration": dur_str,
        "duration_sec": duration_sec,
        "risk": risk,
        "weather": weather_list,
        "advice": advice,
        "best_departure": best_dep,
        "points": points,
        "color": colors[idx % len(colors)]
    })

# Sort or rank routes (Primary is lowest risk & fastest)
st.divider()
st.subheader("🔀 Route Comparison (Top 3 Alternatives)")

cols = st.columns(len(evaluated_routes))
for i, r in enumerate(evaluated_routes):
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"### {r['label']}")
            st.metric("📏 Distance", f"{r['distance']} km")
            st.metric("⏱ Travel Time", r["duration"])
            st.metric("⚠️ Weather Risk", f"{r['risk']}/100")
            c_val = r['color']
            st.markdown(f"**Map Path**: <span style='color:{c_val}; font-weight:bold;'>█ Polyline</span>", unsafe_allow_html=True)



# Select active route for detailed breakdown
selected_route_idx = st.radio(
    "Select Route Path to View Map & Advisories:",
    options=range(len(evaluated_routes)),
    format_func=lambda i: f"{evaluated_routes[i]['label']} ({evaluated_routes[i]['distance']} km, Risk: {evaluated_routes[i]['risk']}/100)"
)

active_r = evaluated_routes[selected_route_idx]

st.divider()

st.subheader(f"🤖 AI Analysis for {active_r['label']}")

col_a, col_b = st.columns(2)
with col_a:
    st.info(f"Recommended Departure: **{active_r['best_departure']['hour']:02d}:00** (Min Risk: {round(active_r['best_departure']['risk'])}/100)")
with col_b:
    st.write(f"Current Planned Time: **{route['time']}**")

st.markdown("#### 📋 Travel & Outfit Advisories:")
for adv in active_r["advice"]:
    st.write(adv)

# Render Folium Map
st.subheader("🛣 Multi-Route Map View")

all_lats = [p[0] for r in evaluated_routes for p in r["points"]]
all_lons = [p[1] for r in evaluated_routes for p in r["points"]]

m = folium.Map(location=[sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)])

# Add start and end markers
folium.Marker(
    [start_lat, start_lon],
    popup=f"Start: {route['start']}",
    tooltip="Start Location",
    icon=folium.Icon(color="green", icon="play")
).add_to(m)

folium.Marker(
    [dest_lat, dest_lon],
    popup=f"Destination: {route['destination']}",
    tooltip="Destination Location",
    icon=folium.Icon(color="red", icon="stop")
).add_to(m)

# Draw all alternative route polylines
for r in evaluated_routes:
    is_active = (r["index"] == active_r["index"])
    folium.PolyLine(
        r["points"],
        weight=8 if is_active else 4,
        color=r["color"],
        opacity=0.9 if is_active else 0.5,
        tooltip=f"{r['label']} ({r['distance']} km)"
    ).add_to(m)

# Add weather markers for active route
for idx, w in enumerate(active_r["weather"], start=1):
    rain = w["rain"]
    marker_color = "red" if rain >= 60 else "orange" if rain >= 30 else "green"
    popup_txt = f"Point {idx}<br>Temp: {w['temperature']}°C<br>Rain: {w['rain']}%<br>UV: {round(w['uv'],1)}<br>Wind: {w['wind']} km/h"
    folium.Marker(
        [w["lat"], w["lon"]],
        popup=popup_txt,
        tooltip=f"Weather Point {idx}",
        icon=folium.Icon(color=marker_color, icon="cloud")
    ).add_to(m)

# Auto-fit map bounds dynamically with safety padding
min_lat, max_lat = min(all_lats), max(all_lats)
min_lon, max_lon = min(all_lons), max(all_lons)
if min_lat == max_lat:
    min_lat -= 0.005
    max_lat += 0.005
if min_lon == max_lon:
    min_lon -= 0.005
    max_lon += 0.005

m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])


st.divider()

st.subheader("📈 Dynamic Hourly Weather Trend for Route")
if active_r["weather"] and "hourly" in active_r["weather"][0]:
    import pandas as pd
    first_w = active_r["weather"][0]["hourly"]
    times = [t.split("T")[1][:5] for t in first_w.get("time", [])[:24]]
    rains = first_w.get("precipitation_probability", [])[:24]
    temps = first_w.get("temperature_2m", [])[:24]

    chart_df = pd.DataFrame({
        "Rain Probability (%)": rains,
        "Temperature (°C)": temps
    }, index=times)

    st.line_chart(chart_df)

st.divider()

st.subheader("🌦 Segment Weather Details")
for idx, w in enumerate(active_r["weather"], start=1):
    st.write(f"### Point {idx}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Temp", f"{w['temperature']}°C")
    with c2:
        st.metric("Rain Chance", f"{w['rain']}%")
    with c3:
        st.metric("UV Index", round(w['uv'], 1))
    with c4:
        st.metric("Wind Speed", f"{w['wind']} km/h")
