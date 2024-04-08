from pathlib import Path
import os
import json

BASE_DIR = Path(__file__).parent
PARENT_DIR = BASE_DIR.parent



class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              str(BASE_DIR.joinpath('db.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CREDENTIALS_PATH = str(PARENT_DIR.joinpath('google_secret.json'))



secret_key = os.getenv('SECRET_KEY', 'no Secret_key found')


try:
    with open(Config.GOOGLE_CREDENTIALS_PATH, 'r') as file:
        google_credentials_data = json.load(file)
        print(google_credentials_data)  # Display the data for verification
except Exception as e:
    print(f"Error opening or reading the Google JSON file: {e}")
