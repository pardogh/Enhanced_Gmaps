import googlemaps 
import requests
import pandas
from app.models import GoogleMapsRoute
from os import getenv
from dotenv import load_dotenv

load_dotenv()

ROUTES_URL="https://routes.googleapis.com/directions/v2:computeRoutes"

def get_latitude(geocode_result):
    '''Returns latitude of '''
    return geocode_result[0]['geometry']['location']['lat'] if geocode_result else None

def get_longitude(geocode_result):
    return geocode_result[0]['geometry']['location']['lng'] if geocode_result else None


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
    