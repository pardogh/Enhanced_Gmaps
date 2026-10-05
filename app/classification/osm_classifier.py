from app.models import Segment, ClassificationResult
from app.classification.base import BaseClassifier

# road_class di Valhalla -> tua categoria di tipo strada
ROAD_TYPE_MAP: dict[str, str] = {
    "motorway": "highway",
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
    "paved": ("asphalt", 3),
    "compacted": ("dirt", 2),
    "gravel" :("dirt", 2),
    "dirt": ("dirt", 1)
}

# Strade dove, senza tag surface, puoi assumere asfalto senza troppi dubbi
ASSUME_PAVED_ROAD_CLASSES: set[str] = {
    "motorway", "trunk", "primary", "secondary"
}

# --- 2. FUNZIONI PURE (niente DB, niente rete) ---

def map_road_type(road_class: str | None) -> str | None:
    """Traduce road_class di Valhalla nella tua categoria.
    Restituisce None se il valore è assente o sconosciuto."""
    if road_class in ROAD_TYPE_MAP:
        return ROAD_TYPE_MAP[road_class]
    else 
        return None
    pass


def map_surface(surface: str | None) -> tuple[str, int] | None:
    """Traduce surface di Valhalla in (categoria, punteggio base).
    Restituisce None se il valore è assente o sconosciuto."""
    if surface in SURFACE_MAP:
        return SURFACE_MAP[surface]
    else
        return None 
    pass


def estimate_confidence(has_explicit_surface: bool, road_class: str | None) -> float:
    match road_class:
        case "highway":
            return 5
        case "extraurban":
            if(has_explicit_surface):
                return 4 
            else:
                return 3 
        case "rural":
            if(has_explicit_surface):
                return 3
            else:
                return 2 
        case "residential":
            if(has_explicit_surface):
                return 4
            else:
                return 3
        case 
    pass

# --- 3. IL CLASSIFICATORE ---

class OsmRulesClassifier(BaseClassifier):

    def classify(self, segment: Segment) -> ClassificationResult | None:
        
        

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
        pass