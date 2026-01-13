import os

class Config:
    """Configuration for the Flask application."""
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'tasks.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
