from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from backend.common import (
    NGSI_CONTEXT,
    default_weather_context,
    geo_property,
    property_value,
    relationship,
    sensor_by_id,
    sensor_entity_id,
)
from backend.ml_model.train import DEFAULT_ARTIFACT_PATH, build_feature_vector, heuristic_prediction, load_artifact


DEFAULT_HORIZONS = (6, 12, 24)


def _predict_targets(sensor_id: str, timestamp: dt.datetime, traffic: Dict[str, float], weather: Optional[Dict[str, float]] = None, noise_laeq: float = 50.0, artifact_path: Optional[Path] = None) -> Dict[str, float]:
    artifact = load_artifact(artifact_path or DEFAULT_ARTIFACT_PATH)
    if artifact is None:
        return heuristic_prediction(sensor_id, timestamp, traffic, weather=weather, noise_laeq=noise_laeq)
    model = artifact["model"]
    feature_vector = build_feature_vector(sensor_id, timestamp, traffic, weather=weather, noise_laeq=noise_laeq)
    prediction = model.predict([feature_vector])[0]
    if hasattr(prediction, "tolist"):
        prediction = prediction.tolist()
    if not isinstance(prediction, list):
        prediction = list(prediction)
    return {"no2": round(float(prediction[0]), 2), "pm25": round(float(prediction[1]), 2), "impactScore": round(float(prediction[2]), 2)}


def _confidence_bounds(predictions: Dict[str, float], horizon: int) -> Dict[str, float]:
    spread = max(4.0, horizon * 0.9)
    return {"confidenceLow": round(max(0.0, predictions["no2"] - spread), 2), "confidenceHigh": round(predictions["no2"] + spread, 2)}


def build_forecast_entity(sensor_id: str, horizon_hours: int, predictions: Dict[str, float], issued_at: dt.datetime, base_impact_id: Optional[str] = None) -> Dict[str, Any]:
    sensor = sensor_by_id(sensor_id)
    valid_from = issued_at
    valid_to = issued_at + dt.timedelta(hours=horizon_hours)
    forecast_id = sensor_entity_id(sensor_id, f"TrafficEnvironmentImpactForecast:{issued_at:%Y%m%dT%H%M%S}:{horizon_hours}h")
    base_impact = base_impact_id or sensor_entity_id(sensor_id, "TrafficEnvironmentImpact")
    bounds = _confidence_bounds(predictions, horizon_hours)
    return {
        "id": forecast_id,
        "type": "TrafficEnvironmentImpactForecast",
        "name": f"Forecast impacto ambiental {sensor['name']} +{horizon_hours}h",
        "description": "Prediccion ML para NO2, PM2.5 e impacto ambiental",
        "dataProvider": "UrbanPulse Coruna ML",
        "location": geo_property(float(sensor["lat"]), float(sensor["lon"])),
        "dateIssued": property_value(issued_at.isoformat()),
        "validFrom": property_value(valid_from.isoformat()),
        "validTo": property_value(valid_to.isoformat()),
        "horizon": property_value(horizon_hours),
        "predictedNO2": property_value(predictions["no2"]),
        "predictedPM25": property_value(predictions["pm25"]),
        "predictedImpactScore": property_value(predictions["impactScore"]),
        "confidenceLow": property_value(bounds["confidenceLow"]),
        "confidenceHigh": property_value(bounds["confidenceHigh"]),
        "basedOn": relationship(base_impact),
        "@context": [NGSI_CONTEXT],
    }


def generate_forecasts_for_sensor(
    sensor_id: str,
    current_traffic: Dict[str, float],
    current_impact_id: Optional[str] = None,
    current_weather: Optional[Dict[str, float]] = None,
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    issued_at: Optional[dt.datetime] = None,
    artifact_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    timestamp = issued_at or dt.datetime.now(dt.timezone.utc)
    weather = current_weather or default_weather_context(sensor_id, timestamp)
    forecasts: List[Dict[str, Any]] = []
    for horizon in horizons:
        future_ts = timestamp + dt.timedelta(hours=horizon)
        future_traffic = dict(current_traffic)
        future_traffic["traffic_intensity"] = float(current_traffic.get("traffic_intensity", current_traffic.get("intensity", 0.0))) * (1.0 + min(0.12, horizon * 0.01))
        future_traffic["traffic_avg_speed"] = float(current_traffic.get("traffic_avg_speed", current_traffic.get("averageSpeed", 0.0))) * (1.0 - min(0.15, horizon * 0.004))
        targets = _predict_targets(sensor_id, future_ts, future_traffic, weather=weather, noise_laeq=float(current_traffic.get("noise_laeq", 50.0)), artifact_path=artifact_path)
        forecasts.append(build_forecast_entity(sensor_id, horizon, targets, timestamp, base_impact_id=current_impact_id))
    return forecasts


def publish_forecasts(orion_client: Any, forecasts: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    return orion_client.upsert_entities(list(forecasts))
