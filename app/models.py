from dataclasses import dataclass

@dataclass
class ValhallaSegment:
    way_id: int
    length: float
    surface: str | None
    road_class: str | None
    start_coord: float 
    end_coord: float
    begin_shape_index: int 
    end_shape_index: int
    shape: str
    
@dataclass 
class ClassifiedSegment:
    source: str
    length: float
    road_type: str
    surface_type: str
    condition_score: int
    confidence: float
    start: tuple[float,float]
    end: tuple[float,float]
    segment_key: str