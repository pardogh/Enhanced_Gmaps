from app import routing
from app.services import google_client
from app.services.valhalla_client import get_segments
import json 
from pathlib import Path
from collections import Counter

JSON_PATH = Path("tests/data/routes_api_sample.json")

STARTING_POINT = "Centro commerciale I Petali"
DESTINATION_POINT = "Fabbrico"

def main():
    """main"""
    with open(JSON_PATH) as json_file:
        data = json.load(json_file)
        lista = google_client.parse_routes(data)

        for gmaps_routes in lista:
            summarized_route = routing.analyze_route(gmaps_routes)

            """segments = get_segments(gmaps_routes.points_list)

            print(Counter(s.surface for s in segments))
            print(Counter(s.road_class for s in segments))

            for s in segments:
                print(s.way_id)"""
            
            text = f"""
                Duration in seconds: {summarized_route.duration_s} s
                Distance in meters: {summarized_route.distance_m} m 
                Quality Score: {summarized_route.quality_score}
                Coverage: {summarized_route.coverage * 100} %
                Distance by Road Type: {summarized_route.distance_by_road_type}
                Distance by Surface Type: {summarized_route.distance_by_surface} 
                Critical meters: {summarized_route.critical_m}
                Unrated meters: {summarized_route.unrated_m}
            """

            print(text)
            

    
if __name__=="__main__":
    main()