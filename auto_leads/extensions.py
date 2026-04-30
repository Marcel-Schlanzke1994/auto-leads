"""Deprecated compatibility module.

Use `app.extensions` instead.
"""

from __future__ import annotations

from app.extensions import csrf, db, limiter, migrate

__all__ = ["db", "migrate", "csrf", "limiter"]
