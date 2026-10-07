import json
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

from app.services.valhalla_client import call_trace_attributes, parse_edges
from app.classification.osm_classifier import OsmRulesClassifier

# Sostituisci con 2-3 punti presi da Google Maps (clic destro -> coordinate)
POINTS = [(44.4949, 11.3426), (44.5000, 11.3500)]
SAMPLE = Path("tests/data/valhalla_sample.json")


def main():
    # 1. chiamata a Valhalla
    try:
        response = call_trace_attributes(POINTS)
    except requests.HTTPError as e:
        print("Errore HTTP da Valhalla:", e.response.status_code)
        print(e.response.text)
        return

    print("Chiavi della risposta:", list(response.keys()))
    print("Numero di edge:", len(response.get("edges", [])))

    # 2. salva la risposta per i test pytest
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE.write_text(json.dumps(response, indent=2))
    print("Risposta salvata in", SAMPLE)

    # 3. parsing
    segments = parse_edges(response)
    print("Segmenti ottenuti:", len(segments))
    print("Valori road_class:", Counter(s.road_class for s in segments))
    print("Valori surface:   ", Counter(s.surface for s in segments))

if __name__ == "__main__":
    main()