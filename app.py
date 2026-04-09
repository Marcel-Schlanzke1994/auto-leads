from __future__ import annotations

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
                    audit_result = audit_website(lead.website, app.config["REQUEST_TIMEOUT"])
                    apply_audit_to_lead(lead, audit_result)
                except Exception:
                    score, reasons = calculate_lead_score(lead)
                    lead.score = score
                    lead.score_reasons = "\n".join(reasons)
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


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host=host, port=port, debug=True)