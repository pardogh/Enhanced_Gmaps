from app.models import ValhallaSegment, ClassifiedSegment
from app.classification.base import BaseClassifier
import hashlib, polyline

from typing import Optional, Union

ASSUMED_ASPHALT_SCORE = 3

# road_class di Valhalla -> tua categoria di tipo strada
ROAD_TYPE_MAP: dict[str, str] = {
    "motorway": "highway",
    "trunk": "highway",
    "primary": "extraurban",
    "secondary": "extraurban",
    "tertiary": "rural",
    "unclassified": "rural",
    "residential": "urban"
}

# surface di Valhalla -> (tua categoria di superficie, punteggio base 1-5)
SURFACE_MAP: dict[str, tuple[str, int]] = {
    "paved_smooth": ("asphalt", 5),
    "paved": ("asphalt", 4),
    "paved_rough": ("unknown_paved", 2),
    "compacted": ("dirt", 2),
    "gravel" :("dirt", 2),
    "dirt": ("dirt", 1),
}

# Strade dove, senza tag surface, puoi assumere asfalto senza troppi dubbi
ASSUME_PAVED_ROAD_CLASSES: set[str] = { "highway", "extraurban", "urban" }

# --- 2. FUNZIONI PURE (niente DB, niente rete) ---

def map_road_type(road_class: str | None) -> Optional[str]:
    """Traduce road_class di Valhalla nella tua categoria.
    Restituisce None se il valore è assente o sconosciuto."""
    return ROAD_TYPE_MAP.get(road_class)


def map_surface(surface: str | None) -> Optional[tuple[str, int]]:
    """Traduce surface di Valhalla in (categoria, punteggio base).
    Restituisce None se il valore è assente o sconosciuto."""
    return SURFACE_MAP.get(surface)


def estimate_confidence(has_explicit_surface: bool, road_type: Optional[str]) -> float:
    match road_type:
        case "highway":
            return 0.9
        case "extraurban":
            return 0.8 if has_explicit_surface else 0.6
        case "rural":
            return 0.6 if has_explicit_surface else 0.3
        case "urban":
            return 0.8 if has_explicit_surface else 0.4
        case _:
            return 0.0


# --- 3. IL CLASSIFICATORE ---

class OsmRulesClassifier(BaseClassifier):

    def classify(self, segment: ValhallaSegment) -> Optional[ClassifiedSegment]:
        # Segment Class
        road_type = map_road_type(segment.road_class)
        if segment.road_class is None:
            return None

        # Segment surface
       
        if segment.surface is not None:
            mapped = map_surface(segment.surface)
            if mapped is None:
                return None
            surface_type, score = mapped
        elif road_type in ASSUME_PAVED_ROAD_CLASSES:
            surface_type, score = "asphalt", ASSUMED_ASPHALT_SCORE
        else:
            return None

        confidence = estimate_confidence(segment.surface is not None, road_type)

        return ClassifiedSegment(
            road_type=road_type, 
            surface_type=surface_type,
            confidence=confidence,
            length=segment.length)
      
        # 1. ricava il tipo di strada da segment.road_class
        #    se non riesci -> return None
        #
        # 2. prova a ricavare la superficie da segment.surface
        #    - se esiste: usala, confidenza alta
        #    - se manca: la strada è in ASSUME_PAVED_ROAD_CLASSES?
        #         sì -> assumi asfalto, confidenza media/bassa
        #         no -> return None (lo deciderà l'AI)
        #
        # 3. eventuali aggiustamenti al punteggio (per esempio il tipo
        #    di strada o la lunghezza del segmento), se vuoi
        #
        # 4. costruisci e restituisci ClassificationResult(source="osm", ...)