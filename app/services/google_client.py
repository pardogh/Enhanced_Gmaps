import time 

import requests
from app.models import GoogleMapsRoute
import googlemaps
import polyline

from os import getenv
from dotenv import load_dotenv

load_dotenv()

ROUTES_URL="https://routes.googleapis.com/directions/v2:computeRoutes"

def get_latitude(geocode_result):
    '''Returns latitude of '''
    return geocode_result[0]['geometry']['location']['lat'] if geocode_result else None

def get_longitude(geocode_result):
    return geocode_result[0]['geometry']['location']['lng'] if geocode_result else None

def parse_durationString(duration: str):
    # Se volessi ottenere direttamente tempo in Ore:Minuti:Secondi -> time.strftime('%H:%M:%S', time.gmtime(duration.removesuffix("s")))
    return duration.removesuffix("s")
    

def get_gmaps_routes(starting_point: str, destination_point: str, avoidTolls: bool) -> dict:
    
    origin = {
        "address" : starting_point
    }

    destination = {
        "address" : destination_point
    }

    headers = {
        "X-Goog-Api-Key": getenv("GOOGLE_API_KEY"),
        "X-Goog-FieldMask":"routes.duration,routes.distanceMeters,routes.polyline"
    }

    payload = {
        "origin": origin,
        "destination": destination,
        "travelMode": "DRIVE",
        "computeAlternativeRoutes": True,
        "routeModifiers": {
            "avoidTolls": avoidTolls
        },
        "units": "METRIC"
    }

    response = requests.post(
        url=ROUTES_URL,
        headers=headers,
        json=payload,
        timeout=30
    )
    print(response.text)
    response.raise_for_status()

    return response.json()

def parse_routes(routes_json: dict) -> list[GoogleMapsRoute]:
    gmaps_routes = []

    for route in routes_json.get("routes",[]):
        distance = route["distanceMeters"]
        duration = parse_durationString(route["duration"])
        poly = route["polyline"]["encodedPolyline"]
        points_list = polyline.decode(poly,precision=5)

        gmaps_routes.append(GoogleMapsRoute(polyline=poly,points_list=points_list,duration_s=duration,distance_meters=distance))

    return gmaps_routes

