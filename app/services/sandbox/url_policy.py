from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from app.services.sandbox.exceptions import (
    PrivateNetworkBlockedError,
    SandboxPolicyError,
    UnsafeUrlError,
)

_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_SCHEMES = {"file", "ftp", "data", "javascript", "chrome", "ws", "wss"}


@dataclass(frozen=True, slots=True)
class ValidatedUrl:
    original_url: str
    normalized_url: str
    scheme: str
    hostname: str
    port: int


Resolver = Callable[[str], list[str]]


def _default_resolver(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise SandboxPolicyError(f"DNS resolution failed for host: {hostname}") from exc
    return [info[4][0] for info in infos]


def _is_blocked_ip(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate_resolved_ips(hostname: str, resolver: Resolver) -> None:
    resolved = resolver(hostname)
    if not resolved:
        raise SandboxPolicyError(
            f"DNS resolution returned no records for host: {hostname}"
        )
    for item in resolved:
        try:
            is_blocked = _is_blocked_ip(item)
        except ValueError as exc:
            raise SandboxPolicyError(
                f"Resolver returned invalid IP address: {item}"
            ) from exc
        if is_blocked:
            raise PrivateNetworkBlockedError(
                f"Host resolves to blocked private/internal IP: {item}"
            )


def validate_external_url(
    url: str,
    *,
    allow_localhost: bool = False,
    resolver: Resolver | None = None,
) -> ValidatedUrl:
    raw = (url or "").strip()
    if not raw:
        raise UnsafeUrlError("URL must not be empty")

    parsed = urlparse(raw)
    scheme = (parsed.scheme or "").lower()
    if not scheme:
        raise UnsafeUrlError("Relative URLs are not allowed")
    if scheme in _BLOCKED_SCHEMES or scheme not in _ALLOWED_SCHEMES:
        raise UnsafeUrlError(f"Scheme is not allowed: {scheme}")
    if not parsed.netloc or not parsed.hostname:
        raise UnsafeUrlError("URL must include an absolute hostname")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("Credentials in URL are not allowed")

    hostname = parsed.hostname.encode("idna").decode("ascii").strip(".").lower()
    if hostname == "localhost" and not allow_localhost:
        raise PrivateNetworkBlockedError("localhost is blocked")

    try:
        ip = ipaddress.ip_address(hostname)
        if _is_blocked_ip(str(ip)) and not (allow_localhost and ip.is_loopback):
            raise PrivateNetworkBlockedError(
                f"Direct private/internal IP targets are blocked: {ip}"
            )
    except ValueError:
        if hostname.endswith(".local") and not allow_localhost:
            raise PrivateNetworkBlockedError(".local hostnames are blocked")

    try:
        port = parsed.port or (443 if scheme == "https" else 80)
    except ValueError as exc:
        raise UnsafeUrlError("Invalid URL port") from exc

    if port <= 0 or port > 65535:
        raise UnsafeUrlError("URL port out of range")

    if not allow_localhost:
        dns_resolver = resolver or _default_resolver
        _validate_resolved_ips(hostname, dns_resolver)

    normalized = parsed._replace(
        scheme=scheme,
        netloc=f"{hostname}:{port}" if parsed.port else hostname,
        fragment="",
    ).geturl()

    return ValidatedUrl(
        original_url=url,
        normalized_url=normalized,
        scheme=scheme,
        hostname=hostname,
        port=port,
    )
