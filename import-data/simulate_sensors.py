#!/usr/bin/env python3
"""Simulate realistic IoT data for UrbanPulse Coruna and send every N seconds."""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import random
import sys
import time
from typing import Dict, List

import requests

NGSI_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"

SENSORS: List[Dict[str, object]] = [
    {"id": "sensor-001", "name": "Avda. Finisterre", "lat": 43.3713, "lon": -8.4194, "zone_factor": 1.25, "air_bias": 1.15, "noise_bias": 1.10},
    {"id": "sensor-002", "name": "Ronda de Outeiro", "lat": 43.3687, "lon": -8.4071, "zone_factor": 1.20, "air_bias": 1.10, "noise_bias": 1.05},
    {"id": "sensor-003", "name": "Cuatro Caminos", "lat": 43.3698, "lon": -8.4089, "zone_factor": 1.30, "air_bias": 1.20, "noise_bias": 1.15},
    {"id": "sensor-004", "name": "Paseo Maritimo", "lat": 43.3714, "lon": -8.3967, "zone_factor": 0.75, "air_bias": 0.70, "noise_bias": 0.85},
    {"id": "sensor-005", "name": "Torre Hercules", "lat": 43.3858, "lon": -8.4066, "zone_factor": 0.85, "air_bias": 0.80, "noise_bias": 0.90},
    {"id": "sensor-006", "name": "Monte San Pedro", "lat": 43.3782, "lon": -8.4397, "zone_factor": 0.65, "air_bias": 0.60, "noise_bias": 0.75},
]


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


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def property_value(value: object) -> Dict[str, object]:
    return {"type": "Property", "value": value}


def relationship(target: str) -> Dict[str, object]:
    return {"type": "Relationship", "object": target}


def geo_property(lat: float, lon: float) -> Dict[str, object]:
    return {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [lon, lat]}}


def traffic_curve(hour_decimal: float) -> float:
    morning_peak = math.exp(-((hour_decimal - 8.5) ** 2) / 2.0)
    evening_peak = math.exp(-((hour_decimal - 18.5) ** 2) / 3.0)
    night_valley = 0.4 * math.exp(-((hour_decimal - 3.0) ** 2) / 5.0)
    baseline = 0.35
    return baseline + 0.9 * morning_peak + 0.8 * evening_peak - night_valley


def generate_metrics(sensor: Dict[str, object], ts: dt.datetime, rng: random.Random) -> Dict[str, float | bool]:
    hour_decimal = ts.hour + ts.minute / 60.0
    zone_factor = float(sensor["zone_factor"])
    air_bias = float(sensor["air_bias"])
    noise_bias = float(sensor["noise_bias"])

    traffic_factor = traffic_curve(hour_decimal)
    traffic = clamp(rng.gauss(250.0 * zone_factor + 1000.0 * traffic_factor * zone_factor, 60.0), 30.0, 2200.0)

    occupancy = clamp(12.0 + traffic * 0.03 + rng.gauss(0.0, 4.0), 5.0, 98.0)
    avg_speed = clamp(56.0 - occupancy * 0.35 + rng.gauss(0.0, 2.5), 8.0, 80.0)

    no2 = clamp(10.0 + 0.045 * traffic * air_bias + rng.gauss(0.0, 6.0), 10.0, 120.0)
    pm25 = clamp(6.0 + 0.018 * traffic * air_bias + rng.gauss(0.0, 3.0), 4.0, 55.0)
    o3 = clamp(65.0 - 0.22 * no2 + max(0.0, math.sin((hour_decimal - 6.0) / 24.0 * 2.0 * math.pi)) * 12.0 + rng.gauss(0.0, 4.5), 8.0, 130.0)
    co = clamp(0.25 + 0.0014 * traffic + rng.gauss(0.0, 0.05), 0.1, 4.5)

    laeq = clamp(40.0 + 0.016 * traffic * noise_bias + rng.gauss(0.0, 2.0), 40.0, 90.0)
    lamax = clamp(laeq + rng.uniform(4.0, 12.0), 45.0, 100.0)
    las = clamp(laeq - rng.uniform(2.0, 6.0), 35.0, 85.0)

    impact = clamp((traffic / 22.0) + (no2 * 0.45) + (laeq * 0.3), 10.0, 100.0)
    persisted = impact > 70.0 and traffic > 900.0

    return {
        "traffic": round(traffic, 2),
        "occupancy": round(occupancy, 2),
        "avg_speed": round(avg_speed, 2),
        "no2": round(no2, 2),
        "pm25": round(pm25, 2),
        "o3": round(o3, 2),
        "co": round(co, 3),
        "laeq": round(laeq, 2),
        "lamax": round(lamax, 2),
        "las": round(las, 2),
        "impact": round(impact, 2),
        "persisted": persisted,
    }


def send_iot_measure(iota_http_url: str, sensor_id: str, entity_suffix: str, payload: Dict[str, object], timeout: int) -> requests.Response:
    device_id = f"{sensor_id}-{entity_suffix}"
    url = f"{iota_http_url.rstrip('/')}/iot/json"
    return requests.post(url, params={"k": "urbanpulse", "i": device_id}, json=payload, timeout=timeout)


def upsert_orion(orion_url: str, entities: List[Dict[str, object]], timeout: int) -> None:
    url = f"{orion_url.rstrip('/')}/ngsi-ld/v1/entityOperations/upsert"
    resp = requests.post(
        url,
        params={"options": "update"},
        json=entities,
        headers={"Content-Type": "application/ld+json"},
        timeout=timeout,
    )
    resp.raise_for_status()


def build_entities(sensor: Dict[str, object], values: Dict[str, float | bool], ts: dt.datetime) -> List[Dict[str, object]]:
    sid = str(sensor["id"])
    lat = float(sensor["lat"])
    lon = float(sensor["lon"])
    device_id = f"urn:ngsi-ld:Device:coruna:{sid}"
    date_obs = ts.isoformat()

    traffic_id = f"urn:ngsi-ld:TrafficFlowObserved:coruna:{sid}"
    air_id = f"urn:ngsi-ld:AirQualityObserved:coruna:{sid}"
    noise_id = f"urn:ngsi-ld:NoiseLevelObserved:coruna:{sid}"
    impact_id = f"urn:ngsi-ld:TrafficEnvironmentImpact:coruna:{sid}"

    traffic_entity = {
        "id": traffic_id,
        "type": "TrafficFlowObserved",
        "dateObserved": property_value(date_obs),
        "intensity": property_value(values["traffic"]),
        "occupancy": property_value(values["occupancy"]),
        "averageSpeed": property_value(values["avg_speed"]),
        "location": geo_property(lat, lon),
        "measuredBy": relationship(device_id),
        "@context": [NGSI_CONTEXT],
    }

    air_entity = {
        "id": air_id,
        "type": "AirQualityObserved",
        "dateObserved": property_value(date_obs),
        "no2": property_value(values["no2"]),
        "pm25": property_value(values["pm25"]),
        "o3": property_value(values["o3"]),
        "co": property_value(values["co"]),
        "location": geo_property(lat, lon),
        "measuredBy": relationship(device_id),
        "@context": [NGSI_CONTEXT],
    }

    noise_entity = {
        "id": noise_id,
        "type": "NoiseLevelObserved",
        "dateObserved": property_value(date_obs),
        "dateObservedFrom": property_value(date_obs),
        "dateObservedTo": property_value(date_obs),
        "LAeq": property_value(values["laeq"]),
        "LAmax": property_value(values["lamax"]),
        "LAS": property_value(values["las"]),
        "location": geo_property(lat, lon),
        "measuredBy": relationship(device_id),
        "@context": [NGSI_CONTEXT],
    }

    impact_entity = {
        "id": impact_id,
        "type": "TrafficEnvironmentImpact",
        "dateObservedFrom": property_value(date_obs),
        "dateObservedTo": property_value(date_obs),
        "traffic": property_value(
            [
                {
                    "class": "all",
                    "intensity": values["traffic"],
                    "averageSpeed": values["avg_speed"],
                    "occupancy": values["occupancy"],
                }
            ]
        ),
        "impactScore": property_value(values["impact"]),
        "persistedOver2h": property_value(values["persisted"]),
        "location": geo_property(lat, lon),
        "refersTo": relationship(traffic_id),
        "@context": [NGSI_CONTEXT],
    }

    return [traffic_entity, air_entity, noise_entity, impact_entity]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate dynamic sensor values and push to IoT Agent + Orion-LD")
    parser.add_argument("--agent", choices=["json", "jsonld"], default="json")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--orion-url", default=os.getenv("ORION_BASE_URL", "http://localhost:1026"))
    parser.add_argument("--iota-http-json", default=f"http://localhost:{os.getenv('IOTA_HTTP_PORT', '7896')}")
    parser.add_argument("--iota-http-jsonld", default=f"http://localhost:{os.getenv('IOTA_HTTP_PORT_LD', '7897')}")
    return parser.parse_args()


def main() -> int:
    root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(os.path.abspath(root_env))
    args = parse_args()
    rng = random.Random(args.seed)

    iota_http_url = args.iota_http_json if args.agent == "json" else args.iota_http_jsonld
    end_at = time.time() + max(args.duration, args.interval)

    iot_success = 0
    iot_fail = 0

    while time.time() < end_at:
        ts = dt.datetime.now(dt.timezone.utc)
        batch_entities: List[Dict[str, object]] = []

        for sensor in SENSORS:
            values = generate_metrics(sensor, ts, rng)
            batch_entities.extend(build_entities(sensor, values, ts))
            sid = str(sensor["id"])

            iot_payloads = {
                "trafficflow": {
                    "intensity": values["traffic"],
                    "occupancy": values["occupancy"],
                    "averageSpeed": values["avg_speed"],
                },
                "airquality": {
                    "no2": values["no2"],
                    "pm25": values["pm25"],
                    "o3": values["o3"],
                    "co": values["co"],
                },
                "noiselevel": {
                    "LAeq": values["laeq"],
                    "LAmax": values["lamax"],
                    "LAS": values["las"],
                },
                "impact": {
                    "impactScore": values["impact"],
                    "persistedOver2h": values["persisted"],
                },
            }

            for suffix, payload in iot_payloads.items():
                try:
                    response = send_iot_measure(iota_http_url, sid, suffix, payload, args.timeout)
                    if response.ok:
                        iot_success += 1
                    else:
                        iot_fail += 1
                except requests.RequestException:
                    iot_fail += 1

        upsert_orion(args.orion_url, batch_entities, args.timeout)
        print(f"[TICK] {ts.isoformat()} entities={len(batch_entities)} iot_ok={iot_success} iot_fail={iot_fail}")
        time.sleep(args.interval)

    print(f"[DONE] iot_ok={iot_success} iot_fail={iot_fail}")
    return 0 if iot_success > 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"[ERROR] Request failure: {exc}", file=sys.stderr)
        raise SystemExit(1)
