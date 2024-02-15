from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
print(BASE_DIR)


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                              str(BASE_DIR.joinpath('db.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

secret_key = os.getenv('SECRET_KEY', 'no Secret_key found')
