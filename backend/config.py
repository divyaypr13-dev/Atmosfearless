import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/climate.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.getenv('MODEL_PATH', 'model/climate_model.pth')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
