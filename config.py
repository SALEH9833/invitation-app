# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-vraiment-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.nsfceqykauwcxmuiwjbu:nsfceqykauwcxmuiwjbu@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')