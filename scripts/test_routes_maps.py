from app.services import google_client 

STARTING_POINT="Correggio, Italy"
DESTINATION_POINT="Predappio, Italy"

def main():
    google_client.get_gmaps_routes(STARTING_POINT,DESTINATION_POINT,True)


if __name__ == "__main__":
    main()