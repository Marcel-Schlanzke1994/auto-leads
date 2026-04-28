from __future__ import annotations

import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "replace-with-a-long-random-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///leads.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "8"))
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    PLACES_PROVIDER = os.getenv("PLACES_PROVIDER", "google_places").lower()
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
