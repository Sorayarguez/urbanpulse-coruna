#!/usr/bin/env python3
"""Seed static NGSI-LD entities for UrbanPulse Coruna and provision IoT Agent devices."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

import requests

NGSI_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"

SENSORS: List[Dict[str, object]] = [
    {"id": "sensor-001", "name": "Avda. Finisterre", "lat": 43.3713, "lon": -8.4194, "zone": "high_traffic"},
    {"id": "sensor-002", "name": "Ronda de Outeiro", "lat": 43.3687, "lon": -8.4071, "zone": "ring_road"},
    {"id": "sensor-003", "name": "Cuatro Caminos", "lat": 43.3698, "lon": -8.4089, "zone": "transport_hub"},
    {"id": "sensor-004", "name": "Paseo Maritimo", "lat": 43.3714, "lon": -8.3967, "zone": "coastal"},
    {"id": "sensor-005", "name": "Torre Hercules", "lat": 43.3858, "lon": -8.4066, "zone": "historic"},
    {"id": "sensor-006", "name": "Monte San Pedro", "lat": 43.3782, "lon": -8.4397, "zone": "green_zone"},
]

ENTITY_TYPES = [
    "TrafficFlowObserved",
    "AirQualityObserved",
    "NoiseLevelObserved",
    "TrafficEnvironmentImpact",
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


def geo_property(lat: float, lon: float) -> Dict[str, object]:
    return {
        "type": "GeoProperty",
        "value": {"type": "Point", "coordinates": [lon, lat]},
    }


def property_value(value: object) -> Dict[str, object]:
    return {"type": "Property", "value": value}


def relationship(target: str) -> Dict[str, object]:
    return {"type": "Relationship", "object": target}


def build_entities() -> List[Dict[str, object]]:
    entities: List[Dict[str, object]] = []
    model_id = "urn:ngsi-ld:DeviceModel:coruna:multisensor-v1"

    entities.append(
        {
            "id": model_id,
            "type": "DeviceModel",
            "name": property_value("UrbanPulse multisensor v1"),
            "manufacturerName": property_value("UrbanPulse Lab"),
            "brandName": property_value("UrbanPulse"),
            "modelName": property_value("multisensor-v1"),
            "category": property_value(["environmentalSensor"]),
            "supportedProtocol": property_value(["HTTP", "MQTT"]),
            "controlledProperty": property_value(["trafficFlow", "airQuality", "noiseLevel"]),
            "@context": [NGSI_CONTEXT],
        }
    )

    for sensor in SENSORS:
        sid = str(sensor["id"])
        lat = float(sensor["lat"])
        lon = float(sensor["lon"])
        name = str(sensor["name"])

        device_id = f"urn:ngsi-ld:Device:coruna:{sid}"
        traffic_id = f"urn:ngsi-ld:TrafficFlowObserved:coruna:{sid}"
        air_id = f"urn:ngsi-ld:AirQualityObserved:coruna:{sid}"
        noise_id = f"urn:ngsi-ld:NoiseLevelObserved:coruna:{sid}"
        impact_id = f"urn:ngsi-ld:TrafficEnvironmentImpact:coruna:{sid}"

        entities.append(
            {
                "id": device_id,
                "type": "Device",
                "name": property_value(f"{sid} {name}"),
                "category": property_value(["environmentalSensor"]),
                "controlledProperty": property_value(["trafficFlow", "airQuality", "noiseLevel"]),
                "deviceState": property_value("online"),
                "location": geo_property(lat, lon),
                "hasModel": relationship(model_id),
                "@context": [NGSI_CONTEXT],
            }
        )

        entities.extend(
            [
                {
                    "id": traffic_id,
                    "type": "TrafficFlowObserved",
                    "name": property_value(f"Traffic Flow {name}"),
                    "intensity": property_value(1),
                    "occupancy": property_value(1.0),
                    "averageSpeed": property_value(25.0),
                    "location": geo_property(lat, lon),
                    "measuredBy": relationship(device_id),
                    "@context": [NGSI_CONTEXT],
                },
                {
                    "id": air_id,
                    "type": "AirQualityObserved",
                    "name": property_value(f"Air Quality {name}"),
                    "no2": property_value(20.0),
                    "pm25": property_value(10.0),
                    "o3": property_value(50.0),
                    "co": property_value(0.5),
                    "location": geo_property(lat, lon),
                    "measuredBy": relationship(device_id),
                    "@context": [NGSI_CONTEXT],
                },
                {
                    "id": noise_id,
                    "type": "NoiseLevelObserved",
                    "name": property_value(f"Noise Level {name}"),
                    "LAeq": property_value(50.0),
                    "LAmax": property_value(58.0),
                    "LAS": property_value(46.0),
                    "location": geo_property(lat, lon),
                    "measuredBy": relationship(device_id),
                    "@context": [NGSI_CONTEXT],
                },
                {
                    "id": impact_id,
                    "type": "TrafficEnvironmentImpact",
                    "name": property_value(f"Traffic Impact {name}"),
                    "impactScore": property_value(30.0),
                    "persistedOver2h": property_value(False),
                    "location": geo_property(lat, lon),
                    "refersTo": relationship(traffic_id),
                    "@context": [NGSI_CONTEXT],
                },
            ]
        )

    return entities


def upsert_entities(orion_base_url: str, entities: List[Dict[str, object]], timeout: int) -> None:
    url = f"{orion_base_url.rstrip('/')}/ngsi-ld/v1/entityOperations/upsert"
    response = requests.post(
        url,
        params={"options": "update"},
        json=entities,
        headers={"Content-Type": "application/ld+json"},
        timeout=timeout,
    )
    response.raise_for_status()


def provision_iot_service(iota_north_url: str, orion_base_url: str, timeout: int) -> None:
    url = f"{iota_north_url.rstrip('/')}/iot/services"
    payload = {
        "services": [
            {
                "apikey": "urbanpulse",
                "cbroker": orion_base_url.rstrip("/"),
                "entity_type": "Thing",
                "resource": "/iot/json",
            }
        ]
    }
    headers = {"Content-Type": "application/json", "fiware-service": "urbanpulse", "fiware-servicepath": "/"}
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if response.status_code not in (201, 409):
        response.raise_for_status()


def build_device_payload() -> Dict[str, object]:
    devices = []
    for sensor in SENSORS:
        sid = str(sensor["id"])
        for entity_type in ENTITY_TYPES:
            lname = entity_type.lower().replace("observed", "").replace("trafficenvironmentimpact", "impact")
            devices.append(
                {
                    "device_id": f"{sid}-{lname}",
                    "entity_name": f"urn:ngsi-ld:{entity_type}:coruna:{sid}",
                    "entity_type": entity_type,
                    "protocol": "PDI-IoTA-JSON",
                    "transport": "HTTP",
                    "timezone": "Europe/Madrid",
                    "attributes": [
                        {"name": "intensity", "type": "Number", "object_id": "intensity"},
                        {"name": "occupancy", "type": "Number", "object_id": "occupancy"},
                        {"name": "averageSpeed", "type": "Number", "object_id": "averageSpeed"},
                        {"name": "no2", "type": "Number", "object_id": "no2"},
                        {"name": "pm25", "type": "Number", "object_id": "pm25"},
                        {"name": "o3", "type": "Number", "object_id": "o3"},
                        {"name": "co", "type": "Number", "object_id": "co"},
                        {"name": "LAeq", "type": "Number", "object_id": "LAeq"},
                        {"name": "LAmax", "type": "Number", "object_id": "LAmax"},
                        {"name": "LAS", "type": "Number", "object_id": "LAS"},
                        {"name": "impactScore", "type": "Number", "object_id": "impactScore"},
                        {"name": "persistedOver2h", "type": "Boolean", "object_id": "persistedOver2h"},
                    ],
                }
            )
    return {"devices": devices}


def provision_iot_devices(iota_north_url: str, timeout: int) -> None:
    url = f"{iota_north_url.rstrip('/')}/iot/devices"
    payload = build_device_payload()
    headers = {"Content-Type": "application/json", "fiware-service": "urbanpulse", "fiware-servicepath": "/"}
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if response.status_code not in (201, 409):
        response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed static NGSI-LD entities and IoT Agent provisioning")
    parser.add_argument("--orion-url", default=os.getenv("ORION_BASE_URL", "http://localhost:1026"))
    parser.add_argument("--iota-north-url", default=f"http://localhost:{os.getenv('IOTA_NORTH_PORT', '4041')}")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--skip-iot-provision", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(os.path.abspath(root_env))
    args = parse_args()

    entities = build_entities()
    if args.dry_run:
        print(json.dumps({"entities": entities}, indent=2))
        return 0

    upsert_entities(args.orion_url, entities, args.timeout)
    print(f"[OK] Upserted {len(entities)} static entities in Orion-LD")

    if not args.skip_iot_provision:
        provision_iot_service(args.iota_north_url, args.orion_url, args.timeout)
        provision_iot_devices(args.iota_north_url, args.timeout)
        print("[OK] IoT Agent service/devices provisioned")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"[ERROR] Request failure: {exc}", file=sys.stderr)
        raise SystemExit(1)
