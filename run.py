"""The module that runs all logics"""
import datetime
from waste_calendar.afval import check_waste
from transport.get_stations_schedule import get_data
from google_calendar.get_google_cal_data import get_calendar
from transport.get_stations_schedule import get_data
from waste_calendar.afval import check_waste
import json


def welcome_user():
    print("Hello, User!")
    today = datetime.date.today()
    print(f"Today is {today}")
    waste_calendar = check_waste()
    # show all lines in waste calendar
    [print(i) for i in waste_calendar]

    # show all lines in waste calendar
    transport_schedule = get_data()

    calendar_data = get_calendar()
    [print(i) for i in calendar_data]


if __name__ == '__main__':
    welcome_user()
