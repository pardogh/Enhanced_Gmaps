import polyline, hashlib
from app.models import ValhallaSegment

def make_segment_key(way_id: int, start: tuple[float, float], end: tuple[float, float]) -> str:
    a, b = sorted([start, end])
    raw = f"{way_id}|{a[0]:.6f},{a[1]:.6f}|{b[0]:.6f},{b[1]:.6f}"
    return hashlib.sha1(raw.encode()).hexdigest()

def call_trace_attributes(points: list[tuple[float, float]]) -> dict:
    """Manda i punti a Valhalla e restituisce il JSON grezzo."""
    # TODO: requests.post(...), controllo errori, return response.json()

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