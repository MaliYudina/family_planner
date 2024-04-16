import logging
from buienradar.buienradar import get_data, parse_data
from buienradar.constants import CONTENT, RAINCONTENT, SUCCESS
from typing import Dict, Tuple

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
TIMEFRAME = 45
LATITUDE = 52.3124  # Amstelveen
LONGITUDE = 4.8709


def fetch_weather_data(latitude: float, longitude: float) -> Dict:
    """
    Fetch weather data from the Buienradar API.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: The raw API response data.
    """
    try:
        return get_data(latitude=latitude, longitude=longitude)
    except Exception as e:
        logging.error(f"Failed to fetch data: {e}")
        return {}


def process_weather_data(result: Dict, latitude: float, longitude: float) -> Dict:
    """
    Parse the fetched weather data to extract necessary details.

    Args:
        result (dict): The raw API response data.
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Parsed weather data.
    """
    if result.get(SUCCESS):
        data = result[CONTENT]
        raindata = result[RAINCONTENT]
        return parse_data(data, raindata, latitude, longitude, TIMEFRAME)
    else:
        logging.error("API call unsuccessful.")
        return {}


def prepare_forecast(result: Dict) -> Dict:
    """
    Prepare the weather forecast data for today and tomorrow.

    Args:
        result (dict): The parsed weather data.

    Returns:
        dict: The formatted weather forecast.
    """
    today_forecast = {
        "stationname": result["data"]["stationname"],
        "feeltemperature": result["data"]["feeltemperature"],
        "maxtemp": result["data"]["forecast"][0]["maxtemp"],
        "rainchance": result["data"]["forecast"][0]["rainchance"],
        "windforce": result["data"]["windforce"]
    }

    tomorrow_forecast = {
        "maxtemp": result["data"]["forecast"][1]["maxtemp"],
        "rainchance": result["data"]["forecast"][1]["rainchance"],
        "windforce": result["data"]["forecast"][1]["windforce"],
    }

    return {
        "today_forecast": today_forecast,
        "tomorrow_forecast": tomorrow_forecast
    }


def get_buienradar_weather() -> Dict:
    """
    Orchestrates the fetching, parsing, and formatting of Buienradar weather data.

    Returns:
        dict: The weather forecasts for today and tomorrow.
    """
    result = fetch_weather_data(LATITUDE, LONGITUDE)
    if result:
        parsed_data = process_weather_data(result, LATITUDE, LONGITUDE)
        if parsed_data:
            formatted_data = prepare_forecast(parsed_data)
            logging.info(formatted_data)
            return formatted_data
    return {}


if __name__ == '__main__':
    get_buienradar_weather()
