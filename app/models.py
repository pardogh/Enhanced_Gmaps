from dataclasses import dataclass

@dataclass
class valhalla_segment:
    way_id: int
    length: float
    surface: str | None
    road_class: str | None 
    highway: str | None
    
@dataclass 
class classified_segment:
    source: str
    length: float
    road_type: str
    surface_type: str
    condition_score: int
    confidence: float