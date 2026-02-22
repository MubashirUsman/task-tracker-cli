import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join('/app/data', 'tasks.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
