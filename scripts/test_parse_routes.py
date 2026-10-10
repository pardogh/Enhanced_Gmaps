from app.services import google_client
import json 
from pathlib import Path

SAMPLE = Path("tests/data/routes_api_sample.json")

def main():
    with open(SAMPLE) as json_file:
        data = json.load(json_file)
        lista = google_client.parse_routes(data)

    
    for route in lista:
        #print(route["distance_meters"])
        print(f"Polyline:{route.polyline}\nPoints:{route.points_list}\nDistance:{route.distance_meters}\nDuration:{route.duration_s}")

if __name__ == "__main__":
    main()