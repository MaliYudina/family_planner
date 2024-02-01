import datetime as dt
import requests
from bs4 import BeautifulSoup
import json

base_url = "https://www.mijnafvalwijzer.nl/en/{zip_code}/{house_number}/"


# 'https://www.mijnafvalwijzer.nl/en/1188dm/46/'

def get_current_date():  # return named tuple of month and year
    current_date = dt.date.today()
    # Get the current month as a string
    current_month = current_date.today().strftime("%B")
    current_year = current_date.strftime("%Y")
    print('month: ', current_month)
    print('year: ', current_year)
    return current_month.lower(), current_year


def retrieve_location(zip_code, house_number):
    location_url = base_url.format(zip_code=zip_code, house_number=house_number)
    response = requests.get(location_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # schedule_element = soup.find('div', class_='ophaaldagen')
        current_date = get_current_date()
        print("Checking the schedule for {}".format(current_date))
        month = current_date[0]
        year = current_date[1]
        current_month_div = soup.find('div', id=f'{month.lower()}-{year}')
        table_elements = current_month_div.find_all('table')

        waste_schedule_list = []

        # Loop through the table elements and extract the desired information
        for table in table_elements:
            date = table.find('span', class_='span-line-break').text
            description = table.find('span', class_='afvaldescr').text
            waste_schedule_list.append({'Date': date, 'Type': description})
        # Print the extracted data
        # for item in data_list:
        #     print(item)

        return waste_schedule_list


def check_waste():
    try:
        waste = retrieve_location(zip_code='1188dm', house_number=46)
        return waste
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    check_waste()

