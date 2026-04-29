from __future__ import annotations

import datetime as dt
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


NGSI_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"

SENSORS: List[Dict[str, Any]] = [
    {"id": "sensor-001", "name": "Avda. Finisterre", "lat": 43.3713, "lon": -8.4194, "zone_factor": 1.25, "air_bias": 1.15, "noise_bias": 1.10},
    {"id": "sensor-002", "name": "Ronda de Outeiro", "lat": 43.3687, "lon": -8.4071, "zone_factor": 1.20, "air_bias": 1.10, "noise_bias": 1.05},
    {"id": "sensor-003", "name": "Cuatro Caminos", "lat": 43.3698, "lon": -8.4089, "zone_factor": 1.30, "air_bias": 1.20, "noise_bias": 1.15},
    {"id": "sensor-004", "name": "Paseo Maritimo", "lat": 43.3714, "lon": -8.3967, "zone_factor": 0.75, "air_bias": 0.70, "noise_bias": 0.85},
    {"id": "sensor-005", "name": "Torre Hercules", "lat": 43.3858, "lon": -8.4066, "zone_factor": 0.85, "air_bias": 0.80, "noise_bias": 0.90},
    {"id": "sensor-006", "name": "Monte San Pedro", "lat": 43.3782, "lon": -8.4397, "zone_factor": 0.65, "air_bias": 0.60, "noise_bias": 0.75},
]


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def env_list(name: str, default: Iterable[str]) -> List[str]:
    value = os.getenv(name)
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def property_value(value: object) -> Dict[str, object]:
    return {"type": "Property", "value": value}


def relationship(target: str) -> Dict[str, object]:
    return {"type": "Relationship", "object": target}


def geo_property(lat: float, lon: float) -> Dict[str, object]:
    return {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [lon, lat]}}


def unwrap_ngsi_value(value: Any) -> Any:
    if isinstance(value, dict) and value.get("type") == "Property":
        return value.get("value")
    if isinstance(value, dict) and value.get("type") == "Relationship":
        return value.get("object")
    if isinstance(value, dict) and value.get("type") == "GeoProperty":
        return value.get("value")
    if isinstance(value, dict) and value.get("type") in {"Number", "Text", "Boolean", "geo:json"}:
        return value.get("value")
    return value


def sensor_by_id(sensor_id: str) -> Dict[str, Any]:
    for sensor in SENSORS:
        if sensor["id"] == sensor_id:
            return sensor
    raise KeyError(sensor_id)


def sensor_entity_id(sensor_id: str, entity_type: str) -> str:
    return f"urn:ngsi-ld:{entity_type}:coruna:{sensor_id}"


def extract_sensor_id(entity_id: str) -> Optional[str]:
    parts = entity_id.split(":")
    if len(parts) < 5:
        return None
    return parts[-1]


def default_weather_context(sensor_id: str, when: Optional[dt.datetime] = None) -> Dict[str, float]:
    timestamp = when or dt.datetime.now(dt.timezone.utc)
    sensor = sensor_by_id(sensor_id)
    hour_decimal = timestamp.hour + timestamp.minute / 60.0
    seasonal = math.sin((timestamp.timetuple().tm_yday / 365.0) * 2.0 * math.pi)
    base_temp = 15.5 + 4.0 * seasonal - 0.35 * abs(hour_decimal - 14.0)
    wind_speed = 5.0 + 2.5 * math.cos((hour_decimal / 24.0) * 2.0 * math.pi) + (0.8 - sensor["zone_factor"]) * 1.6
    humidity = 66.0 + 8.0 * math.cos((hour_decimal - 5.0) / 24.0 * 2.0 * math.pi) - 3.0 * seasonal
    wind_direction = (225.0 + 12.0 * math.sin((hour_decimal - 3.0) / 24.0 * 2.0 * math.pi) + 18.0 * sensor["zone_factor"]) % 360.0
    return {
        "temperature": round(base_temp, 2),
        "wind_speed": round(max(0.5, wind_speed), 2),
        "humidity": round(min(98.0, max(32.0, humidity)), 2),
        "wind_direction": round(wind_direction, 2),
    }


def encode_wind_direction(wind_direction: float) -> Dict[str, float]:
    angle = math.radians(wind_direction)
    return {"wind_dir_sin": math.sin(angle), "wind_dir_cos": math.cos(angle)}


def normalize_timestamp(value: Any) -> Optional[dt.datetime]:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
    if isinstance(value, str):
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)
    return None


def summarize_series(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "last": 0.0, "delta": 0.0}
    first = values[0]
    last = values[-1]
    return {
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "avg": round(sum(values) / len(values), 2),
        "last": round(last, 2),
        "delta": round(last - first, 2),
    }


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
