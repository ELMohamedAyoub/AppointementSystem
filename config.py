# config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'mysql://medical_user:medical_pass@127.0.0.1:3306/medical_appointments'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    DB_HOST = '127.0.0.1'
    DB_USER = 'medical_user'
    DB_PASSWORD = 'medical_pass'
    DB_NAME = 'medical_appointments'
    DB_PORT = 3306
