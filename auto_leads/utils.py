from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlparse


def normalize_website_url(value: str | None) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    normalized = raw if "://" in raw else f"https://{raw}"
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return normalized


def parse_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    cleaned = re.sub(r"[^\d-]", "", str(value))
    try:
        return int(cleaned)
    except ValueError:
        return None


def is_private_hostname(hostname: str) -> bool:
    host = hostname.lower().strip(".")
    if host == "localhost" or host.endswith(".local"):
        return True

    try:
        ip = ipaddress.ip_address(host)
        return _is_private_ip(ip)
    except ValueError:
        pass

    try:
        addrinfos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return True

    for info in addrinfos:
        ip_text = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError:
            return True
        if _is_private_ip(ip):
            return True
    return False


def _is_private_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )
