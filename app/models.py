from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

Coord = tuple[float, float]
SegmentTuple = tuple["ValhallaSegment",Optional["ClassifiedSegment"]]

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
    duration_s: int 
    distance_m: float

@dataclass
class RouteSummary:
    # dati di Google
    polyline: str
    duration_s: int
    distance_m: int
    # dati calcolati
    quality_score: float | None          # None se nessun tratto valutato
    coverage: float                  # 0.0-1.0: metri valutati / metri totali
    distance_by_road_type: dict[str, float]
    distance_by_surface: dict[str, float]
    critical_m: float                # metri con voto <= soglia
    unrated_m: float                 # metri senza giudizio
    pairs: list[tuple[ValhallaSegment, ClassifiedSegment | None]]  # per la mappa, più avanti

@dataclass 
class SegmentsChunk:
    road_type: str 
    length: float 
    avg_score: float 
    segments: list[ClassifiedSegment]

