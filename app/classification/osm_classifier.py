from app.models import ValhallaSegment, ClassifiedSegment
from app.classification.base import BaseClassifier
from typing import Optional

# road_class di Valhalla -> tua categoria di tipo strada
ROAD_TYPE_MAP: dict[str, str] = {
    "motorway": "highway",
    "trunk": "extraurban",
    "primary": "extraurban",
    "secondary": "extraurban",
    "tertiary": "rural",
    "unclassified": "rural",
    "residential": "urban"
}

# surface di Valhalla -> tua categoria di superficie (senza punteggio)
SURFACE_MAP: dict[str, str] = {
    "paved_smooth": "asphalt",
    "paved": "asphalt",
    "paved_rough": "unknown_paved",
    "compacted": "dirt",
    "gravel": "dirt",
    "dirt": "dirt",
}

# Strade dove, senza tag surface, puoi assumere asfalto senza troppi dubbi
ASSUME_PAVED_ROAD_CLASSES: set[str] = { "highway", "extraurban", "urban" }

# --- 2. FUNZIONI PURE (niente DB, niente rete) ---

def map_road_type(road_class: str | None) -> Optional[str]:
    """Traduce road_class di Valhalla nella tua categoria."""
    return ROAD_TYPE_MAP.get(road_class)

def map_surface(surface: str | None) -> Optional[str]:
    """Traduce surface di Valhalla nella tua categoria di materiale."""
    return SURFACE_MAP.get(surface)

def calculate_score_and_confidence(valhalla_surface: str | None, surface_type: str, road_type: str) -> tuple[int, float]:
    """Incrocia il materiale e il tipo di strada per dedurre voto e confidenza."""
    
    # Caso 1: Superficie palesemente rovinata o non asfaltata
    if surface_type in ["dirt", "unknown_paved"]:
        # Se OSM specifica che è sterrata, la confidenza è buona
        if valhalla_surface == "dirt": 
            return 1, 0.8
        return 2, 0.8

    # Caso 2: Superficie asfaltata esplicitamente dichiarata da OSM
    if valhalla_surface in ["paved_smooth", "paved"]:
        match road_type:
            case "highway":
                return 5, 0.9
            case "extraurban":
                return 4, 0.8
            case "urban":
                return 3, 0.6
            case "rural":
                return 2, 0.4 

    # Caso 3: Superficie non dichiarata, ma assunta (es. autostrada senza tag surface)
    if valhalla_surface is None:
        match road_type:
            case "highway":
                return 4, 0.6
            case "extraurban":
                return 3, 0.5
            case "urban":
                return 3, 0.4
            case "rural":
                return 2, 0.3

    return 2, 0.3

# --- 3. IL CLASSIFICATORE ---

class OsmRulesClassifier(BaseClassifier):

    def classify(self, segment: ValhallaSegment) -> Optional[ClassifiedSegment]:
        # 1. Ricava il tipo di strada
        road_type = map_road_type(segment.road_class)
        if road_type is None:
            return None

        # 2. Ricava o assumi la superficie
        valhalla_surface = segment.surface
        if valhalla_surface is not None:
            surface_type = map_surface(valhalla_surface)
            if surface_type is None:
                return None
        elif road_type in ASSUME_PAVED_ROAD_CLASSES:
            surface_type = "asphalt"
        else:
            return None

        # 3. Calcola punteggio e confidenza con la matrice incrociata
        score, confidence = calculate_score_and_confidence(valhalla_surface, surface_type, road_type)

        return ClassifiedSegment(
            segment=segment,
            road_type=road_type, 
            surface_type=surface_type,
            confidence=confidence,
            condition_score=score,
            source="osm"
        )