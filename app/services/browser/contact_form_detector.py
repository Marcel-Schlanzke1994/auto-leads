from __future__ import annotations

from bs4 import BeautifulSoup

from app.services.browser.models import ContactFormField, ContactFormSummary


def detect_forms_from_html(html: str) -> list[ContactFormSummary]:
    soup = BeautifulSoup(html or "", "html.parser")
    forms: list[ContactFormSummary] = []
    for form in soup.find_all("form"):
        fields: list[ContactFormField] = []
        for el in form.find_all(["input", "textarea", "select"]):
            input_type = (el.get("type") or el.name or "text").lower()
            name = (el.get("name") or el.get("id") or "").strip()
            label = _label_for(soup, el)
            selector = _selector(el)
            classified = _classify_field(name=name, label=label, input_type=input_type)
            fields.append(
                ContactFormField(
                    name=name,
                    input_type=input_type,
                    label=label,
                    selector=selector,
                    classified_as=classified,
                )
            )

        has_submit = bool(
            form.find("button", attrs={"type": "submit"})
            or form.find("input", attrs={"type": "submit"})
            or form.find("button")
        )
        warnings = _warnings_for(fields=fields, form=form)
        forms.append(
            ContactFormSummary(
                action=form.get("action"),
                method=(form.get("method") or "get").lower(),
                fields=fields,
                has_submit_button=has_submit,
                confidence=_confidence(fields, has_submit),
                warnings=warnings,
            )
        )
    return forms


def _classify_field(name: str, label: str, input_type: str) -> str:
    text = f"{name} {label} {input_type}".lower()
    if any(k in text for k in ["email", "e-mail"]):
        return "email"
    if any(k in text for k in ["phone", "telefon", "mobile", "tel"]):
        return "phone"
    if any(k in text for k in ["message", "nachricht", "textarea", "comment"]):
        return "message"
    if any(k in text for k in ["firma", "company", "unternehmen"]):
        return "company"
    if any(k in text for k in ["subject", "betreff"]):
        return "subject"
    if any(k in text for k in ["consent", "privacy", "datenschutz", "agb", "terms"]):
        return "consent"
    if any(k in text for k in ["name", "vorname", "nachname", "fullname"]):
        return "name"
    return "unknown"


def _label_for(soup: BeautifulSoup, el) -> str:
    el_id = el.get("id")
    if el_id:
        lbl = soup.find("label", attrs={"for": el_id})
        if lbl:
            return lbl.get_text(" ", strip=True)
    parent = el.find_parent("label")
    if parent:
        return parent.get_text(" ", strip=True)
    return (el.get("placeholder") or "").strip()


def _selector(el) -> str:
    if el.get("id"):
        return f"#{el.get('id')}"
    if el.get("name"):
        return f"{el.name}[name='{el.get('name')}']"
    return el.name


def _warnings_for(fields: list[ContactFormField], form) -> list[str]:
    warnings: list[str] = []
    classes = {f.classified_as for f in fields}
    form_text = form.get_text(" ", strip=True).lower()
    if "captcha" in form_text or "g-recaptcha" in str(form).lower():
        warnings.append("captcha detected")
    if "consent" in classes:
        warnings.append("consent checkbox detected")
    if "message" not in classes:
        warnings.append("no message field")
    if "email" not in classes:
        warnings.append("no email field")
    if "unknown" in classes:
        warnings.append("required fields unknown")
    return warnings


def _confidence(fields: list[ContactFormField], has_submit: bool) -> float:
    score = 0.2 if has_submit else 0.0
    classes = {f.classified_as for f in fields}
    for key in ["name", "email", "message"]:
        if key in classes:
            score += 0.25
    if "phone" in classes or "company" in classes:
        score += 0.1
    return min(score, 1.0)
