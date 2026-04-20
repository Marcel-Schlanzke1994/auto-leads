from __future__ import annotations

import csv
import io
import ipaddress
import os
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(120))
    city = db.Column(db.String(120))
    website = db.Column(db.String(500))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))

    google_rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    source = db.Column(db.String(100), default="manual", nullable=False)

    status = db.Column(db.String(30), default="new", nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    score_reasons = db.Column(db.Text, default="", nullable=False)

    site_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    has_h1 = db.Column(db.Boolean, default=False, nullable=False)
    has_cta = db.Column(db.Boolean, default=False, nullable=False)
    mobile_signals = db.Column(db.Boolean, default=False, nullable=False)
    has_contact_info = db.Column(db.Boolean, default=False, nullable=False)
    page_load_ms = db.Column(db.Integer)
    audit_notes = db.Column(db.Text, default="", nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "company_name": self.company_name,
            "industry": self.industry,
            "city": self.city,
            "website": self.website,
            "email": self.email,
            "phone": self.phone,
            "google_rating": self.google_rating,
            "review_count": self.review_count,
            "source": self.source,
            "status": self.status,
            "score": self.score,
            "score_reasons": self.score_reasons,
            "site_title": self.site_title,
            "meta_description": self.meta_description,
            "has_h1": self.has_h1,
            "has_cta": self.has_cta,
            "mobile_signals": self.mobile_signals,
            "has_contact_info": self.has_contact_info,
            "page_load_ms": self.page_load_ms,
            "audit_notes": self.audit_notes,
            "created_at": self.created_at.isoformat(),
        }


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///leads.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REQUEST_TIMEOUT=float(os.getenv("REQUEST_TIMEOUT", "6")),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    register_cli(app)
    return app


def calculate_lead_score(lead: Lead) -> tuple[int, list[str]]:
    score = 10
    reasons: list[str] = ["Basis-Score vergeben (+10)"]

    if lead.google_rating is not None and lead.google_rating < 4.2:
        score += 15
        reasons.append("Google-Rating unter 4.2 (+15)")

    if lead.review_count is not None and lead.review_count < 80:
        score += 10
        reasons.append("Weniger als 80 Bewertungen (+10)")

    if not lead.has_cta:
        score += 12
        reasons.append("Keine klare CTA erkannt (+12)")

    if not lead.has_contact_info:
        score += 10
        reasons.append("Kontaktinfos schlecht sichtbar (+10)")

    if not lead.mobile_signals:
        score += 8
        reasons.append("Kaum Mobile-Signale (+8)")

    if lead.page_load_ms and lead.page_load_ms > 2500:
        score += 10
        reasons.append("Langsame Ladezeit über 2.5s (+10)")

    if not lead.meta_description:
        score += 5
        reasons.append("Meta-Description fehlt (+5)")

    return min(score, 100), reasons


def audit_website(url: str, timeout: float) -> dict[str, Any]:
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Ungültige Website-URL (Host fehlt).")
    if _is_private_hostname(hostname):
        raise ValueError("Lokale/private Hosts sind für Audits nicht erlaubt.")

    started = datetime.now(UTC)
    response = requests.get(
        url, timeout=timeout, headers={"User-Agent": "auto-leads/1.0"}
    )
    response.raise_for_status()
    elapsed_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)

    html = response.text or ""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = None
    if meta_tag and meta_tag.get("content"):
        meta_description = str(meta_tag["content"]).strip()

    text = soup.get_text(" ", strip=True).lower()
    has_h1 = soup.find("h1") is not None

    cta_keywords = ("kontakt", "anfrage", "termin", "jetzt", "angebot")
    has_cta = any(keyword in text for keyword in cta_keywords)

    mobile_signals = any(
        [
            soup.find("meta", attrs={"name": "viewport"}) is not None,
            "@media" in html,
            "responsive" in text,
        ]
    )

    has_contact_info = bool(
        re.search(r"[\w.\-+]+@[\w\-]+\.[\w\-.]+", html)
        or re.search(r"\+?\d[\d\s/().-]{6,}\d", html)
    )

    notes = [
        f"URL: {url}",
        f"Status: {response.status_code}",
        f"Domain: {urlparse(url).netloc or 'unbekannt'}",
    ]

    return {
        "site_title": title,
        "meta_description": meta_description,
        "has_h1": has_h1,
        "has_cta": has_cta,
        "mobile_signals": mobile_signals,
        "has_contact_info": has_contact_info,
        "page_load_ms": elapsed_ms,
        "audit_notes": "\n".join(notes),
    }


def apply_audit_to_lead(lead: Lead, audit: dict[str, Any]) -> None:
    lead.site_title = audit.get("site_title")
    lead.meta_description = audit.get("meta_description")
    lead.has_h1 = bool(audit.get("has_h1"))
    lead.has_cta = bool(audit.get("has_cta"))
    lead.mobile_signals = bool(audit.get("mobile_signals"))
    lead.has_contact_info = bool(audit.get("has_contact_info"))
    lead.page_load_ms = audit.get("page_load_ms")
    lead.audit_notes = str(audit.get("audit_notes") or "")

    score, reasons = calculate_lead_score(lead)
    lead.score = score
    lead.score_reasons = "\n".join(reasons)


def build_email_template(lead: Lead) -> dict[str, str]:
    subject = f"Ideen für mehr Anfragen bei {lead.company_name}"
    body = (
        f"Hallo {lead.company_name}-Team,\n\n"
        "ich habe mir Ihre Website kurz angesehen und ein paar konkrete "
        "Optimierungsmöglichkeiten gefunden, die oft zu mehr Anfragen führen.\n"
        f"\nKurzer Kontext: Score {lead.score}/100\n"
        "- Schnelle Umsetzbarkeit in 7 Tagen\n"
        "- Fokus auf lokale Sichtbarkeit und Conversion\n\n"
        "Wenn Sie möchten, sende ich Ihnen eine kompakte Analyse als PDF.\n\n"
        "Beste Grüße"
    )
    return {"subject": subject, "body": body}


def register_routes(app: Flask) -> None:
    @app.route("/")
    def dashboard() -> str:
        leads = Lead.query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()
        stats = {
            "total": len(leads),
            "high_score": sum(1 for lead in leads if lead.score >= 50),
            "contacted": sum(1 for lead in leads if lead.status == "contacted"),
            "won": sum(1 for lead in leads if lead.status == "won"),
        }
        return render_template("dashboard.html", leads=leads, stats=stats)

    @app.route("/lead/new", methods=["GET", "POST"])
    def new_lead() -> str:
        if request.method == "POST":
            company_name = (request.form.get("company_name") or "").strip()
            if not company_name:
                flash("Firmenname ist erforderlich.", "error")
                return render_template("new_lead.html")

            lead = Lead(
                company_name=company_name,
                industry=(request.form.get("industry") or "").strip() or None,
                city=(request.form.get("city") or "").strip() or None,
                website=_normalize_website_url(request.form.get("website")),
                email=(request.form.get("email") or "").strip() or None,
                phone=(request.form.get("phone") or "").strip() or None,
                google_rating=_to_float(request.form.get("google_rating")),
                review_count=_to_int(request.form.get("review_count")),
                source=(request.form.get("source") or "manual").strip() or "manual",
            )

            if lead.website:
                try:
                    audit_result = audit_website(
                        lead.website, app.config["REQUEST_TIMEOUT"]
                    )
                    apply_audit_to_lead(lead, audit_result)
                except (requests.RequestException, ValueError) as exc:
                    _set_default_score(
                        lead, f"Website-Audit fehlgeschlagen: {exc.__class__.__name__}"
                    )
            else:
                _set_default_score(lead)

            db.session.add(lead)
            db.session.commit()
            flash("Lead wurde erfolgreich angelegt.", "success")
            return redirect(url_for("lead_detail", lead_id=lead.id))

        return render_template("new_lead.html")

    @app.route("/lead/<int:lead_id>")
    def lead_detail(lead_id: int) -> str:
        lead = db.session.get(Lead, lead_id)
        if not lead:
            flash("Lead nicht gefunden.", "error")
            return redirect(url_for("dashboard"))

        email_tpl = build_email_template(lead)
        return render_template("lead_detail.html", lead=lead, email_tpl=email_tpl)

    @app.route("/lead/<int:lead_id>/status", methods=["POST"])
    def update_status(lead_id: int):
        lead = db.session.get(Lead, lead_id)
        if not lead:
            flash("Lead nicht gefunden.", "error")
            return redirect(url_for("dashboard"))

        valid_statuses = {"new", "qualified", "contacted", "replied", "won", "lost"}
        new_status = (request.form.get("status") or "new").strip().lower()
        if new_status not in valid_statuses:
            flash("Ungültiger Status.", "error")
            return redirect(url_for("lead_detail", lead_id=lead.id))

        lead.status = new_status
        db.session.commit()
        flash("Status wurde aktualisiert.", "success")
        return redirect(url_for("lead_detail", lead_id=lead.id))

    @app.route("/lead/<int:lead_id>/rerun-audit", methods=["POST"])
    def rerun_audit(lead_id: int):
        lead = db.session.get(Lead, lead_id)
        if not lead:
            flash("Lead nicht gefunden.", "error")
            return redirect(url_for("dashboard"))

        if not lead.website:
            flash("Keine Website hinterlegt.", "error")
            return redirect(url_for("lead_detail", lead_id=lead.id))

        try:
            audit_result = audit_website(lead.website, app.config["REQUEST_TIMEOUT"])
            apply_audit_to_lead(lead, audit_result)
            db.session.commit()
            flash("Audit erfolgreich neu ausgeführt.", "success")
        except (requests.RequestException, ValueError) as exc:
            flash(f"Audit fehlgeschlagen: {exc}", "error")

        return redirect(url_for("lead_detail", lead_id=lead.id))

    @app.route("/import", methods=["GET", "POST"])
    def import_csv() -> str:
        if request.method == "POST":
            upload = request.files.get("file")
            if not upload or not upload.filename:
                flash("Bitte eine CSV-Datei auswählen.", "error")
                return render_template("import.html")

            raw_bytes = upload.read()
            try:
                decoded = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                flash("Datei muss UTF-8 codiert sein.", "error")
                return render_template("import.html")

            reader = csv.DictReader(io.StringIO(decoded))
            created = 0

            for row in reader:
                company_name = (row.get("company_name") or "").strip()
                if not company_name:
                    continue

                lead = Lead(
                    company_name=company_name,
                    industry=(row.get("industry") or "").strip() or None,
                    city=(row.get("city") or "").strip() or None,
                    website=_normalize_website_url(row.get("website")),
                    email=(row.get("email") or "").strip() or None,
                    phone=(row.get("phone") or "").strip() or None,
                    google_rating=_to_float(row.get("google_rating")),
                    review_count=_to_int(row.get("review_count")),
                    source=(row.get("source") or "csv").strip() or "csv",
                )

                if lead.website:
                    try:
                        audit_result = audit_website(
                            lead.website,
                            app.config["REQUEST_TIMEOUT"],
                        )
                        apply_audit_to_lead(lead, audit_result)
                    except (requests.RequestException, ValueError):
                        _set_default_score(lead)
                else:
                    _set_default_score(lead)

                db.session.add(lead)
                created += 1

            db.session.commit()
            flash(f"Import abgeschlossen. {created} Leads angelegt.", "success")
            return redirect(url_for("dashboard"))

        return render_template("import.html")

    @app.route("/api/leads")
    def api_leads():
        leads = Lead.query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()
        return jsonify([lead.to_dict() for lead in leads])

    @app.route("/api/leads/<int:lead_id>")
    def api_lead_detail(lead_id: int):
        lead = db.session.get(Lead, lead_id)
        if not lead:
            return jsonify({"error": "not found"}), 404
        return jsonify(lead.to_dict())


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed() -> None:
        sample_leads = [
            {
                "company_name": "Praxis BeispielDent",
                "industry": "Zahnarzt",
                "city": "Köln",
                "website": "https://example.com",
                "email": "kontakt@example.com",
                "google_rating": 4.1,
                "review_count": 53,
                "source": "seed",
            },
            {
                "company_name": "Muster Elektrotechnik",
                "industry": "Elektriker",
                "city": "Bielefeld",
                "website": "https://example.org",
                "email": "info@example.org",
                "google_rating": 3.8,
                "review_count": 29,
                "source": "seed",
            },
        ]

        for item in sample_leads:
            lead = Lead(**item)
            if lead.website:
                try:
                    audit_result = audit_website(
                        lead.website, app.config["REQUEST_TIMEOUT"]
                    )
                    apply_audit_to_lead(lead, audit_result)
                except (requests.RequestException, ValueError):
                    _set_default_score(lead)
            else:
                _set_default_score(lead)
            db.session.add(lead)

        db.session.commit()
        print("Beispiel-Leads angelegt.")


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        cleaned = re.sub(r"[^\d-]", "", str(value))
        return int(cleaned)
    except ValueError:
        return None


def _normalize_website_url(value: Any) -> str | None:
    raw = (str(value).strip() if value is not None else "").strip()
    if not raw:
        return None
    normalized = raw if "://" in raw else f"https://{raw}"
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return normalized


def _is_private_hostname(hostname: str) -> bool:
    lowered = hostname.lower()
    if lowered in {"localhost"}:
        return True
    try:
        ip = ipaddress.ip_address(lowered)
    except ValueError:
        return lowered.endswith(".local")
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
    )


def _set_default_score(lead: Lead, extra_reason: str | None = None) -> None:
    score, reasons = calculate_lead_score(lead)
    lead.score = score
    if extra_reason:
        reasons.append(extra_reason)
    lead.score_reasons = "\n".join(reasons)


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
