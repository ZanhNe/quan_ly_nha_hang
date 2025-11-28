from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
# from datetime import timedelta

load_dotenv()


DB_PASSWORD = quote_plus(os.getenv('DB_PASS'))
DB_URL = f'{os.getenv('DB_DRIVER')}://{os.getenv('DB_USERNAME')}:{DB_PASSWORD}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'hard to guess key'
    SESSION_COOKIE_HTTPONLY = True # Chặn Javascript đọc cookie (chống XSS)
    SESSION_COOKIE_SECURE = False  # Để True nếu chạy HTTPS
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


    DEBUG = os.getenv('DEBUG', 'False') == 'True'

