"""Deprecated compatibility module.

Use app blueprints in `app.routes.*` directly.
"""

from __future__ import annotations

from app.routes.web_compat import web_compat_bp as web_bp

__all__ = ["web_bp"]
