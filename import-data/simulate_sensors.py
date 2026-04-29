#!/usr/bin/env python3
"""Simulate realistic IoT data and update NGSI v2 entity attributes in Orion via PATCH."""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import random
import sys
import time
from typing import Any

import requests

SENSORS: list[dict[str, Any]] = [
    {"id": "sensor-001", "name": "Avda. Finisterre", "lat": 43.3713, "lon": -8.4194, "traffic_factor": 1.25, "air_factor": 1.15},
    {"id": "sensor-002", "name": "Ronda de Outeiro", "lat": 43.3687, "lon": -8.4071, "traffic_factor": 1.20, "air_factor": 1.10},
    {"id": "sensor-003", "name": "Cuatro Caminos", "lat": 43.3698, "lon": -8.4089, "traffic_factor": 1.30, "air_factor": 1.20},
    {"id": "sensor-004", "name": "Paseo Maritimo", "lat": 43.3714, "lon": -8.3967, "traffic_factor": 0.75, "air_factor": 0.70},
    {"id": "sensor-005", "name": "Torre Hercules", "lat": 43.3858, "lon": -8.4066, "traffic_factor": 0.85, "air_factor": 0.80},
    {"id": "sensor-006", "name": "Monte San Pedro", "lat": 43.3782, "lon": -8.4397, "traffic_factor": 0.65, "air_factor": 0.60},
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


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value between low and high."""
    return max(low, min(high, value))


def ngsi_v2_number(value: float | int) -> dict[str, Any]:
    """NGSI v2 Number attribute wrapper."""
    return {"type": "Number", "value": float(value)}


def ngsi_v2_text(value: str) -> dict[str, Any]:
    """NGSI v2 Text attribute wrapper."""
    return {"type": "Text", "value": value}


def ngsi_v2_bool(value: bool) -> dict[str, Any]:
    """NGSI v2 Boolean attribute wrapper."""
    return {"type": "Boolean", "value": value}


def traffic_pattern(hour: float) -> float:
    """Generate realistic traffic pattern (0-1) based on hour of day.
    
    Morning peak: 7-9h, Evening peak: 18-20h, Night valley: 22-6h
    """
    morning = 0.9 * math.exp(-((hour - 8.0) ** 2) / 2.0)
    evening = 0.8 * math.exp(-((hour - 19.0) ** 2) / 3.0)
    night_valley = 0.3 * math.exp(-((hour - 3.0) ** 2) / 5.0)
    baseline = 0.35
    result = baseline + morning + evening - night_valley
    return clamp(result, 0.1, 1.0)


def generate_sensor_data(sensor: dict[str, Any], ts: dt.datetime, rng: random.Random) -> dict[str, float | bool]:
    """Generate realistic correlated sensor values."""
    hour_decimal = ts.hour + ts.minute / 60.0
    traffic_factor = sensor["traffic_factor"]
    air_factor = sensor["air_factor"]
    
    # Traffic: keep the final value in the requested 50-200 veh/h range.
    traffic_pattern_value = traffic_pattern(hour_decimal)
    base_traffic = 50.0 * traffic_factor
    peak_traffic = 200.0 * traffic_factor
    traffic = clamp(
        base_traffic + traffic_pattern_value * (peak_traffic - base_traffic) + rng.gauss(0, 6),
        50.0,
        200.0
    )
    
    # Road occupancy (correlation: occupancy ↑ with traffic)
    occupancy = clamp(10.0 + traffic * 0.035 + rng.gauss(0, 1.5), 5.0, 95.0)
    
    # Average speed (inverse correlation: speed ↓ with occupancy)
    avg_speed = clamp(60.0 - occupancy * 0.4 + rng.gauss(0, 1.2), 10.0, 80.0)
    
    # NO2 strongly correlated with traffic
    no2 = clamp(20.0 + 0.04 * traffic * air_factor + rng.gauss(0, 1.5), 10.0, 80.0)
    
    # PM2.5 correlated with traffic but slower response
    pm25 = clamp(8.0 + 0.02 * traffic * air_factor + rng.gauss(0, 1.2), 5.0, 40.0)
    
    # O3 inverse correlation with NOx
    o3_base = 55.0 - 0.15 * no2
    o3_time = 10.0 * max(0, math.sin((hour_decimal - 6.0) / 24.0 * 2.0 * math.pi))
    o3 = clamp(o3_base + o3_time + rng.gauss(0, 3), 10.0, 100.0)
    
    # CO: trace amounts
    co = clamp(0.3 + 0.001 * traffic + rng.gauss(0, 0.03), 0.1, 2.0)
    
    # Noise Level strongly correlated with traffic
    laeq = clamp(45.0 + 0.015 * traffic * 1.1 + rng.gauss(0, 0.8), 40.0, 75.0)
    lamax = clamp(laeq + rng.uniform(5, 10), 45.0, 85.0)
    las = clamp(laeq - rng.uniform(2, 4), 38.0, 70.0)
    
    # Impact score: weighted combination
    impact = clamp((traffic / 3.0) + (no2 * 0.3) + (laeq * 0.2), 10.0, 100.0)
    persisted = impact > 70.0 and traffic > 150.0
    
    return {
        "intensity": round(traffic, 1),
        "occupancy": round(occupancy, 1),
        "averageSpeed": round(avg_speed, 1),
        "no2": round(no2, 2),
        "pm25": round(pm25, 2),
        "o3": round(o3, 2),
        "co": round(co, 3),
        "LAeq": round(laeq, 1),
        "LAmax": round(lamax, 1),
        "LAS": round(las, 1),
        "impactScore": round(impact, 1),
        "persistedOver2h": persisted,
    }


def patch_entity_attributes(orion_url: str, entity_id: str, entity_type: str, attributes: dict[str, Any]) -> bool:
    """Update NGSI v2 entity attributes using PATCH (only update, never create).
    
    Uses: PATCH /v2/entities/{entityId}/attrs
    Returns: True if successful, False otherwise
    """
    url = f"{orion_url.rstrip('/')}/v2/entities/{entity_id}/attrs"
    headers = {"Content-Type": "application/json"}
    params = {"type": entity_type}
    
    try:
        resp = requests.patch(url, params=params, json=attributes, headers=headers, timeout=10)
        
        if resp.status_code in (200, 204):  # 200 OK, 204 No Content
            return True
        else:
            print(f"[ERROR] PATCH {entity_id}: HTTP {resp.status_code}")
            print(f"        Response: {resp.text}")
            return False
            
    except requests.RequestException as e:
        print(f"[ERROR] PATCH {entity_id}: {e}")
        return False


def update_sensor_attributes(orion_url: str, sensor_id: str, values: dict[str, float | bool], ts: dt.datetime) -> tuple[int, int]:
    """Update attributes for all entity types for one sensor.
    
    Returns: (success_count, fail_count) for the 4 entities
    """
    success = 0
    fail = 0
    ts_iso = ts.isoformat() + "Z" if not ts.isoformat().endswith("Z") else ts.isoformat()
    
    # TrafficFlowObserved attributes
    traffic_id = f"urn:ngsi-ld:TrafficFlowObserved:coruna:{sensor_id}"
    traffic_attrs = {
        "intensity": ngsi_v2_number(values["intensity"]),
        "occupancy": ngsi_v2_number(values["occupancy"]),
        "averageSpeed": ngsi_v2_number(values["averageSpeed"]),
        "dateObserved": ngsi_v2_text(ts_iso),
    }
    if patch_entity_attributes(orion_url, traffic_id, "TrafficFlowObserved", traffic_attrs):
        success += 1
    else:
        fail += 1
    
    # AirQualityObserved attributes
    air_id = f"urn:ngsi-ld:AirQualityObserved:coruna:{sensor_id}"
    air_attrs = {
        "no2": ngsi_v2_number(values["no2"]),
        "pm25": ngsi_v2_number(values["pm25"]),
        "o3": ngsi_v2_number(values["o3"]),
        "co": ngsi_v2_number(values["co"]),
        "dateObserved": ngsi_v2_text(ts_iso),
    }
    if patch_entity_attributes(orion_url, air_id, "AirQualityObserved", air_attrs):
        success += 1
    else:
        fail += 1
    
    # NoiseLevelObserved attributes
    noise_id = f"urn:ngsi-ld:NoiseLevelObserved:coruna:{sensor_id}"
    noise_attrs = {
        "LAeq": ngsi_v2_number(values["LAeq"]),
        "LAmax": ngsi_v2_number(values["LAmax"]),
        "LAS": ngsi_v2_number(values["LAS"]),
        "dateObserved": ngsi_v2_text(ts_iso),
    }
    if patch_entity_attributes(orion_url, noise_id, "NoiseLevelObserved", noise_attrs):
        success += 1
    else:
        fail += 1
    
    # TrafficEnvironmentImpact attributes
    impact_id = f"urn:ngsi-ld:TrafficEnvironmentImpact:coruna:{sensor_id}"
    impact_attrs = {
        "impactScore": ngsi_v2_number(values["impactScore"]),
        "persistedOver2h": ngsi_v2_bool(values["persistedOver2h"]),
        "dateObserved": ngsi_v2_text(ts_iso),
    }
    if patch_entity_attributes(orion_url, impact_id, "TrafficEnvironmentImpact", impact_attrs):
        success += 1
    else:
        fail += 1

    print(f"Updated {sensor_id}: {values}")
    
    return success, fail


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate IoT sensor data and PATCH NGSI v2 entity attributes in Orion"
    )
    parser.add_argument(
        "--orion-url",
        default=os.getenv("ORION_BASE_URL", "http://localhost:1027"),
        help="Orion Context Broker base URL"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Update interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Total duration in seconds (default: 300)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    return parser.parse_args()


def main() -> int:
    """Main execution."""
    root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(os.path.abspath(root_env))
    args = parse_args()
    
    rng = random.Random(args.seed)
    
    print(f"[INFO] Using Orion URL: {args.orion_url}")
    print(f"[INFO] Method: PATCH /v2/entities/{{entityId}}/attrs (UPDATE ONLY, NO CREATE)")
    print(f"[INFO] Simulating {len(SENSORS)} sensors, interval={args.interval}s, duration={args.duration}s")
    print(f"[INFO] Each tick updates {len(SENSORS)} × 4 = {len(SENSORS) * 4} attributes")
    print("[INFO] Data ranges: traffic=50-200 veh/h, NO2 correlated, noise correlated\n")
    
    end_time = time.time() + args.duration
    tick_count = 0
    total_success = 0
    total_fail = 0
    
    try:
        while time.time() < end_time:
            tick_count += 1
            ts = dt.datetime.now(dt.timezone.utc)
            tick_success = 0
            tick_fail = 0
            
            print(f"\n[TICK {tick_count}] {ts.strftime('%H:%M:%S')} UTC")
            print("-" * 70)
            
            for sensor in SENSORS:
                values = generate_sensor_data(sensor, ts, rng)
                success, fail = update_sensor_attributes(args.orion_url, sensor["id"], values, ts)
                tick_success += success
                tick_fail += fail
            
            total_success += tick_success
            total_fail += tick_fail
            
            print("-" * 70)
            print(f"Tick summary: {tick_success} updated, {tick_fail} failed")
            if time.time() < end_time:
                time.sleep(args.interval)
        
        print(f"\n{'=' * 70}")
        print(f"[DONE] Simulation complete after {tick_count} ticks")
        print(f"[SUMMARY] Total success: {total_success} | Total failures: {total_fail}")
        print(f"{'=' * 70}")
        
        return 0 if total_fail == 0 else 1
        
    except KeyboardInterrupt:
        print(f"\n[INTERRUPTED] Simulation stopped after {tick_count} ticks")
        print(f"[PARTIAL] Processed: {total_success} success, {total_fail} failures")
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"[FATAL ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise SystemExit(1)
