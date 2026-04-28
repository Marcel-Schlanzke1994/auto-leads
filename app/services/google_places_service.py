from __future__ import annotations

import time
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
    all_types: list[str]
    address_components: list[dict]


@dataclass(slots=True)
class SearchBatch:
    place_ids: list[str]
    total_found_raw: int


class GooglePlacesClient:
    def __init__(self, api_key: str, timeout: float = 8.0):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.base = "https://places.googleapis.com/v1"

    def text_search_paginated(
        self, query: str, *, max_results: int, safety_page_limit: int = 60
    ) -> SearchBatch:
        url = f"{self.base}/places:searchText"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,nextPageToken",
            "Content-Type": "application/json",
        }
        all_ids: list[str] = []
        seen: set[str] = set()
        page_token: str | None = None
        pages = 0
        total_found_raw = 0
        while pages < safety_page_limit and len(all_ids) < max_results:
            payload = {"textQuery": query, "pageSize": 20}
            if page_token:
                payload["pageToken"] = page_token
            response = self.session.post(
                url, json=payload, headers=headers, timeout=self.timeout
            )
            if not response.ok:
                raise GooglePlacesError(f"Text Search failed ({response.status_code})")
            data = response.json() or {}
            places = data.get("places", []) or []
            total_found_raw += len(places)
            for item in places:
                place_id = item.get("id")
                if place_id and place_id not in seen:
                    seen.add(place_id)
                    all_ids.append(place_id)
                    if len(all_ids) >= max_results:
                        break
            pages += 1
            page_token = data.get("nextPageToken")
            if not page_token or not places:
                break
            time.sleep(2.1)
        return SearchBatch(
            place_ids=all_ids[:max_results], total_found_raw=total_found_raw
        )

    def place_details(self, place_id: str) -> PlaceSummary:
        fields = ",".join(
            [
                "id",
                "displayName",
                "formattedAddress",
                "addressComponents",
                "rating",
                "userRatingCount",
                "websiteUri",
                "internationalPhoneNumber",
                "primaryType",
                "types",
            ]
        )
        headers = {"X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": fields}
        response = self.session.get(
            f"{self.base}/places/{place_id}", headers=headers, timeout=self.timeout
        )
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
            primary_type=payload.get("primaryType"),
            all_types=payload.get("types") or [],
            address_components=payload.get("addressComponents") or [],
        )
