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
    distance_m: float

@dataclass 
class RouteSummary:
    polyline: str
    duration_s: str
    distance_m: float
    quality_score: float
    distance_per_road_type: dict 
    distance_per_road_surface: dict 
    classifiedSegment_list: list[ClassifiedSegment]