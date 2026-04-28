from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Iterable, List, Optional

import requests

from backend.common import normalize_timestamp


class QuantumLeapClient:
    def __init__(self, crate_http_url: str, timeout_seconds: float = 15.0) -> None:
        self.crate_http_url = crate_http_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(self, stmt: str, args: Optional[List[Any]] = None) -> Dict[str, Any]:
        response = requests.post(
            f"{self.crate_http_url}/_sql",
            json={"stmt": stmt, "args": args or []},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def fetch_rows(
        self,
        sensor_id: str,
        hours: int = 24,
        entity_types: Optional[Iterable[str]] = None,
    ) -> List[Dict[str, Any]]:
        start = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
        stmt = (
            "SELECT entity_id, entity_type, sensor_id, ts, lat, lon, payload "
            "FROM urbanpulse_history "
            "WHERE sensor_id = ? AND ts >= ?"
        )
        args: List[Any] = [sensor_id, start.isoformat()]
        if entity_types:
            entity_types_list = list(entity_types)
            placeholders = ", ".join(["?"] * len(entity_types_list))
            stmt += f" AND entity_type IN ({placeholders})"
            args.extend(entity_types_list)
        stmt += " ORDER BY ts ASC"
        payload = self._request(stmt, args)
        rows = payload.get("rows", [])
        columns = [column[0] for column in payload.get("cols", [])]
        result: List[Dict[str, Any]] = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            row_dict["ts"] = normalize_timestamp(row_dict.get("ts"))
            result.append(row_dict)
        return result

    def fetch_latest_rows(self, sensor_id: str) -> List[Dict[str, Any]]:
        return self.fetch_rows(sensor_id=sensor_id, hours=6)
