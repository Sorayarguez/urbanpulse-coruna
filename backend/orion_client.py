from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import requests

from backend.common import env


class OrionClient:
    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/ld+json",
            "Content-Type": "application/ld+json",
            "Fiware-Service": env("FIWARE_SERVICE", "urbanpulse"),
            "Fiware-ServicePath": env("FIWARE_SERVICEPATH", "/"),
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout_seconds,
            headers={**self._headers(), **kwargs.pop("headers", {})},
            **kwargs,
        )
        response.raise_for_status()
        return response

    def list_entities(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        q: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if entity_type:
            params["type"] = entity_type
        if entity_id:
            params["id"] = entity_id
        if q:
            params["q"] = q
        response = self._request("GET", "/ngsi-ld/v1/entities", params=params)
        data = response.json()
        return data if isinstance(data, list) else [data]

    def list_entities_v2(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if entity_type:
            params["type"] = entity_type
        if entity_id:
            params["id"] = entity_id
        response = requests.get(
            f"{self.base_url}/v2/entities",
            timeout=self.timeout_seconds,
            params=params,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else [data]

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self._request("GET", f"/ngsi-ld/v1/entities/{entity_id}")
            return response.json()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise

    def upsert_entities(self, entities: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        response = self._request(
            "POST",
            "/ngsi-ld/v1/entityOperations/upsert",
            params={"options": "update"},
            json=list(entities),
        )
        if response.content:
            return response.json()
        return {"status": "ok"}

    def get_current_state(self) -> Dict[str, List[Dict[str, Any]]]:
        state: Dict[str, List[Dict[str, Any]]] = {}
        for entity_type in [
            "Device",
            "TrafficFlowObserved",
            "AirQualityObserved",
            "NoiseLevelObserved",
            "TrafficEnvironmentImpact",
            "TrafficEnvironmentImpactForecast",
            "ItemFlowObserved",
        ]:
            try:
                state[entity_type] = self.list_entities(entity_type=entity_type)
            except requests.RequestException:
                state[entity_type] = []
        return state
