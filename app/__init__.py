from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask

from auto_leads.extensions import csrf, db, limiter, migrate
from app.routes.dashboard import dashboard_bp
from app.routes.export import export_bp
from app.routes.jobs import jobs_bp
from app.routes.leads import leads_bp
from auto_leads.routes.api import api_bp
from auto_leads.routes.web import web_bp


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "replace-with-a-long-random-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///leads.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REQUEST_TIMEOUT=float(os.getenv("REQUEST_TIMEOUT", "8")),
        GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY", ""),
        PLACES_PROVIDER=os.getenv("PLACES_PROVIDER", "google_places").lower(),
        APP_HOST=os.getenv("APP_HOST", "127.0.0.1"),
        APP_PORT=int(os.getenv("APP_PORT", "5000")),
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    from app import models  # noqa: F401

    _configure_logging(app)
    return app


def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app.logger.info("Auto-Leads app initialized")
