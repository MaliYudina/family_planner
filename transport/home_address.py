import googlemaps
from datetime import datetime
import requests
import configparser
import os


# Path to the config file (one level up from the script)
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'credentials_config.ini')

# Read the config.ini file
config = configparser.ConfigParser()
config.read(config_file_path)

# Access the API key
api_key = config.get('google_maps', 'api_key')

# Google Maps Client



def get_home_address_details():
    """
    Geocoding an address based on zip code
    :return: Dictionary with home location details
    """
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode('1182GJ, Amstelveen')

    if geocode_result:
        # Extract relevant information from geocode result
        place_id = geocode_result[0]['place_id']
        home_location = geocode_result[0]['geometry']['location']
        print(home_location)
        print(place_id)
        return home_location
    else:
        print(f'Place_id was not found, {Exception}')
        return None


def find_nearest_transit_station(api_key, home_location):
    """
    Find nearby transit stations based on home location
    :param api_key: Google Maps API key
    :param home_location: Dictionary with home location details
    :return: List of dictionaries with transit station details
    """
    type_place = 'transit_station'
    nearby_search_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch" \
                        f"/json?location=" \
                        f"{home_location['lat']},{home_location['lng']}&radius=400" \
                        f"&type={type_place}&fields=name,place_id,geometry&key={api_key}"

    response = requests.get(nearby_search_url)
    nearby_stations = response.json()

    if response.status_code == 200 and nearby_stations.get("status") == "OK":
        list_of_transit_stations = []

        for station in nearby_stations["results"]:
            # Extract relevant information for each station
            station_details = {
                'name': station['name'],
                'place_id': station['place_id'],
                'location': station['geometry']['location']
            }
            print(f"- {station_details['name']}, {station_details['place_id']}, {station_details['location']}")
            list_of_transit_stations.append(station_details)

        return list_of_transit_stations
    else:
        print(f"Error in Nearby Search: {nearby_stations.get('status', '')} - "
              f"{nearby_stations.get('error_message', '')}")


def clean_up_results(results):
    """
    Clean up the results and store only unique pairs of location names, lat/lng values, and place_ids
    :param results: List of dictionaries with location details
    :return: Dictionary with unique location names as keys and a dictionary containing lat/lng values and place_id as values
    """
    name_to_place_id_dict = {}

    for result in results:
        name = result.get('name', '')
        place_id = result.get('place_id', '')
        location = result.get('location', '')

        if name and place_id:
            # Check if the name is not already in the dictionary
            if name not in name_to_place_id_dict:
                name_to_place_id_dict[name] = place_id

    print(name_to_place_id_dict)
    return name_to_place_id_dict


def retrieve_stations():
    home_location = get_home_address_details()
    transit_stations = find_nearest_transit_station(api_key=api_key, home_location=home_location)
    stations = clean_up_results(transit_stations)
    return stations


if __name__ == '__main__':
    retrieve_stations()
