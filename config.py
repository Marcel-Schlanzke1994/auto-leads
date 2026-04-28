from __future__ import annotations

import os
from dataclasses import dataclass


def _as_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _as_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


@dataclass(frozen=True, slots=True)
class ServicePolicy:
    timeout: float
    min_interval_seconds: float


class Config:
    ENV = os.getenv("FLASK_ENV", "production").lower()
    DEBUG = os.getenv("FLASK_DEBUG", "0").strip() in {"1", "true", "yes", "on"}
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///leads.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = _as_int("APP_PORT", 5000)
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    REQUEST_TIMEOUT = _as_float("REQUEST_TIMEOUT", 8.0)
    USER_AGENT = os.getenv("USER_AGENT", "auto-leads/3.0 (+website-audit)").strip()

    SEARCH_DEFAULT_CITIES = [
        city.strip()
        for city in os.getenv(
            "SEARCH_DEFAULT_CITIES",
            "Köln, Bonn, Leverkusen",
        ).split(",")
        if city.strip()
    ]
    SEARCH_MAX_TARGET_COUNT = _as_int("SEARCH_MAX_TARGET_COUNT", 1000)
    SEARCH_TEXT_PAGE_LIMIT = _as_int("SEARCH_TEXT_PAGE_LIMIT", 60)
    SEARCH_MAX_RAW_RESULTS = _as_int("SEARCH_MAX_RAW_RESULTS", 3000)

    CRAWL_MAX_PAGES = _as_int("CRAWL_MAX_PAGES", 10)
    CRAWL_DELAY_SECONDS = _as_float("CRAWL_DELAY_SECONDS", 0.1)

    PLACES_PROVIDER = os.getenv("PLACES_PROVIDER", "google_places").lower().strip()
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "").strip()

    GOOGLE_PLACES_TIMEOUT = _as_float("GOOGLE_PLACES_TIMEOUT", REQUEST_TIMEOUT)
    GOOGLE_PLACES_MIN_INTERVAL_SECONDS = _as_float(
        "GOOGLE_PLACES_MIN_INTERVAL_SECONDS", 2.1
    )
    GOOGLE_PLACES_RETRY_MAX_ATTEMPTS = _as_int("GOOGLE_PLACES_RETRY_MAX_ATTEMPTS", 4)
    GOOGLE_PLACES_RETRY_BACKOFF_BASE = _as_float(
        "GOOGLE_PLACES_RETRY_BACKOFF_BASE", 0.5
    )
    GOOGLE_PLACES_RETRY_MAX_DELAY = _as_float("GOOGLE_PLACES_RETRY_MAX_DELAY", 8.0)
    GOOGLE_PLACES_RETRY_JITTER = _as_float("GOOGLE_PLACES_RETRY_JITTER", 0.3)
    WEBSITE_FETCH_TIMEOUT = _as_float("WEBSITE_FETCH_TIMEOUT", REQUEST_TIMEOUT)
    WEBSITE_FETCH_MIN_INTERVAL_SECONDS = _as_float(
        "WEBSITE_FETCH_MIN_INTERVAL_SECONDS", 0.0
    )
    PAGESPEED_TIMEOUT = _as_float("PAGESPEED_TIMEOUT", REQUEST_TIMEOUT)
    PAGESPEED_MIN_INTERVAL_SECONDS = _as_float("PAGESPEED_MIN_INTERVAL_SECONDS", 0.0)

    EXTERNAL_SERVICE_POLICIES = {
        "google_places": ServicePolicy(
            timeout=max(1.0, GOOGLE_PLACES_TIMEOUT),
            min_interval_seconds=max(0.0, GOOGLE_PLACES_MIN_INTERVAL_SECONDS),
        ),
        "website_fetch": ServicePolicy(
            timeout=max(1.0, WEBSITE_FETCH_TIMEOUT),
            min_interval_seconds=max(0.0, WEBSITE_FETCH_MIN_INTERVAL_SECONDS),
        ),
        "pagespeed": ServicePolicy(
            timeout=max(1.0, PAGESPEED_TIMEOUT),
            min_interval_seconds=max(0.0, PAGESPEED_MIN_INTERVAL_SECONDS),
        ),
    }

    @classmethod
    def is_development_mode(cls) -> bool:
        return cls.ENV in {"development", "dev"} or cls.DEBUG
