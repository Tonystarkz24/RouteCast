import json

FILE_NAME = "routes.json"
SELECTED_FILE = "selected_route.json"


def load_routes():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except:
        return []


def save_route(route):

    routes = load_routes()

    routes.append(route)

    with open(FILE_NAME, "w") as file:
        json.dump(routes, file, indent=4)


def delete_route(index):

    routes = load_routes()

    routes.pop(index)

    with open(FILE_NAME, "w") as file:
        json.dump(routes, file, indent=4)


def save_selected_route(route):

    with open(SELECTED_FILE, "w") as file:
        json.dump(route, file, indent=4)


def load_selected_route():

    try:
        with open(SELECTED_FILE, "r") as file:
            return json.load(file)
    except:
        return None