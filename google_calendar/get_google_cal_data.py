from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
from app_front_flask.config import Config  # Adjust the import path as necessary

# Scopes define the level of access you are requesting from the user
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def auth_google():
    creds = None
    # Check if 'token.pickle' exists and load it if it does
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the GOOGLE_CREDENTIALS_PATH from the Config class
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.GOOGLE_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=54807)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_cal_data():
    creds = auth_google()
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = '2022-01-01T00:00:00Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    return events  # You might want to format these events before returning

def get_calendar():
    print('List of events...')
    required_events = get_cal_data()
    # Format the events into a more readable form or directly use the returned result
    return required_events

if __name__ == '__main__':
    get_calendar()
