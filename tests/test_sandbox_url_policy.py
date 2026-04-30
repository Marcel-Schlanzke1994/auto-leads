import pytest

from app.services.sandbox import PrivateNetworkBlockedError, UnsafeUrlError
from app.services.sandbox.url_policy import validate_external_url


def _public_resolver(_: str) -> list[str]:
    return ["93.184.216.34"]


def test_https_example_com_allowed() -> None:
    validated = validate_external_url("https://example.com", resolver=_public_resolver)
    assert validated.scheme == "https"


def test_http_example_com_allowed() -> None:
    validated = validate_external_url("http://example.com", resolver=_public_resolver)
    assert validated.scheme == "http"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "",
        "/relative/path",
        "https://user:pass@example.com",
    ],
)
def test_blocked_or_invalid_urls(url: str) -> None:
    with pytest.raises(UnsafeUrlError):
        validate_external_url(url, resolver=_public_resolver)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://127.0.0.1",
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://192.168.1.1",
        "http://[::1]",
    ],
)
def test_private_and_local_addresses_blocked(url: str) -> None:
    with pytest.raises(PrivateNetworkBlockedError):
        validate_external_url(url)


def test_fake_resolver_private_ip_blocked() -> None:
    with pytest.raises(PrivateNetworkBlockedError):
        validate_external_url("https://example.com", resolver=lambda _: ["10.1.2.3"])


def test_fake_resolver_public_ip_allowed() -> None:
    validated = validate_external_url("https://example.com", resolver=_public_resolver)
    assert validated.hostname == "example.com"
