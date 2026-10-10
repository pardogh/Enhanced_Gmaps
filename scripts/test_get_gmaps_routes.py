from app.services import google_client 
from pathlib import Path
import requests
import json

STARTING_POINT="Correggio, Italy"
DESTINATION_POINT="Predappio, Italy"

SAMPLE = Path("tests/data/routes_api_sample.json")


def main():
    try:
        response = google_client.get_gmaps_routes(STARTING_POINT,DESTINATION_POINT,True)
    except requests.HTTPError as e:
        print("Errore HTTPS da Google:", e.response.status_code)
        print(e.response.text)
        return

    print("Chiavi della risposta:", list(response.keys()))

    # 2. salva la risposta per i test pytest
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE.write_text(json.dumps(response, indent=2))
    print("Risposta salvata in", SAMPLE)



if __name__ == "__main__":
    main()