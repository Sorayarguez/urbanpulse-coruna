#!/usr/bin/env python3
"""Insert 30 days of historical synthetic data directly into CrateDB."""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import random
import sys
from typing import Dict, List, Tuple

import pandas as pd
import requests

try:
    import geopandas as gpd
    from shapely.geometry import Point
except Exception:  # pragma: no cover
    gpd = None
    Point = None

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
    traffic = clamp(rng.gauss(250.0 * zone_factor + 1000.0 * traffic_factor * zone_factor, 70.0), 30.0, 2200.0)
    occupancy = clamp(12.0 + traffic * 0.03 + rng.gauss(0.0, 5.0), 5.0, 98.0)
    avg_speed = clamp(56.0 - occupancy * 0.35 + rng.gauss(0.0, 3.0), 8.0, 80.0)

    no2 = clamp(10.0 + 0.045 * traffic * air_bias + rng.gauss(0.0, 7.0), 10.0, 120.0)
    pm25 = clamp(6.0 + 0.018 * traffic * air_bias + rng.gauss(0.0, 3.2), 4.0, 55.0)
    o3 = clamp(65.0 - 0.22 * no2 + max(0.0, math.sin((hour_decimal - 6.0) / 24.0 * 2.0 * math.pi)) * 12.0 + rng.gauss(0.0, 5.0), 8.0, 130.0)
    laeq = clamp(40.0 + 0.016 * traffic * noise_bias + rng.gauss(0.0, 2.5), 40.0, 90.0)

    impact = clamp((traffic / 22.0) + (no2 * 0.45) + (laeq * 0.3), 10.0, 100.0)
    item_intensity = clamp(20.0 + traffic * 0.18 + rng.gauss(0.0, 15.0), 5.0, 1200.0)

    return {
        "traffic": round(traffic, 2),
        "occupancy": round(occupancy, 2),
        "avg_speed": round(avg_speed, 2),
        "item_intensity": round(item_intensity, 2),
        "no2": round(no2, 2),
        "pm25": round(pm25, 2),
        "o3": round(o3, 2),
        "laeq": round(laeq, 2),
        "impact": round(impact, 2),
    }


def sensor_frame() -> pd.DataFrame:
    frame = pd.DataFrame(SENSORS)
    if gpd is not None and Point is not None:
        geom = [Point(float(row["lon"]), float(row["lat"])) for _, row in frame.iterrows()]
        gpd.GeoDataFrame(frame, geometry=geom, crs="EPSG:4326")
    return frame


def create_table(crate_url: str, timeout: int) -> None:
    stmt = (
        "CREATE TABLE IF NOT EXISTS urbanpulse_history ("
        "entity_id TEXT,"
        "entity_type TEXT,"
        "sensor_id TEXT,"
        "ts TIMESTAMP WITH TIME ZONE,"
        "lat DOUBLE,"
        "lon DOUBLE,"
        "payload OBJECT(DYNAMIC),"
        "PRIMARY KEY (entity_id, ts)"
        ")"
    )
    response = requests.post(f"{crate_url.rstrip('/')}/_sql", json={"stmt": stmt}, timeout=timeout)
    response.raise_for_status()


def bulk_insert(crate_url: str, rows: List[Tuple[object, ...]], timeout: int) -> int:
    stmt = (
        "INSERT INTO urbanpulse_history (entity_id, entity_type, sensor_id, ts, lat, lon, payload) "
        "VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT (entity_id, ts) DO UPDATE SET payload = excluded.payload"
    )
    response = requests.post(
        f"{crate_url.rstrip('/')}/_sql",
        json={"stmt": stmt, "bulk_args": rows},
        timeout=timeout,
    )
    response.raise_for_status()
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed CrateDB with 30 days of synthetic historical data")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--freq-minutes", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--crate-url", default=f"http://localhost:{os.getenv('CRATE_HTTP_PORT', '4200')}")
    return parser.parse_args()


def main() -> int:
    root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(os.path.abspath(root_env))
    args = parse_args()

    rng = random.Random(args.seed)
    sensors = sensor_frame()
    end_ts = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
    start_ts = end_ts - dt.timedelta(days=args.days)
    timestamps = pd.date_range(start=start_ts, end=end_ts, freq=f"{args.freq_minutes}min", tz="UTC")

    create_table(args.crate_url, args.timeout)

    rows: List[Tuple[object, ...]] = []
    inserted = 0

    for ts in timestamps:
        py_ts = ts.to_pydatetime()
        for _, sensor in sensors.iterrows():
            sid = str(sensor["id"])
            lat = float(sensor["lat"])
            lon = float(sensor["lon"])
            metrics = generate_metrics(sensor.to_dict(), py_ts, rng)

            entities = [
                (
                    f"urn:ngsi-ld:TrafficFlowObserved:coruna:{sid}",
                    "TrafficFlowObserved",
                    sid,
                    py_ts.isoformat(),
                    lat,
                    lon,
                    {"intensity": metrics["traffic"], "occupancy": metrics["occupancy"], "averageSpeed": metrics["avg_speed"]},
                ),
                (
                    f"urn:ngsi-ld:ItemFlowObserved:coruna:{sid}",
                    "ItemFlowObserved",
                    sid,
                    py_ts.isoformat(),
                    lat,
                    lon,
                    {"intensity": metrics["item_intensity"], "occupancy": metrics["occupancy"], "congested": bool(metrics["traffic"] > 900)},
                ),
                (
                    f"urn:ngsi-ld:AirQualityObserved:coruna:{sid}",
                    "AirQualityObserved",
                    sid,
                    py_ts.isoformat(),
                    lat,
                    lon,
                    {"no2": metrics["no2"], "pm25": metrics["pm25"], "o3": metrics["o3"]},
                ),
                (
                    f"urn:ngsi-ld:NoiseLevelObserved:coruna:{sid}",
                    "NoiseLevelObserved",
                    sid,
                    py_ts.isoformat(),
                    lat,
                    lon,
                    {"LAeq": metrics["laeq"], "LAmax": metrics["laeq"] + 6.0, "LAS": metrics["laeq"] - 4.0},
                ),
                (
                    f"urn:ngsi-ld:TrafficEnvironmentImpact:coruna:{sid}",
                    "TrafficEnvironmentImpact",
                    sid,
                    py_ts.isoformat(),
                    lat,
                    lon,
                    {"impactScore": metrics["impact"], "persistedOver2h": bool(metrics["impact"] > 70)},
                ),
            ]
            rows.extend(entities)

            if len(rows) >= args.batch_size:
                inserted += bulk_insert(args.crate_url, rows, args.timeout)
                rows.clear()

    if rows:
        inserted += bulk_insert(args.crate_url, rows, args.timeout)

    print(
        f"[OK] Seeded CrateDB: days={args.days} freq={args.freq_minutes}min sensors={len(sensors)} rows={inserted}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"[ERROR] Request failure: {exc}", file=sys.stderr)
        raise SystemExit(1)
