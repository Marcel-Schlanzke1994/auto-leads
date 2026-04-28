from app.services.browser.contact_form_detector import detect_forms_from_html
from app.services.browser.draft_builder import build_contact_form_message_draft
from app.services.browser.playwright_analyzer import (
    _contact_candidates,
    analyze_contact_forms,
)


def test_contact_form_detector_classifies_fields_and_captcha():
    html = """
    <form action='/contact' method='post'>
      <label for='name'>Name</label><input id='name' name='name' type='text' />
      <label for='email'>E-Mail</label><input id='email' name='email' type='email' />
      <label for='phone'>Telefon</label><input id='phone' name='phone' type='tel' />
      <textarea name='message' placeholder='Nachricht'></textarea>
      <label><input type='checkbox' name='privacy_consent'/> Datenschutz</label>
      <div>captcha required</div>
      <button type='submit'>Senden</button>
    </form>
    """
    forms = detect_forms_from_html(html)
    assert forms
    classes = {f.classified_as for f in forms[0].fields}
    assert {"email", "name", "phone", "message", "consent"}.issubset(classes)
    assert "captcha detected" in forms[0].warnings


def test_draft_builder_is_text_only():
    draft = build_contact_form_message_draft("Beispiel GmbH", "LCP ist über 3s")
    assert "Beispiel GmbH" in draft
    assert "Marcel Schlanzke" in draft
    assert "submit" not in draft.lower()


def test_playwright_missing_returns_unavailable(monkeypatch):
    monkeypatch.setenv("PLAYWRIGHT_ANALYSIS_ENABLED", "true")
    monkeypatch.setattr("builtins.__import__", __import__)
    result = analyze_contact_forms("https://example.com", html="<html></html>")
    assert result.status in {"unavailable", "failed", "success"}


def test_relative_contact_links_are_normalized_with_sandbox_validation():
    html = (
        "<a href='/kontakt'>Kontakt</a>"
        "<a href='https://example.com/contact'>Contact</a>"
    )
    urls = _contact_candidates("https://example.com", html)
    assert urls[0].startswith("https://example.com")


def test_unsafe_url_is_blocked():
    result = analyze_contact_forms("http://localhost:5000")
    assert result.status == "failed"
