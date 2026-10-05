import polyline, hashlib

def call_trace_attributes(points: list[tuple[float, float]]) -> dict:
    """Manda i punti a Valhalla e restituisce il JSON grezzo."""
    # TODO: requests.post(...), controllo errori, return response.json()

def parse_edges(response: dict) -> list[ValhallaSegment]:
    """Trasforma la risposta JSON in una lista di ValhallaSegment."""
    # TODO: decodifica shape, ciclo sugli edge, crea i ValhallaSegment

def get_segments(points: list[tuple[float, float]]) -> list[ValhallaSegment]:
    """Funzione che usa il resto del programma: chiama + traduce."""
    return parse_edges(call_trace_attributes(points))