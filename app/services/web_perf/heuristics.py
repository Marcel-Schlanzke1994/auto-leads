from __future__ import annotations

from bs4 import BeautifulSoup

from app.services.sandbox.limits import MAX_RESPONSE_BYTES


def evaluate_local_heuristics(html: str, headers: dict[str, str]) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")
    normalized_headers = {k.lower(): v for k, v in (headers or {}).items()}

    encoding = (normalized_headers.get("content-encoding") or "").lower()
    uses_compression = any(token in encoding for token in ["gzip", "br", "deflate"])
    cache_policy_present = any(
        normalized_headers.get(key)
        for key in ["cache-control", "etag", "last-modified"]
    )

    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    scripts = soup.find_all("script")
    stylesheets = soup.find_all(
        "link", attrs={"rel": lambda rel: rel and "stylesheet" in rel}
    )
    images = soup.find_all("img")

    blocking_scripts = [
        script
        for script in scripts
        if not script.has_attr("defer") and not script.has_attr("async")
    ]
    images_missing_dimensions = [
        img for img in images if not img.get("width") or not img.get("height")
    ]
    lazy_count = sum(
        1 for img in images if (img.get("loading") or "").lower() == "lazy"
    )

    body_bytes = len((html or "").encode("utf-8"))
    html_size_ratio = body_bytes / MAX_RESPONSE_BYTES if MAX_RESPONSE_BYTES else 0

    render_blocking_risk = "low"
    if len(blocking_scripts) >= 5 or len(stylesheets) >= 8:
        render_blocking_risk = "high"
    elif len(blocking_scripts) >= 2 or len(stylesheets) >= 4:
        render_blocking_risk = "medium"

    image_optimization_risk = "low"
    if images:
        missing_ratio = len(images_missing_dimensions) / len(images)
        if missing_ratio > 0.7:
            image_optimization_risk = "high"
        elif missing_ratio > 0.3:
            image_optimization_risk = "medium"

    mobile_risk = "low" if has_viewport else "high"
    if has_viewport and (len(blocking_scripts) >= 5 or html_size_ratio > 0.7):
        mobile_risk = "medium"

    return {
        "uses_compression": uses_compression,
        "cache_policy_present": cache_policy_present,
        "render_blocking_risk": render_blocking_risk,
        "image_optimization_risk": image_optimization_risk,
        "mobile_performance_risk": mobile_risk,
        "has_viewport": has_viewport,
        "html_body_bytes": body_bytes,
        "resource_counts": {
            "scripts": len(scripts),
            "stylesheets": len(stylesheets),
            "images": len(images),
            "blocking_scripts": len(blocking_scripts),
            "images_missing_dimensions": len(images_missing_dimensions),
            "lazy_images": lazy_count,
        },
    }
