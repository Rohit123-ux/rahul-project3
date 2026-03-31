"""
HealthGuard — config.py
Uses SQLite so it works on Vercel (no MySQL server needed).
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'healthguard_secret_2025')

    # SQLite — works everywhere including Vercel (no separate DB server needed)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'healthguard.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
