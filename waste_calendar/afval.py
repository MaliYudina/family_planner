import datetime as dt
import requests
from bs4 import BeautifulSoup
import json

translation_dict = {
    "Papier en karton": "paper",
    "Groente, Fruit en Tuinafval": "GFT",
    "Plastic en metalen verpakkingen, drankkartons": "PMD"
}

month_translation = {
    "januari": "January",
    "februari": "February",
    "maart": "March",
    "april": "April",
    "mei": "May",
    "juni": "June",
    "juli": "July",
    "augustus": "August",
    "september": "September",
    "oktober": "October",
    "november": "November",
    "december": "December"
}

base_url = "https://www.mijnafvalwijzer.nl/en/{zip_code}/{house_number}/"


def get_current_date():
    return dt.date.today()


def translate_waste_type(original_type):
    return translation_dict.get(original_type, "Unknown")


def translate_date(dutch_date_str):
    # Split the string and remove the day name (first word)
    parts = dutch_date_str.split()
    date_str_without_day = " ".join(parts[1:])  # Skip the first part (day name)

    for nl_month, en_month in month_translation.items():
        if nl_month in date_str_without_day:
            # Replace the Dutch month name with its English counterpart
            date_str = date_str_without_day.replace(nl_month, en_month)
            # Append the current year to the date string
            date_str_with_year = f"{date_str} {dt.datetime.now().year}"
            try:
                # Now parse the date without the day name, using the format "%d %B %Y"
                return dt.datetime.strptime(date_str_with_year, "%d %B %Y").date()
            except ValueError as e:
                print(f"Error parsing date '{date_str_with_year}': {e}")
                return None


def retrieve_location(zip_code, house_number):
    location_url = base_url.format(zip_code=zip_code, house_number=house_number)
    response = requests.get(location_url)
    print(location_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        today_date = get_current_date()
        print("Checking the schedule for today's date and onwards")
        waste_schedule_list = []

        table_elements = soup.find_all('table')
        for table in table_elements:
            date_element = table.find('span', class_='span-line-break')
            description_element = table.find('span', class_='afvaldescr')
            if date_element and description_element:
                dutch_date_str = date_element.text.strip()
                try:
                    waste_date = translate_date(dutch_date_str)
                    if waste_date and waste_date >= today_date:
                        description = translate_waste_type(description_element.text.strip())
                        waste_schedule_list.append({'Date': waste_date.strftime("%d %b"), 'Type': description})
                except ValueError as e:
                    print(f"Error parsing date '{dutch_date_str}': {e}")

        return waste_schedule_list
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return []


def check_waste():
    try:
        waste = retrieve_location(zip_code='1188dm', house_number=46)
        if waste:
            # waste_result = json.dumps(waste, indent=4)
            print(waste)
            return waste
        else:
            print("No future waste schedule found.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    check_waste()
