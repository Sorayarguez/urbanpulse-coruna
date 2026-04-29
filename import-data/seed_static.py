#!/usr/bin/env python3
"""Seed static NGSI v2 entities for UrbanPulse Coruna."""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict

import requests

SENSORS: list[dict[str, Any]] = [
    {"id": "sensor-001", "name": "Avda. Finisterre", "lat": 43.3713, "lon": -8.4194},
    {"id": "sensor-002", "name": "Ronda de Outeiro", "lat": 43.3687, "lon": -8.4071},
    {"id": "sensor-003", "name": "Cuatro Caminos", "lat": 43.3698, "lon": -8.4089},
    {"id": "sensor-004", "name": "Paseo Maritimo", "lat": 43.3714, "lon": -8.3967},
    {"id": "sensor-005", "name": "Torre Hercules", "lat": 43.3858, "lon": -8.4066},
    {"id": "sensor-006", "name": "Monte San Pedro", "lat": 43.3782, "lon": -8.4397},
]


def load_dotenv(path: str) -> None:
    """Load .env file variables into os.environ."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def ngsi_v2_text(value: str) -> dict[str, Any]:
    """NGSI v2 Text attribute wrapper."""
    return {"type": "Text", "value": value}


def ngsi_v2_number(value: float | int) -> dict[str, Any]:
    """NGSI v2 Number attribute wrapper."""
    return {"type": "Number", "value": float(value) if isinstance(value, (int, float)) else float(value)}


def ngsi_v2_bool(value: bool) -> dict[str, Any]:
    """NGSI v2 Boolean attribute wrapper."""
    return {"type": "Boolean", "value": value}


def ngsi_v2_location(lat: float, lon: float) -> dict[str, Any]:
    """NGSI v2 geo:json location attribute."""
    return {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [float(lon), float(lat)]}
    }


def create_entities() -> list[dict[str, Any]]:
    """Create initial NGSI v2 measurement entities for all sensors."""
    entities: list[dict[str, Any]] = []
    
    for sensor in SENSORS:
        sid = sensor["id"]
        lat, lon = sensor["lat"], sensor["lon"]
        name = sensor["name"]
        
        # TrafficFlowObserved entity
        traffic_id = f"urn:ngsi-ld:TrafficFlowObserved:coruna:{sid}"
        entities.append({
            "id": traffic_id,
            "type": "TrafficFlowObserved",
            "location": ngsi_v2_location(lat, lon),
            "intensity": ngsi_v2_number(500),  # vehicles/hour
            "occupancy": ngsi_v2_number(25.0),  # percent
            "averageSpeed": ngsi_v2_number(45.0),  # km/h
            "name": ngsi_v2_text(f"Traffic Flow {name}"),
            "dateObserved": ngsi_v2_text("2026-04-28T10:00:00Z"),
        })
        
        # AirQualityObserved entity
        air_id = f"urn:ngsi-ld:AirQualityObserved:coruna:{sid}"
        entities.append({
            "id": air_id,
            "type": "AirQualityObserved",
            "location": ngsi_v2_location(lat, lon),
            "no2": ngsi_v2_number(35.0),  # µg/m³
            "pm25": ngsi_v2_number(15.0),  # µg/m³
            "o3": ngsi_v2_number(60.0),  # µg/m³
            "co": ngsi_v2_number(0.5),  # mg/m³
            "name": ngsi_v2_text(f"Air Quality {name}"),
            "dateObserved": ngsi_v2_text("2026-04-28T10:00:00Z"),
        })
        
        # NoiseLevelObserved entity
        noise_id = f"urn:ngsi-ld:NoiseLevelObserved:coruna:{sid}"
        entities.append({
            "id": noise_id,
            "type": "NoiseLevelObserved",
            "location": ngsi_v2_location(lat, lon),
            "LAeq": ngsi_v2_number(52.0),  # dB(A)
            "LAmax": ngsi_v2_number(65.0),  # dB(A)
            "LAS": ngsi_v2_number(48.0),  # dB(A)
            "name": ngsi_v2_text(f"Noise Level {name}"),
            "dateObserved": ngsi_v2_text("2026-04-28T10:00:00Z"),
        })
        
        # TrafficEnvironmentImpact entity
        impact_id = f"urn:ngsi-ld:TrafficEnvironmentImpact:coruna:{sid}"
        entities.append({
            "id": impact_id,
            "type": "TrafficEnvironmentImpact",
            "location": ngsi_v2_location(lat, lon),
            "impactScore": ngsi_v2_number(45.0),  # 0-100
            "persistedOver2h": ngsi_v2_bool(False),
            "name": ngsi_v2_text(f"Traffic Environment Impact {name}"),
            "dateObserved": ngsi_v2_text("2026-04-28T10:00:00Z"),
        })
    
    return entities


def upsert_entities_ngsi_v2(orion_url: str, entities: list[dict[str, Any]], max_retries: int = 3) -> tuple[int, int]:
    """Upsert entities to Orion Context Broker using NGSI v2 API.
    
    Returns: (success_count, fail_count)
    """
    success = 0
    fail = 0
    
    for entity in entities:
        entity_id = entity.get("id", "unknown")
        entity_type = entity.get("type", "unknown")
        
        # NGSI v2: POST to /v2/entities (not /v2/entities/{id})
        url = f"{orion_url.rstrip('/')}/v2/entities"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=entity, headers=headers, timeout=10)
                # 201 = Created, 409 = already exists (idempotent upsert)
                if resp.status_code in (201, 204, 409):
                    print(f"✓ Entity created: {entity_type} {entity_id}")
                    success += 1
                    break
                else:
                    if attempt == max_retries - 1:
                        print(f"✗ Failed to create {entity_id}: HTTP {resp.status_code} - {resp.text[:100]}")
                        fail += 1
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"✗ Failed to create {entity_id}: {e}")
                    fail += 1
                else:
                    time.sleep(1)
                    continue
    
    return success, fail


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Seed initial NGSI v2 entities in Orion Context Broker"
    )
    parser.add_argument(
        "--orion-url",
        default=os.getenv("ORION_BASE_URL", "http://localhost:1026"),
        help="Orion Context Broker base URL"
    )
    return parser.parse_args()


def main() -> int:
    """Main execution."""
    root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(os.path.abspath(root_env))
    args = parse_args()
    
    print(f"[INFO] Using Orion URL: {args.orion_url}")
    print(f"[INFO] Creating {len(SENSORS)} sensors × 4 entity types = {len(SENSORS) * 4} entities...")
    
    entities = create_entities()
    success, fail = upsert_entities_ngsi_v2(args.orion_url, entities)
    
    print(f"\n[SUMMARY] ✓ {success} created | ✗ {fail} failed")
    
    if fail == 0:
        print("[SUCCESS] All entities created successfully!")
        return 0
    else:
        print(f"[WARNING] {fail} entities failed to create")
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise SystemExit(1)
