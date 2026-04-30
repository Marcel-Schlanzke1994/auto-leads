from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

# WICHTIG:
# .env muss VOR dem Import von Config geladen werden,
# damit GOOGLE_MAPS_API_KEY, FLASK_ENV, SECRET_KEY usw.
# korrekt übernommen werden.
load_dotenv()

from flask import Flask, flash, redirect, request, url_for  # noqa: E402

from app.extensions import csrf, db, limiter, migrate  # noqa: E402
from app.routes.dashboard import dashboard_bp  # noqa: E402
from app.routes.export import export_bp  # noqa: E402
from app.routes.jobs import jobs_bp  # noqa: E402
from app.routes.outreach import outreach_bp  # noqa: E402
from app.routes.leads import leads_bp  # noqa: E402
from app.routes.api import api_bp  # noqa: E402
from app.routes.web_compat import web_compat_bp  # noqa: E402
from config import Config  # noqa: E402


def create_app(test_config: dict | None = None) -> Flask:
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

    # API-Sicherheitsstrategie:
    # - CSRF wird für den API-Blueprint explizit ausgenommen
    # - Schreibende API-Endpoints nutzen stattdessen
    #   Token-Auth + striktere Limits + Input-Validierung
    app.config.setdefault("API_REQUIRE_CSRF", False)
    app.config.setdefault("API_AUTH_HEADER", "X-API-Key")
    app.config.setdefault("API_AUTH_TOKEN", "")

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(outreach_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(web_compat_bp)

    if not app.config.get("API_REQUIRE_CSRF", False):
        csrf.exempt(api_bp)

    from app import models  # noqa: F401

    _configure_logging(app)
    _register_error_handlers(app)
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
            "SECRET_KEY muss in Produktion gesetzt sein "
            "und darf kein Default-/Placeholder-Wert sein."
        )


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(429)
    def handle_rate_limit(_error):  # noqa: ANN001
        if request.path.startswith("/api/"):
            return {"error": "Zu viele Anfragen. Bitte später erneut versuchen."}, 429

        flash(
            (
                "Zu viele Anfragen in kurzer Zeit. "
                "Bitte warte einen Moment und versuche es erneut."
            ),
            "error",
        )
        return redirect(request.referrer or url_for("leads.leads_list"))
