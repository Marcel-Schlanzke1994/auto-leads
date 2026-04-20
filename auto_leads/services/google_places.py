from __future__ import annotations

from dataclasses import dataclass

import requests


class GooglePlacesError(RuntimeError):
    pass


@dataclass(slots=True)
class PlaceSummary:
    place_id: str
    display_name: str
    formatted_address: str | None
    rating: float | None
    review_count: int | None
    website: str | None
    phone: str | None
    primary_type: str | None


class GooglePlacesClient:
    """Client for official Google Places API (New)."""

    def __init__(self, api_key: str, timeout: float = 8.0):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.base = "https://places.googleapis.com/v1"

    def text_search(self, query: str, max_results: int = 20) -> list[str]:
        url = f"{self.base}/places:searchText"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,nextPageToken",
            "Content-Type": "application/json",
        }
        payload = {"textQuery": query, "pageSize": min(max_results, 20)}
        response = self.session.post(
            url, json=payload, headers=headers, timeout=self.timeout
        )
        if not response.ok:
            raise GooglePlacesError(f"Text Search failed ({response.status_code})")
        data = response.json() or {}
        return [item.get("id") for item in data.get("places", []) if item.get("id")]

    def place_details(self, place_id: str) -> PlaceSummary:
        fields = ",".join(
            [
                "id",
                "displayName",
                "formattedAddress",
                "rating",
                "userRatingCount",
                "websiteUri",
                "internationalPhoneNumber",
                "primaryTypeDisplayName",
            ]
        )
        url = f"{self.base}/places/{place_id}"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": fields,
        }
        response = self.session.get(url, headers=headers, timeout=self.timeout)
        if not response.ok:
            raise GooglePlacesError(f"Place details failed ({response.status_code})")

        payload = response.json() or {}
        return PlaceSummary(
            place_id=payload.get("id", place_id),
            display_name=(payload.get("displayName") or {}).get("text") or "Unbekannt",
            formatted_address=payload.get("formattedAddress"),
            rating=payload.get("rating"),
            review_count=payload.get("userRatingCount"),
            website=payload.get("websiteUri"),
            phone=payload.get("internationalPhoneNumber"),
            primary_type=(payload.get("primaryTypeDisplayName") or {}).get("text"),
        )
