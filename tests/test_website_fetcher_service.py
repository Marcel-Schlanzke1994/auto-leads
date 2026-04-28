from types import SimpleNamespace

import pytest

from app.services.website_fetcher_service import (
    WebsiteFetchSecurityError,
    fetch_website,
)


class DummyResponse:
    def __init__(
        self,
        url: str,
        status_code: int = 200,
        text: str = "ok",
        history: list[SimpleNamespace] | None = None,
    ) -> None:
        self.url = url
        self.status_code = status_code
        self.text = text
        self.history = history or []

    def raise_for_status(self) -> None:
        return None


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self.response = response

    def get(self, *args, **kwargs):
        return self.response


def test_fetch_website_blocks_private_redirect_target_in_history():
    response = DummyResponse(
        url="https://example.com/final",
        history=[
            SimpleNamespace(url="https://example.com", status_code=301),
            SimpleNamespace(url="http://127.0.0.1/admin", status_code=302),
        ],
    )

    with pytest.raises(WebsiteFetchSecurityError):
        fetch_website("example.com", session=DummySession(response))


def test_fetch_website_blocks_private_redirect_target_in_final_url():
    response = DummyResponse(
        url="http://localhost/private",
        history=[SimpleNamespace(url="https://example.com", status_code=301)],
    )

    with pytest.raises(WebsiteFetchSecurityError):
        fetch_website("example.com", session=DummySession(response))


def test_fetch_website_accepts_public_redirect_chain():
    response = DummyResponse(
        url="https://www.example.org/home",
        history=[
            SimpleNamespace(url="https://example.com", status_code=301),
            SimpleNamespace(url="https://www.example.org", status_code=302),
        ],
    )

    result = fetch_website("example.com", session=DummySession(response))

    assert result.url == "https://www.example.org/home"
    assert [hop.url for hop in result.redirect_history] == [
        "https://example.com",
        "https://www.example.org",
    ]
