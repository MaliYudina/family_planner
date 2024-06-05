from pathlib import Path
import os
import json
import configparser

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent
DB_DIR = PARENT_DIR / 'database'


class Config:
    DATABASE_URI = str(DB_DIR / 'db.sqlite')
    print(f"Database URI: {DATABASE_URI}")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_URI.replace('\\', '/')
    print(f"SQLAlchemy Database URI: {SQLALCHEMY_DATABASE_URI}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CREDENTIALS_PATH = str(BASE_DIR / 'google_secret.json')
    print(f"Google Credentials Path: {GOOGLE_CREDENTIALS_PATH}")

    # Read the API key from the credentials_config.ini file
    config_path = os.path.join(BASE_DIR, 'credentials_config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    GOOGLE_MAPS_API_KEY = config.get('google_maps', 'api_key', fallback=None)
    print(f"Google Maps API Key: {GOOGLE_MAPS_API_KEY}")


secret_key = os.getenv('SECRET_KEY', 'no Secret_key found')

try:
    with open(Config.GOOGLE_CREDENTIALS_PATH, 'r') as file:
        google_credentials_data = json.load(file)
        print(f"Google Credentials Data: {google_credentials_data}")  # Display the data for verification
except Exception as e:
    print(f"Error opening or reading the Google JSON file: {e}")
