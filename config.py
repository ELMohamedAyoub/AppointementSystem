# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER', 'medical_user')}:{os.getenv('DB_PASSWORD', 'medical_pass')}@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'medicalpro')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = [os.getenv('ADMIN_EMAIL', 'your-email@example.com')]
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_USER = os.getenv('DB_USER', 'medical_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'medical_pass')
    DB_NAME = os.getenv('DB_NAME', 'medicalpro')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
