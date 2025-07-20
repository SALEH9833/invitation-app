# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-vraiment-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = 'postgresql://projet_invitation_user:test123@localhost:5432/invitation_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === CONFIGURATION POUR FLASK-MAIL ===
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')