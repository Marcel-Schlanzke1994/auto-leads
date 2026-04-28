from app.extensions import db
from app.models import Lead
from app.services.duplicate_service import (
    is_duplicate,
    normalize_city,
    normalize_company_name,
    normalize_domain,
    normalize_email,
    normalize_phone,
)


def _lead(**kwargs):
    return Lead(
        company_name=kwargs.get("company_name", "Muster GmbH"),
        normalized_company_name=kwargs.get(
            "normalized_company_name", normalize_company_name("Muster GmbH")
        ),
        city=kwargs.get("city", "Köln"),
        city_normalized=kwargs.get("city_normalized", normalize_city("Köln")),
        source_query="q",
        website=kwargs.get("website", "https://www.firma.de"),
        domain=kwargs.get("domain", normalize_domain("https://www.firma.de")),
        phone=kwargs.get("phone", "+49 (221) 1234"),
        phone_normalized=kwargs.get(
            "phone_normalized", normalize_phone("+49 (221) 1234")
        ),
        email=kwargs.get("email", "Info@Firma.de"),
        email_normalized=kwargs.get(
            "email_normalized", normalize_email("Info@Firma.de")
        ),
        google_place_id=kwargs.get("google_place_id", "gp-1"),
    )


def test_duplicate_checks_all_match_paths(app):
    with app.app_context():
        db.session.add(_lead())
        db.session.commit()

        assert is_duplicate(
            place_id="gp-1",
            company_name="Andere",
            city="Berlin",
            website=None,
            phone=None,
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="Andere",
            city="Berlin",
            website="https://firma.de/kontakt",
            phone=None,
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="Muster AG",
            city="Berlin",
            website=None,
            phone=None,
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="Andere",
            city="Berlin",
            website=None,
            phone="00492211234",
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="Andere",
            city="Berlin",
            website=None,
            phone=None,
            email=" info@firma.de ",
        )


def test_duplicate_for_name_and_city_combo(app):
    with app.app_context():
        db.session.add(
            _lead(
                company_name="Dach Meister e.K.",
                normalized_company_name=normalize_company_name("Dach Meister e.K."),
                city="Bonn",
                city_normalized=normalize_city("Bonn"),
                website="https://other.de",
                domain="other.de",
                google_place_id="gp-2",
                email="a@other.de",
                email_normalized="a@other.de",
                phone="+491111",
                phone_normalized="+491111",
            )
        )
        db.session.commit()

        assert is_duplicate(
            place_id=None,
            company_name="Dach Meister GmbH",
            city="BONN",
            website="https://brandnew.de",
            phone="+49222",
            email="x@brandnew.de",
        )

        assert not is_duplicate(
            place_id=None,
            company_name="Neue Dachwelt GmbH",
            city="Köln",
            website="https://brandnew.de",
            phone="+49222",
            email="x@brandnew.de",
        )
