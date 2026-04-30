"""Deprecated compatibility module.

Use `app.routes.api` instead.
"""

from __future__ import annotations

from app.routes.api import api_bp, start_search_job

__all__ = ["api_bp", "start_search_job"]
