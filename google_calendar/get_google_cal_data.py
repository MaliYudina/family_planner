

def auth_google():
    pass


def get_cal_data():
    print("Google Cal data")
    events = []
    results = ['doctor', 'meeting', 'party']
    for r in results:
        events.append(r)
    return events


def get_calendar():
    print('List of events...')
    required_events = get_cal_data()
    return required_events


if __name__ == '__main__':
    get_calendar()
