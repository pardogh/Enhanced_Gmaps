from dataclasses import dataclass
Coord = tuple[float, float]

@dataclass
class ValhallaSegment:
    segment_key: str          # identificatore del pezzo di strada (lo calcola il client)
    way_id: int
    length: float             # metri
    road_class: str | None
    surface: str | None
    coords: list[Coord]
    
@dataclass 
class ClassifiedSegment:
    segment: ValhallaSegment  # il pezzo di strada a cui si riferisce il giudizio
    source: str               # "osm", "ai"...
    road_type: str
    surface_type: str
    condition_score: int
    confidence: float

@dataclass 
class GoogleMapsRoute:
    polyline: str            # codificata a precisione 5(valhalla è a 6)
    points_list: list[Coord] 
    duration_s: str 
    distance_meters: float