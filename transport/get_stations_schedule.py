import googlemaps
from datetime import datetime, timedelta
import configparser
import os
from pprint import pprint
from collections import defaultdict

# Path to the config file (one level up from the script)
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'credentials_config.ini')

# Read the config.ini file
config = configparser.ConfigParser()
config.read(config_file_path)

# Access the API key
api_key = config.get('google_maps', 'api_key')

# Google Maps Client
gmaps = googlemaps.Client(key=api_key)


def extract_transit_data(response, existing_entries):
    """Extract transit data from the Google Maps API response."""
    transit_data = []
    for leg in response.get('legs', []):
        for step in leg.get('steps', []):
            if step.get('travel_mode') == 'TRANSIT':
                transit_details = step.get('transit_details', {})
                line = transit_details.get('line', {})
                vehicle = line.get('vehicle', {})
                transit_type = vehicle.get('type', '').upper()

                if transit_type in ['BUS', 'TRAM']:
                    entry = {
                        'type': transit_type,
                        'departure_time': transit_details.get('departure_time', {}).get('text', ''),
                        'arrival_time': transit_details.get('arrival_time', {}).get('text', ''),
                        'departure_stop': transit_details.get('departure_stop', {}).get('name', ''),
                        'arrival_stop': transit_details.get('arrival_stop', {}).get('name', ''),
                        'line': line.get('short_name', ''),
                        'vehicle_name': vehicle.get('name', ''),
                    }

                    # Create a unique identifier for the entry
                    entry_id = (entry['departure_time'], entry['arrival_time'], entry['line'])

                    # Check if this entry already exists to avoid duplicates
                    if entry_id not in existing_entries:
                        transit_data.append(entry)
                        existing_entries.add(entry_id)

    return transit_data


def get_transportation_schedule_one_hour_interval():
    destination_address = 'Zuidas Amsterdam'
    base_departure_time = datetime.now()

    tram_results = defaultdict(list)
    bus_results = defaultdict(list)
    existing_entries = set()  # Initialize the set to track entries

    for interval in range(0, 60, 7):
        departure_time = base_departure_time + timedelta(minutes=interval)
        directions_response = gmaps.directions(
            origin='Amstelveen Stadshart',
            destination=destination_address,
            mode='transit',
            transit_mode='tram|bus',
            alternatives=True,
            departure_time=departure_time,
        )

        if not directions_response:
            continue

        for response in directions_response:
            transit_data = extract_transit_data(response, existing_entries)  # Pass the set here
            for item in transit_data:
                key = (item['departure_stop'], item['arrival_stop'])
                if item['type'] == 'TRAM':
                    tram_results[key].append(item)
                elif item['type'] == 'BUS':
                    bus_results[key].append(item)

    return {'trams': dict(tram_results), 'buses': dict(bus_results)}


def get_data():
    gmaps_response = get_transportation_schedule_one_hour_interval()
    if gmaps_response:
        print('----------')
        pprint(gmaps_response)
        return gmaps_response


if __name__ == '__main__':
    get_data()
