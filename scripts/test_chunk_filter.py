from app.models import ValhallaSegment, ClassifiedSegment, SegmentsChunk
from app.routing import filter_road_chunks_for_ai
# Assicurati di importare la tua funzione e il dizionario delle soglie
from app.routing import filter_road_chunks_for_ai, MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE

# Per il test, simuliamo le soglie
MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE = {
    "rural": 500,
    "extraurban": 1000
}

def make_mock_segment(road_type: str, length: float, score: int | None) -> ClassifiedSegment:
    """Helper per creare rapidamente segmenti fittizi"""
    v_seg = ValhallaSegment(
        segment_key="dummy_key", 
        way_id=123, 
        length=length, 
        road_class=road_type, 
        surface="paved", 
        coords=[(0.0, 0.0), (1.1, 1.1)]
    )
    return ClassifiedSegment(
        segment=v_seg, 
        source="osm", 
        road_type=road_type, 
        surface_type="asphalt", 
        condition_score=score, 
        confidence=0.5
    )

def test_filter_road_chunks_for_ai():
    # 1. Crea la lista di segmenti da testare
    test_segments = [
        # --- Blocco 1: Rural, brutto, abbastanza lungo (500m, score 2) -> DEVE ESSERE ESTRATTO ---
        make_mock_segment("rural", 300, 2),
        make_mock_segment("rural", 200, 2),
        
        # --- Blocco 2: Extraurban, brutto, ma TROPPO CORTO (300m, soglia è 1000) -> IGNORATO ---
        make_mock_segment("extraurban", 300, 2),
        
        # --- Blocco 3: Rural, bello e lungo (600m, score 4) -> IGNORATO ---
        make_mock_segment("rural", 300, 4),
        make_mock_segment("rural", 300, 4),
        
        # --- Blocco 4: Extraurban, brutto, misto con None, lungo (1100m, avg_score < 2.5) -> DEVE ESSERE ESTRATTO ---
        make_mock_segment("extraurban", 600, 2),
        make_mock_segment("extraurban", 500, None), # Fallback a 0 nel codice
    ]

    # 2. Esegui la funzione
    chunks = filter_road_chunks_for_ai(test_segments)

    # 3. Verifica i risultati attesi (Asserts)
    assert len(chunks) == 2, f"Attesi 2 chunks, ottenuti {len(chunks)}"
    
    assert chunks[0].road_type == "rural"
    assert chunks[0].length == 500.0
    assert chunks[0].avg_score == 2.0
    
    assert chunks[1].road_type == "extraurban"
    assert chunks[1].length == 1100.0
    # Score pesato del blocco 4: (600*2 + 500*0) / 1100 = 1200 / 1100 = 1.09
    assert round(chunks[1].avg_score, 2) == 1.09

    print("Tutti i test passati con successo!")

if __name__ == "__main__":
    test_filter_road_chunks_for_ai()