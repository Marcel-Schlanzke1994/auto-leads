from __future__ import annotations

import time
from dataclasses import dataclass
import random

import requests


class GooglePlacesError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        endpoint: str,
        attempt: int,
        status_code: int | None = None,
        retryable: bool | None = None,
        cause: str | None = None,
    ):
        self.endpoint = endpoint
        self.attempt = attempt
        self.status_code = status_code
        self.retryable = retryable
        self.cause = cause
        details = (
            f"endpoint={endpoint}, attempt={attempt}, status_code={status_code}, "
            f"retryable={retryable}, cause={cause or 'n/a'}"
        )
        super().__init__(f"{message} ({details})")


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
    def __init__(
        self,
        api_key: str,
        timeout: float = 8.0,
        min_interval_seconds: float = 2.1,
        retry_max_attempts: int = 4,
        retry_backoff_base: float = 0.5,
        retry_max_delay: float = 8.0,
        retry_jitter: float = 0.3,
    ):
        self.api_key = api_key
        self.timeout = timeout
        self.min_interval_seconds = min_interval_seconds
        self.retry_max_attempts = max(1, int(retry_max_attempts))
        self.retry_backoff_base = max(0.0, float(retry_backoff_base))
        self.retry_max_delay = max(0.0, float(retry_max_delay))
        self.retry_jitter = max(0.0, float(retry_jitter))
        self.session = requests.Session()
        self.base = "https://places.googleapis.com/v1"

    def _retry_delay(self, attempt: int) -> float:
        exponential_delay = self.retry_backoff_base * (2 ** max(0, attempt - 1))
        jitter = random.uniform(0.0, self.retry_jitter)
        return min(self.retry_max_delay, exponential_delay + jitter)

    def _request_with_retry(
        self, method: str, endpoint: str, **request_kwargs: object
    ) -> requests.Response:
        retryable_status_codes = {429}

        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                response = self.session.request(
                    method=method, timeout=self.timeout, **request_kwargs
                )
            except requests.RequestException as exc:
                if attempt >= self.retry_max_attempts:
                    raise GooglePlacesError(
                        "Google Places request failed after network retries",
                        endpoint=endpoint,
                        attempt=attempt,
                        retryable=True,
                        cause=str(exc),
                    ) from exc
                time.sleep(self._retry_delay(attempt))
                continue

            status_code = response.status_code
            if response.ok:
                return response

            is_server_error = 500 <= status_code <= 599
            is_retryable_status = (
                status_code in retryable_status_codes or is_server_error
            )
            is_permanent_client_error = 400 <= status_code <= 499 and status_code != 429

            if is_permanent_client_error:
                raise GooglePlacesError(
                    "Google Places request aborted due to permanent client error",
                    endpoint=endpoint,
                    attempt=attempt,
                    status_code=status_code,
                    retryable=False,
                    cause=response.text[:300] or None,
                )

            if is_retryable_status and attempt < self.retry_max_attempts:
                time.sleep(self._retry_delay(attempt))
                continue

            raise GooglePlacesError(
                "Google Places request failed after retries",
                endpoint=endpoint,
                attempt=attempt,
                status_code=status_code,
                retryable=is_retryable_status,
                cause=response.text[:300] or None,
            )

        raise GooglePlacesError(
            "Google Places request failed without response",
            endpoint=endpoint,
            attempt=self.retry_max_attempts,
            retryable=True,
        )

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
            response = self._request_with_retry(
                method="POST",
                endpoint="/places:searchText",
                url=url,
                json=payload,
                headers=headers,
            )
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
            time.sleep(self.min_interval_seconds)
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
        response = self._request_with_retry(
            method="GET",
            endpoint=f"/places/{place_id}",
            url=f"{self.base}/places/{place_id}",
            headers=headers,
        )
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
