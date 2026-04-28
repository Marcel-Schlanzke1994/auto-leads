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
from config import Config


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    if app.config.get("TESTING") and not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "test-secret-key"

    _validate_security_config(app)

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


def _validate_security_config(app: Flask) -> None:
    secret_key = str(app.config.get("SECRET_KEY") or "").strip()
    insecure_placeholder = "replace-with-a-long-random-secret"
    is_dev = bool(app.config.get("TESTING")) or Config.is_development_mode()
    if not is_dev and (not secret_key or secret_key == insecure_placeholder):
        raise RuntimeError(
            "SECRET_KEY muss in Produktion gesetzt sein und darf kein "
            "Default-/Placeholder-Wert sein."
        )
