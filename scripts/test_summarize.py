import traceback

from app.models import ValhallaSegment, ClassifiedSegment, GoogleMapsRoute
from app.routing import summarize, CRITICAL_SCORE_THRESHOLD


# ---------- helper per creare dati finti ----------

def make_seg(length):
    return ValhallaSegment(
        segment_key="k", way_id=1, length=length,
        road_class="primary", surface="paved",
        coords=[(44.49, 11.34), (44.50, 11.35)],
    )


def make_judgement(seg, score, road_type="urban", surface_type="asphalt"):
    return ClassifiedSegment(
        segment=seg, source="osm", road_type=road_type,
        surface_type=surface_type, condition_score=score, confidence=0.8,
    )


def make_route():
    return GoogleMapsRoute(
        polyline="abc", points_list=[(44.49, 11.34), (44.50, 11.35)],
        duration_s=600, distance_m=500,
    )


def close(a, b):
    """Confronto tra numeri con virgola, con piccola tolleranza."""
    return abs(a - b) < 1e-9


# ---------- test ----------

def test_caso_misto():
    s1, s2, s3 = make_seg(100), make_seg(300), make_seg(100)
    pairs = [
        (s1, make_judgement(s1, 5, "urban", "asphalt")),
        (s2, make_judgement(s2, 1, "rural", "dirt")),
        (s3, None),
    ]
    r = summarize(pairs, make_route())

    assert close(r.quality_score, 2.0), f"quality_score = {r.quality_score}, atteso 2.0"
    assert close(r.coverage, 0.8), f"coverage = {r.coverage}, atteso 0.8"
    assert close(r.unrated_m, 100), f"unrated_m = {r.unrated_m}, atteso 100"
    assert close(r.critical_m, 300), f"critical_m = {r.critical_m}, atteso 300"
    assert dict(r.distance_by_road_type) == {"urban": 100, "rural": 300}, r.distance_by_road_type
    assert dict(r.distance_by_surface) == {"asphalt": 100, "dirt": 300}, r.distance_by_surface


def test_lista_vuota():
    r = summarize([], make_route())
    assert r.quality_score is None, f"quality_score = {r.quality_score}, atteso None"
    assert r.coverage == 0.0, f"coverage = {r.coverage}, atteso 0.0"
    assert r.unrated_m == 0
    assert r.critical_m == 0


def test_tutti_senza_giudizio():
    s1, s2 = make_seg(200), make_seg(300)
    r = summarize([(s1, None), (s2, None)], make_route())
    assert r.quality_score is None, f"quality_score = {r.quality_score}, atteso None"
    assert r.coverage == 0.0
    assert close(r.unrated_m, 500)


def test_tutti_valutati():
    s1, s2 = make_seg(100), make_seg(100)
    pairs = [(s1, make_judgement(s1, 4)), (s2, make_judgement(s2, 2))]
    r = summarize(pairs, make_route())
    assert close(r.coverage, 1.0)
    assert r.unrated_m == 0
    assert close(r.quality_score, 3.0)


def test_stessa_categoria_si_somma():
    s1, s2 = make_seg(100), make_seg(250)
    pairs = [
        (s1, make_judgement(s1, 4, "urban", "asphalt")),
        (s2, make_judgement(s2, 4, "urban", "asphalt")),
    ]
    r = summarize(pairs, make_route())
    assert dict(r.distance_by_road_type) == {"urban": 350}, r.distance_by_road_type
    assert dict(r.distance_by_surface) == {"asphalt": 350}, r.distance_by_surface


def test_media_pesata_per_lunghezza():
    lungo, corto = make_seg(1000), make_seg(10)
    pairs = [(lungo, make_judgement(lungo, 1)), (corto, make_judgement(corto, 5))]
    r = summarize(pairs, make_route())
    atteso = (1 * 1000 + 5 * 10) / 1010
    assert close(r.quality_score, atteso), f"quality_score = {r.quality_score}, atteso {atteso}"


def test_soglia_critica_inclusiva():
    sopra, uguale = make_seg(100), make_seg(200)
    pairs = [
        (sopra, make_judgement(sopra, CRITICAL_SCORE_THRESHOLD + 1)),
        (uguale, make_judgement(uguale, CRITICAL_SCORE_THRESHOLD)),
    ]
    r = summarize(pairs, make_route())
    assert close(r.critical_m, 200), f"critical_m = {r.critical_m}, atteso 200"


def test_dati_di_google_copiati():
    route = make_route()
    s1 = make_seg(100)
    pairs = [(s1, make_judgement(s1, 3))]
    r = summarize(pairs, route)
    assert r.polyline == route.polyline
    assert r.duration_s == route.duration_s
    assert r.distance_m == route.distance_m
    assert r.pairs == pairs


# ---------- esecuzione ----------

TESTS = [
    test_caso_misto,
    test_lista_vuota,
    test_tutti_senza_giudizio,
    test_tutti_valutati,
    test_stessa_categoria_si_somma,
    test_media_pesata_per_lunghezza,
    test_soglia_critica_inclusiva,
    test_dati_di_google_copiati,
]


def main():
    passed = 0
    for test in TESTS:
        try:
            test()
            print(f"OK      {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FALLITO {test.__name__}: {e}")
        except Exception:
            print(f"ERRORE  {test.__name__}:")
            traceback.print_exc()
    print(f"\n{passed}/{len(TESTS)} test superati")


if __name__ == "__main__":
    main()