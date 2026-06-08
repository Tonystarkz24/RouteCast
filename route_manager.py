import json

FILE_NAME = "routes.json"

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
        