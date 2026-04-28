"""Deprecated compatibility module.

Use `app.utils` instead.
"""

from __future__ import annotations

from app.utils import is_private_hostname, normalize_website_url, parse_float, parse_int

__all__ = ["normalize_website_url", "parse_float", "parse_int", "is_private_hostname"]
