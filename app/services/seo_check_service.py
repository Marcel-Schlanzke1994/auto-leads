from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(slots=True)
class SeoSignals:
    site_title: str | None
    meta_description: str | None
    has_h1: bool
    has_cta: bool
    mobile_signals: bool


@dataclass(slots=True)
class CheckResult:
    category: str
    priority: str
    passed: bool
    message: str
    recommendation: str


def analyze_seo(html: str) -> SeoSignals:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = (meta.get("content") or "").strip() or None if meta else None
    page_text = soup.get_text(" ", strip=True).lower()
    return SeoSignals(
        site_title=title,
        meta_description=meta_description,
        has_h1=bool(soup.find("h1")),
        has_cta=any(
            k in page_text for k in ["kontakt", "anfrage", "termin", "angebot", "call"]
        ),
        mobile_signals=bool(
            soup.find("meta", attrs={"name": "viewport"}) or "@media" in html
        ),
    )


def run_all_seo_checks(
    html: str, checked_pages: list[str], domain: str
) -> list[CheckResult]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    checks = [
        check_title_present,
        check_title_length,
        check_meta_description_present,
        check_meta_description_length,
        check_single_h1,
        check_h2_present,
        check_word_count,
        check_canonical,
        check_indexability,
        check_lang_attribute,
        check_viewport,
        check_image_alt,
        check_internal_links,
        check_external_links,
        check_https_links,
        check_favicon,
        check_open_graph,
        check_twitter_cards,
        check_structured_data,
        check_contact_link,
        check_impressum_link,
        check_privacy_link,
        check_cta_presence,
        check_booking_hint,
        check_whatsapp_hint,
        check_social_hint,
        check_broken_links,
        check_redirects,
    ]
    return [c(soup, text, checked_pages, domain) for c in checks]


def _result(
    category: str, priority: str, passed: bool, msg: str, reco: str
) -> CheckResult:
    return CheckResult(
        category=category,
        priority=priority,
        passed=passed,
        message=msg,
        recommendation=reco,
    )


def check_title_present(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    ok = bool(soup.title and (soup.title.string or "").strip())
    return _result(
        "title_present",
        "high",
        ok,
        "Seitentitel vorhanden" if ok else "Seitentitel fehlt",
        "Unique <title> pro Seite setzen",
    )


def check_title_length(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    t = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    ok = 35 <= len(t) <= 65
    return _result(
        "title_length",
        "medium",
        ok,
        f"Title-Länge: {len(t)}",
        "Title auf 35-65 Zeichen optimieren",
    )


def check_meta_description_present(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    meta = soup.find("meta", attrs={"name": "description"})
    ok = bool(meta and (meta.get("content") or "").strip())
    return _result(
        "meta_description_present",
        "high",
        ok,
        "Meta-Description vorhanden" if ok else "Meta-Description fehlt",
        "Meta-Description ergänzen",
    )


def check_meta_description_length(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    meta = soup.find("meta", attrs={"name": "description"})
    content = (meta.get("content") or "").strip() if meta else ""
    ok = 70 <= len(content) <= 170
    return _result(
        "meta_description_length",
        "medium",
        ok,
        f"Description-Länge: {len(content)}",
        "Description auf 70-170 Zeichen optimieren",
    )


def check_single_h1(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    count = len(soup.find_all("h1"))
    return _result(
        "single_h1",
        "high",
        count == 1,
        f"H1-Anzahl: {count}",
        "Genau eine H1 verwenden",
    )


def check_h2_present(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    ok = bool(soup.find("h2"))
    return _result(
        "h2_present",
        "medium",
        ok,
        "H2-Struktur vorhanden" if ok else "H2 fehlt",
        "Abschnitte mit H2 strukturieren",
    )


def check_word_count(soup, text, checked_pages, domain):
    del soup, checked_pages, domain
    wc = len(text.split())
    return _result(
        "word_count",
        "medium",
        wc >= 250,
        f"Wörter: {wc}",
        "Mindestens ~250 relevante Wörter bereitstellen",
    )


def check_canonical(soup, text, checked_pages, domain):
    del text, checked_pages
    canonical = soup.find("link", attrs={"rel": "canonical"})
    href = canonical.get("href") if canonical else ""
    ok = bool(href and domain in href)
    return _result(
        "canonical",
        "medium",
        ok,
        "Canonical gesetzt" if ok else "Canonical fehlt/inkorrekt",
        "Canonical-URL auf Hauptdomain setzen",
    )


def check_indexability(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    robots = soup.find("meta", attrs={"name": "robots"})
    robots_content = (robots.get("content") or "").lower() if robots else ""
    ok = "noindex" not in robots_content
    return _result(
        "indexability",
        "high",
        ok,
        "Seite indexierbar" if ok else "noindex erkannt",
        "noindex entfernen, falls Seite ranken soll",
    )


def check_lang_attribute(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    html_tag = soup.find("html")
    ok = bool(html_tag and html_tag.get("lang"))
    return _result(
        "lang_attribute",
        "low",
        ok,
        "Lang-Attribut gesetzt" if ok else "Lang-Attribut fehlt",
        "<html lang='de'> oder passende Sprache setzen",
    )


def check_viewport(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    ok = bool(soup.find("meta", attrs={"name": "viewport"}))
    return _result(
        "viewport",
        "high",
        ok,
        "Viewport gesetzt" if ok else "Viewport fehlt",
        "Responsive Viewport-Meta-Tag setzen",
    )


def check_image_alt(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    images = soup.find_all("img")
    if not images:
        return _result("image_alt", "low", True, "Keine Bilder", "")
    with_alt = [img for img in images if (img.get("alt") or "").strip()]
    ok = len(with_alt) == len(images)
    return _result(
        "image_alt",
        "medium",
        ok,
        f"{len(with_alt)}/{len(images)} Bilder mit alt",
        "Alt-Texte für alle Bilder pflegen",
    )


def check_internal_links(soup, text, checked_pages, domain):
    del text, checked_pages
    internal = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if href.startswith("/") or domain in href:
            internal += 1
    return _result(
        "internal_links",
        "medium",
        internal >= 3,
        f"Interne Links: {internal}",
        "Interne Verlinkung ausbauen",
    )


def check_external_links(soup, text, checked_pages, domain):
    del text, checked_pages
    external = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if href.startswith("http") and domain not in href:
            external += 1
    return _result(
        "external_links",
        "low",
        external >= 1,
        f"Externe Links: {external}",
        "Mindestens eine vertrauenswürdige externe Referenz",
    )


def check_https_links(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    insecure = [
        a
        for a in soup.find_all("a", href=True)
        if a["href"].lower().startswith("http://")
    ]
    return _result(
        "https_links",
        "medium",
        not insecure,
        f"Unsichere Links: {len(insecure)}",
        "Alle Ressourcen/Links auf HTTPS umstellen",
    )


def check_favicon(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    icon = soup.find("link", attrs={"rel": lambda v: v and "icon" in str(v).lower()})
    return _result(
        "favicon",
        "low",
        bool(icon),
        "Favicon vorhanden" if icon else "Favicon fehlt",
        "Favicon integrieren",
    )


def check_open_graph(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    og_title = soup.find("meta", attrs={"property": "og:title"})
    return _result(
        "open_graph",
        "low",
        bool(og_title),
        "OpenGraph vorhanden" if og_title else "OpenGraph fehlt",
        "og:title/description/image ergänzen",
    )


def check_twitter_cards(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    tc = soup.find("meta", attrs={"name": "twitter:card"})
    return _result(
        "twitter_cards",
        "low",
        bool(tc),
        "Twitter Card vorhanden" if tc else "Twitter Card fehlt",
        "twitter:card Metadaten hinzufügen",
    )


def check_structured_data(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    return _result(
        "structured_data",
        "medium",
        bool(scripts),
        "Strukturierte Daten vorhanden" if scripts else "Keine strukturierten Daten",
        "JSON-LD (LocalBusiness) ergänzen",
    )


def check_contact_link(soup, text, checked_pages, domain):
    del text, domain
    hit = any(
        "kontakt" in link.lower() or "contact" in link.lower() for link in checked_pages
    )
    return _result(
        "contact_link",
        "high",
        hit,
        "Kontaktseite gefunden" if hit else "Keine Kontaktseite erkannt",
        "Kontaktseite intern verlinken",
    )


def check_impressum_link(soup, text, checked_pages, domain):
    del soup, text, domain
    hit = any(
        "impressum" in link.lower() or "legal" in link.lower() for link in checked_pages
    )
    return _result(
        "impressum_link",
        "high",
        hit,
        "Impressum gefunden" if hit else "Impressum-Link fehlt",
        "Impressum klar verlinken",
    )


def check_privacy_link(soup, text, checked_pages, domain):
    del soup, text, domain
    hit = any(
        "datenschutz" in link.lower() or "privacy" in link.lower()
        for link in checked_pages
    )
    return _result(
        "privacy_link",
        "high",
        hit,
        "Datenschutzseite gefunden" if hit else "Datenschutz-Link fehlt",
        "Datenschutzseite verlinken",
    )


def check_cta_presence(soup, text, checked_pages, domain):
    del soup, checked_pages, domain
    lowered = text.lower()
    hit = any(k in lowered for k in ["anfrage", "jetzt", "kontakt", "angebot", "call"])
    return _result(
        "cta_presence",
        "high",
        hit,
        "CTA vorhanden" if hit else "CTA fehlt",
        "Deutliche Call-to-Actions ergänzen",
    )


def check_booking_hint(soup, text, checked_pages, domain):
    del soup, checked_pages, domain
    lowered = text.lower()
    hit = any(
        k in lowered for k in ["book", "booking", "reservierung", "termin buchen"]
    )
    return _result(
        "booking_hint",
        "medium",
        hit,
        "Booking-Hinweis gefunden" if hit else "Kein Booking-Hinweis",
        "Online-Termin/Booking hervorheben",
    )


def check_whatsapp_hint(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    has_wa = bool(soup.find("a", href=lambda v: v and "wa.me" in v.lower()))
    return _result(
        "whatsapp_hint",
        "medium",
        has_wa,
        "WhatsApp-Link vorhanden" if has_wa else "Kein WhatsApp-Link",
        "WhatsApp-CTA ergänzen",
    )


def check_social_hint(soup, text, checked_pages, domain):
    del text, checked_pages, domain
    has_social = bool(
        soup.find(
            "a",
            href=lambda v: v
            and any(
                k in v.lower()
                for k in ["facebook.com", "instagram.com", "linkedin.com", "tiktok.com"]
            ),
        )
    )
    return _result(
        "social_hint",
        "low",
        has_social,
        "Social-Profil verlinkt" if has_social else "Keine Social-Links",
        "Wichtige Social-Profile verlinken",
    )


def check_broken_links(soup, text, checked_pages, domain):
    del soup, text, domain
    broken = [link for link in checked_pages if " 404" in link]
    return _result(
        "broken_links",
        "high",
        not broken,
        "Keine offensichtlichen Broken Links" if not broken else "Broken Links erkannt",
        "404-Ziele reparieren oder entfernen",
    )


def check_redirects(soup, text, checked_pages, domain):
    del soup, text, domain
    redirects = [link for link in checked_pages if "->" in link]
    return _result(
        "redirects",
        "low",
        len(redirects) <= 2,
        f"Weiterleitungen: {len(redirects)}",
        "Redirect-Ketten reduzieren",
    )
