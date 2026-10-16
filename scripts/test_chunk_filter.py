from app.models import ValhallaSegment, ClassifiedSegment, SegmentsChunk, Coord
from app.routing import (
    filter_road_chunks_for_ai, 
    get_sample_points_from_chunk,
    MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE,
    SAMPLE_INTERVAL_PER_ROAD_TYPE
)

def make_mock_segment(
    road_type: str, 
    length: float, 
    score: int | None, 
    coords: list[Coord]
) -> ClassifiedSegment:
    """Helper per creare segmenti fittizi con coordinate personalizzate"""
    v_seg = ValhallaSegment(
        segment_key="dummy_key", 
        way_id=123, 
        length=length, 
        road_class=road_type, 
        surface="paved", 
        coords=coords
    )
    return ClassifiedSegment(
        segment=v_seg, 
        source="osm", 
        road_type=road_type, 
        surface_type="asphalt", 
        condition_score=score, 
        confidence=0.5
    )

def test_chunk_filter_and_sampling():
    # Setup dati di test:
    # Chunk 1: Rural (lunghezza totale = 600m < intervallo 800m -> atteso 1 punto centrale)
    # Seg 1 (300m): coord [(10.0, 10.0), (10.1, 10.1)]
    # Seg 2 (300m): coord [(10.2, 10.2), (10.3, 10.3)] -> il punto a metà (300m) cade qui!
    
    # Chunk 2: Extraurban (lunghezza totale = 1800m > intervallo 1500m -> attesi 1 o 2 punti)
    
    test_segments = [
        # --- Blocco 1: Rural (2 segmenti da 300m, score 2) ---
        make_mock_segment("rural", 300, 2, [(10.0, 10.0), (10.1, 10.1)]),
        make_mock_segment("rural", 300, 2, [(10.2, 10.2), (10.3, 10.3)]),
        
        # --- Blocco 2: Extraurban (2 segmenti da 900m = 1800m, score 1) ---
        make_mock_segment("extraurban", 900, 1, [(20.0, 20.0), (20.1, 20.1)]),
        make_mock_segment("extraurban", 900, 1, [(20.2, 20.2), (20.3, 20.3)]),
    ]

    # 1. Filtra i chunks
    chunks = filter_road_chunks_for_ai(test_segments)
    assert len(chunks) == 2, f"Attesi 2 chunks, ottenuti {len(chunks)}"

    # 2. Test Campionamento Chunk 1 (Rural - 600m)
    # L'intervallo rural è 800m -> points_number = max(1, 600 // 800) = 1 punto (caso centrale)
    rural_points = get_sample_points_from_chunk(chunks[0])
    assert len(rural_points) == 1, f"Atteso 1 punto per il chunk rural, ottenuti {len(rural_points)}"
    
    # La metà del chunk (300m) viene raggiunta al secondo segmento.
    # Il centro di [(10.2, 10.2), (10.3, 10.3)] è l'indice len // 2 -> (10.3, 10.3)
    print(f"Punto estratto per Chunk Rural (1 punto): {rural_points[0]}")

    # 3. Test Campionamento Chunk 2 (Extraurban - 1800m)
    # L'intervallo extraurban è 1500m -> points_number = max(1, 1800 // 1500) = 1 punto campionato ogni >= 1500m
    extraurban_points = get_sample_points_from_chunk(chunks[1])
    assert len(extraurban_points) >= 1, "Atteso almeno 1 punto per extraurban"
    print(f"Punti estratti per Chunk Extraurban: {extraurban_points}")

    print("\nTutti i test passati con successo!")

if __name__ == "__main__":
    test_chunk_filter_and_sampling()