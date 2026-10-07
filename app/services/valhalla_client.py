import polyline, hashlib
from app.models import ValhallaSegment
import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def make_segment_key(way_id: int, start: tuple[float, float], end: tuple[float, float]) -> str:
    a, b = sorted([start, end])
    raw = f"{way_id}|{a[0]:.6f},{a[1]:.6f}|{b[0]:.6f},{b[1]:.6f}"
    return hashlib.sha1(raw.encode()).hexdigest()

'''
curl -s http://localhost:8002/trace_attributes \
  -H "Content-Type: application/json" \
  -d '{
    "shape":[{"lat":44.8450,"lon":10.7275},{"lat":44.8448,"lon":10.7288}],
    "costing":"auto",
    "shape_match":"map_snap",
    "filters":{"attributes":["edge.way_id","edge.surface","edge.road_class","edge.length"],"action":"include"}
  }'
'''

def call_trace_attributes(points: list[tuple[float, float]]) -> dict:
    """Manda i punti a Valhalla e restituisce il JSON grezzo."""

    if not points:
        return None


    shape=[]
    for lat,lon in points:
        shape.append({"lat": lat, "lon": lon})

    filters={}
    filters = {"attributes":[
        "edge.way_id",
        "edge.surface",
        "edge.road_class",
        "edge.length",
        "edge.begin_shape_index",
        "edge.end_shape_index",
        "shape"
    ],
    "action": "include"}

    data_diz = {
        "shape" : shape,
        "costing" : "auto",
        "shape_match":"map_snap",
        "filters": filters
    }
    
    response = requests.post(
        url=getenv("VALHALLA_URL") + "/trace_attributes",
        json=data_diz,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def parse_edges(response: dict) -> list[ValhallaSegment]:
    """Trasforma la risposta JSON in una lista di ValhallaSegment."""
    valhalla_segment_list=[]
    
    points = polyline.decode(response["shape"], precision=6)   # lista di (lat, lon)
    for edge in response["edges"]:
        coords = points[edge["begin_shape_index"] : edge["end_shape_index"] + 1]
        if not coords:
            print(f"Coords for edge {edge} are empty!")
            continue

        start, end = coords[0], coords[-1]

        valhalla_segment_list.append(ValhallaSegment(
            segment_key=make_segment_key(edge["way_id"],start,end),
            way_id=edge["way_id"],
            length=edge["length"] * 1000,
            road_class=edge.get("road_class"),
            surface=edge.get("surface"),
            coords=coords
        ))

    return valhalla_segment_list    

def get_segments(points: list[tuple[float, float]]) -> list[ValhallaSegment]:
    """Funzione che usa il resto del programma: chiama + traduce."""
    return parse_edges(call_trace_attributes(points))