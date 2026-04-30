from __future__ import annotations

from dataclasses import dataclass

import requests

from auto_leads.services.google_places import PlaceSummary


class FreePlacesError(RuntimeError):
    pass


@dataclass(slots=True)
class _OsmSummary:
    place_id: str
    display_name: str
    formatted_address: str | None
    primary_type: str | None


class OpenStreetMapPlacesClient:
    """Kostenfreier Places-Client via OpenStreetMap Nominatim."""

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.session = requests.Session()
        # Nominatim Usage Policy: expliziter User-Agent ist Pflicht.
        self.session.headers.update(
            {"User-Agent": "auto-leads/1.0 (+https://localhost)"}
        )
        self.base = "https://nominatim.openstreetmap.org"

    def text_search(self, query: str, max_results: int = 20) -> list[str]:
        url = f"{self.base}/search"
        params = {
            "q": query,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": min(max_results, 20),
        }
        response = self.session.get(url, params=params, timeout=self.timeout)
        if not response.ok:
            raise FreePlacesError(f"Nominatim search failed ({response.status_code})")

        data = response.json() or []
        ids: list[str] = []
        for item in data:
            osm_type = item.get("osm_type")
            osm_id = item.get("osm_id")
            if osm_type and osm_id:
                ids.append(f"osm:{osm_type}:{osm_id}")
        return ids

    def place_details(self, place_id: str) -> PlaceSummary:
        parsed = self._parse_place_id(place_id)
        osm_type, osm_id = parsed

        url = f"{self.base}/lookup"
        params = {
            "osm_ids": f"{osm_type[0].upper()}{osm_id}",
            "format": "jsonv2",
            "addressdetails": 1,
        }
        response = self.session.get(url, params=params, timeout=self.timeout)
        if not response.ok:
            raise FreePlacesError(f"Nominatim lookup failed ({response.status_code})")

        payload = response.json() or []
        if not payload:
            raise FreePlacesError("Nominatim lookup returned no result")

        item = payload[0]
        display_name = (
            item.get("name") or item.get("display_name") or "Unbekannt"
        ).strip()
        formatted_address = item.get("display_name")
        primary_type = item.get("type")

        return PlaceSummary(
            place_id=place_id,
            display_name=display_name,
            formatted_address=formatted_address,
            rating=None,
            review_count=None,
            website=None,
            phone=None,
            primary_type=primary_type,
        )

    @staticmethod
    def _parse_place_id(place_id: str) -> tuple[str, str]:
        parts = place_id.split(":")
        if len(parts) != 3 or parts[0] != "osm":
            raise FreePlacesError(f"Ungültige OSM place_id: {place_id}")
        return parts[1], parts[2]
