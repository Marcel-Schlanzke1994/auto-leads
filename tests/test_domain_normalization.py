from app.services.duplicate_service import normalize_company_name, normalize_domain


def test_domain_normalization_handles_www_and_case():
    assert normalize_domain("HTTPS://WWW.Example.COM/path") == "example.com"


def test_domain_normalization_supports_idn_to_punycode():
    assert normalize_domain("https://MÜNICH.de") == "xn--mnich-kva.de"


def test_company_name_normalization_strips_legal_forms():
    assert normalize_company_name("  Muster GmbH & Co. KG ") == "muster co"
    assert normalize_company_name("Beispiel UG") == "beispiel"
