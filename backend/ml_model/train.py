from __future__ import annotations

import datetime as dt
import math
import pickle
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from backend.common import (
    SENSORS,
    default_weather_context,
    encode_wind_direction,
    ensure_directory,
    normalize_timestamp,
    sensor_by_id,
)

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.multioutput import MultiOutputRegressor
    from sklearn.model_selection import train_test_split
except Exception:  # pragma: no cover
    RandomForestRegressor = None
    mean_absolute_error = None
    mean_squared_error = None
    MultiOutputRegressor = None
    train_test_split = None


FEATURE_COLUMNS = [
    "traffic_intensity",
    "traffic_occupancy",
    "traffic_avg_speed",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_dir_sin",
    "wind_dir_cos",
    "noise_laeq",
]

TARGET_COLUMNS = ["no2", "pm25", "impactScore"]
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
DEFAULT_ARTIFACT_PATH = ARTIFACT_DIR / "rf_forecaster.pkl"


def _hour_features(timestamp: dt.datetime) -> Dict[str, float]:
    hour = timestamp.hour + timestamp.minute / 60.0
    day_of_week = timestamp.weekday()
    return {
        "hour_sin": math.sin((hour / 24.0) * 2.0 * math.pi),
        "hour_cos": math.cos((hour / 24.0) * 2.0 * math.pi),
        "dow_sin": math.sin((day_of_week / 7.0) * 2.0 * math.pi),
        "dow_cos": math.cos((day_of_week / 7.0) * 2.0 * math.pi),
    }


def _traffic_heuristic(sensor_id: str, timestamp: dt.datetime) -> Dict[str, float]:
    sensor = sensor_by_id(sensor_id)
    hour = timestamp.hour + timestamp.minute / 60.0
    morning_peak = math.exp(-((hour - 8.5) ** 2) / 2.0)
    evening_peak = math.exp(-((hour - 18.5) ** 2) / 3.0)
    night_valley = 0.4 * math.exp(-((hour - 3.0) ** 2) / 5.0)
    traffic_factor = 0.35 + 0.9 * morning_peak + 0.8 * evening_peak - night_valley
    traffic = max(30.0, min(2200.0, 250.0 * sensor["zone_factor"] + 1000.0 * traffic_factor * sensor["zone_factor"]))
    occupancy = max(5.0, min(98.0, 12.0 + traffic * 0.03))
    avg_speed = max(8.0, min(80.0, 56.0 - occupancy * 0.35))
    return {"traffic_intensity": traffic, "traffic_occupancy": occupancy, "traffic_avg_speed": avg_speed}


def _synthetic_sample(sensor_id: str, timestamp: dt.datetime, rng: random.Random) -> Tuple[Dict[str, float], Dict[str, float]]:
    sensor = sensor_by_id(sensor_id)
    traffic = _traffic_heuristic(sensor_id, timestamp)
    weather = default_weather_context(sensor_id, timestamp)
    wind = encode_wind_direction(weather["wind_direction"])
    noise_laeq = max(40.0, min(90.0, 40.0 + 0.016 * traffic["traffic_intensity"] * sensor["noise_bias"]))
    no2 = max(10.0, min(120.0, 10.0 + 0.045 * traffic["traffic_intensity"] * sensor["air_bias"] + rng.gauss(0.0, 6.5)))
    pm25 = max(4.0, min(55.0, 6.0 + 0.018 * traffic["traffic_intensity"] * sensor["air_bias"] + rng.gauss(0.0, 3.0)))
    impact = max(10.0, min(100.0, (traffic["traffic_intensity"] / 22.0) + (no2 * 0.45) + (noise_laeq * 0.3)))
    features = {
        **traffic,
        **_hour_features(timestamp),
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        **wind,
        "noise_laeq": noise_laeq,
    }
    targets = {"no2": no2, "pm25": pm25, "impactScore": impact}
    return features, targets


def _load_rows_from_history(history_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for row in history_rows:
        sensor_id = row.get("sensor_id")
        ts = normalize_timestamp(row.get("ts"))
        if not sensor_id or ts is None:
            continue
        key = (sensor_id, ts.isoformat())
        bucket = grouped.setdefault(key, {"sensor_id": sensor_id, "ts": ts, "entities": {}})
        bucket["entities"][row.get("entity_type")] = row.get("payload") or {}
    return list(grouped.values())


def build_dataset(history_rows: Sequence[Dict[str, Any]]) -> Tuple[List[List[float]], List[List[float]], List[Dict[str, Any]]]:
    samples = _load_rows_from_history(history_rows)
    X: List[List[float]] = []
    y: List[List[float]] = []
    metadata: List[Dict[str, Any]] = []
    for sample in samples:
        entities = sample["entities"]
        traffic_entity = entities.get("TrafficFlowObserved") or {}
        air_entity = entities.get("AirQualityObserved") or {}
        noise_entity = entities.get("NoiseLevelObserved") or {}
        ts = sample["ts"]
        sensor_id = sample["sensor_id"]
        weather = default_weather_context(sensor_id, ts)
        wind = encode_wind_direction(weather["wind_direction"])
        features = {
            "traffic_intensity": float(traffic_entity.get("intensity", 0.0)),
            "traffic_occupancy": float(traffic_entity.get("occupancy", 0.0)),
            "traffic_avg_speed": float(traffic_entity.get("averageSpeed", 0.0)),
            **_hour_features(ts),
            "temperature": float(weather["temperature"]),
            "humidity": float(weather["humidity"]),
            "wind_speed": float(weather["wind_speed"]),
            **wind,
            "noise_laeq": float(noise_entity.get("LAeq", 0.0)),
        }
        target_no2 = float(air_entity.get("no2", 0.0))
        target_pm25 = float(air_entity.get("pm25", 0.0))
        target_impact = float(entities.get("TrafficEnvironmentImpact", {}).get("impactScore", 0.0))
        if target_no2 <= 0.0 and target_pm25 <= 0.0 and target_impact <= 0.0:
            continue
        X.append([features[column] for column in FEATURE_COLUMNS])
        y.append([target_no2, target_pm25, target_impact])
        metadata.append({"sensor_id": sensor_id, "ts": ts.isoformat()})
    return X, y, metadata


def generate_synthetic_history(days: int = 30, freq_minutes: int = 30, seed: int = 42) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    end_ts = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
    start_ts = end_ts - dt.timedelta(days=days)
    timestamps = []
    current = start_ts
    while current <= end_ts:
        timestamps.append(current)
        current += dt.timedelta(minutes=freq_minutes)
    rows: List[Dict[str, Any]] = []
    for ts in timestamps:
        for sensor in SENSORS:
            features, targets = _synthetic_sample(sensor["id"], ts, rng)
            rows.append({"entity_type": "TrafficFlowObserved", "sensor_id": sensor["id"], "ts": ts, "payload": {"intensity": features["traffic_intensity"], "occupancy": features["traffic_occupancy"], "averageSpeed": features["traffic_avg_speed"]}})
            rows.append({"entity_type": "NoiseLevelObserved", "sensor_id": sensor["id"], "ts": ts, "payload": {"LAeq": features["noise_laeq"]}})
            rows.append({"entity_type": "AirQualityObserved", "sensor_id": sensor["id"], "ts": ts, "payload": {"no2": targets["no2"], "pm25": targets["pm25"]}})
            rows.append({"entity_type": "TrafficEnvironmentImpact", "sensor_id": sensor["id"], "ts": ts, "payload": {"impactScore": targets["impactScore"]}})
    return rows


def _fit_random_forest(X: List[List[float]], y: List[List[float]]) -> Any:
    if RandomForestRegressor is None or MultiOutputRegressor is None or train_test_split is None:
        raise RuntimeError("scikit-learn is required to train the RandomForest forecaster")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = MultiOutputRegressor(RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions, multioutput="raw_values")
    mse = mean_squared_error(y_test, predictions, multioutput="raw_values")
    return model, {"mae": mae.tolist() if hasattr(mae, "tolist") else list(mae), "rmse": [math.sqrt(value) for value in (mse.tolist() if hasattr(mse, "tolist") else list(mse))]}


def train_model(history_rows: Optional[Sequence[Dict[str, Any]]] = None, artifact_path: Optional[Path] = None) -> Dict[str, Any]:
    rows = list(history_rows or [])
    if not rows:
        rows = generate_synthetic_history()
    X, y, metadata = build_dataset(rows)
    if not X:
        synthetic_rows = generate_synthetic_history()
        X, y, metadata = build_dataset(synthetic_rows)
    model, metrics = _fit_random_forest(X, y)
    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "metrics": metrics,
        "trained_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sample_count": len(X),
        "sensor_ids": sorted({item["sensor_id"] for item in metadata}),
    }
    path = artifact_path or DEFAULT_ARTIFACT_PATH
    ensure_directory(path.parent)
    with open(path, "wb") as file:
        pickle.dump(artifact, file)
    return artifact


def load_artifact(artifact_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    path = artifact_path or DEFAULT_ARTIFACT_PATH
    if not path.exists():
        return None
    with open(path, "rb") as file:
        return pickle.load(file)


def build_feature_vector(sensor_id: str, timestamp: dt.datetime, traffic: Dict[str, float], weather: Optional[Dict[str, float]] = None, noise_laeq: float = 50.0) -> List[float]:
    resolved_weather = weather or default_weather_context(sensor_id, timestamp)
    wind = encode_wind_direction(resolved_weather["wind_direction"])
    features = {
        "traffic_intensity": float(traffic.get("traffic_intensity", traffic.get("intensity", 0.0))),
        "traffic_occupancy": float(traffic.get("traffic_occupancy", traffic.get("occupancy", 0.0))),
        "traffic_avg_speed": float(traffic.get("traffic_avg_speed", traffic.get("averageSpeed", 0.0))),
        **_hour_features(timestamp),
        "temperature": float(resolved_weather["temperature"]),
        "humidity": float(resolved_weather["humidity"]),
        "wind_speed": float(resolved_weather["wind_speed"]),
        **wind,
        "noise_laeq": float(noise_laeq),
    }
    return [features[column] for column in FEATURE_COLUMNS]


def heuristic_prediction(sensor_id: str, timestamp: dt.datetime, traffic: Dict[str, float], weather: Optional[Dict[str, float]] = None, noise_laeq: float = 50.0) -> Dict[str, float]:
    resolved_weather = weather or default_weather_context(sensor_id, timestamp)
    traffic_intensity = float(traffic.get("traffic_intensity", traffic.get("intensity", 0.0)))
    no2 = max(10.0, min(120.0, 12.0 + 0.05 * traffic_intensity + max(0.0, 26.0 - resolved_weather["wind_speed"]) * 1.2 - (resolved_weather["humidity"] - 50.0) * 0.06))
    pm25 = max(4.0, min(55.0, 5.5 + 0.02 * traffic_intensity + max(0.0, 20.0 - resolved_weather["wind_speed"]) * 0.5))
    impact = max(10.0, min(100.0, (traffic_intensity / 24.0) + (no2 * 0.42) + (noise_laeq * 0.28)))
    return {"no2": round(no2, 2), "pm25": round(pm25, 2), "impactScore": round(impact, 2)}
