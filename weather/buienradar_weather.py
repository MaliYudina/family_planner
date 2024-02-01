from buienradar.buienradar import (get_data, parse_data)

from buienradar.constants import (CONTENT, RAINCONTENT, SUCCESS)

from pprint import pprint


# minutes to look ahead for precipitation forecast

# (5..120)

def get_buienradar_weather():
    timeframe = 45

    # gps-coordinates for the weather data

    latitude = 52.3124  # Amstelveen

    longitude = 4.8709

    result = get_data(latitude=latitude,
                      longitude=longitude,
                      )

    if result.get(SUCCESS):
        data = result[CONTENT]
        raindata = result[RAINCONTENT]
        result = parse_data(data, raindata, latitude, longitude, timeframe)


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

        formatted_weather_data = {
            "today_forecast": today_forecast,
            "tomorrow_forecast": tomorrow_forecast
        }

        pprint(formatted_weather_data)

        return formatted_weather_data


if __name__ == '__main__':
    get_buienradar_weather()
