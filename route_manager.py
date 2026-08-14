import json
from pathlib import Path
import streamlit as st

ROUTES_FILE = Path(__file__).parent / "routes.json"
SELECTED_FILE = Path(__file__).parent / "selected_route.json"


def load_routes():
    if not ROUTES_FILE.exists():
        return []
    try:
        with open(ROUTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_route(route):
    routes = load_routes()
    routes.append(route)
    with open(ROUTES_FILE, "w", encoding="utf-8") as file:
        json.dump(routes, file, indent=4)


def delete_route(index):
    routes = load_routes()
    if 0 <= index < len(routes):
        routes.pop(index)
        with open(ROUTES_FILE, "w", encoding="utf-8") as file:
            json.dump(routes, file, indent=4)


def save_selected_route(route):
    st.session_state["selected_route"] = route
    try:
        with open(SELECTED_FILE, "w", encoding="utf-8") as file:
            json.dump(route, file, indent=4)
    except OSError:
        pass


def load_selected_route():
    if "selected_route" in st.session_state and st.session_state["selected_route"]:
        return st.session_state["selected_route"]

    if SELECTED_FILE.exists():
        try:
            with open(SELECTED_FILE, "r", encoding="utf-8") as file:
                route = json.load(file)
                st.session_state["selected_route"] = route
                return route
        except (json.JSONDecodeError, OSError):
            pass
    return None