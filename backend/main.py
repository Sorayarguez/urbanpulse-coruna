from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.common import (
    SENSORS,
    default_weather_context,
    extract_sensor_id,
    load_dotenv,
    normalize_timestamp,
    sensor_by_id,
    summarize_series,
    unwrap_ngsi_value,
)
from backend.config import load_settings
from backend.llm.explainer import OllamaExplainer, build_history_summary
from backend.ml_model.predict import generate_forecasts_for_sensor, publish_forecasts
from backend.orion_client import OrionClient
from backend.quantumleap_client import QuantumLeapClient


load_dotenv(".env")
settings = load_settings()

app = FastAPI(title=settings.fastapi_title, version="0.1.0")

if settings.cors_origins == ["*"]:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
else:
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

orion_client = OrionClient(settings.orion_base_url, timeout_seconds=settings.request_timeout_seconds)
quantumleap_client = QuantumLeapClient(settings.crate_http_url, timeout_seconds=settings.request_timeout_seconds)
llm_explainer = OllamaExplainer(settings.ollama_base_url, settings.ollama_model, timeout_seconds=settings.request_timeout_seconds)


class ExplainRequest(BaseModel):
    sensor_id: str = Field(..., description="Sensor UrbanPulse de A Coruña")
    force_forecast_refresh: bool = Field(default=False)
    include_history_hours: int = Field(default=6, ge=1, le=168)


def _entity_sensor_id(entity: Dict[str, Any]) -> Optional[str]:
    entity_id = entity.get("id")
    if isinstance(entity_id, str):
        return extract_sensor_id(entity_id)
    return None


def _plain_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    plain: Dict[str, Any] = {"id": entity.get("id"), "type": entity.get("type")}
    for key, value in entity.items():
        if key in {"id", "type", "@context"}:
            continue
        plain[key] = unwrap_ngsi_value(value)
    plain["sensor_id"] = _entity_sensor_id(entity)
    return plain


def _current_sensor_state(sensor_id: str) -> Dict[str, Any]:
    current: Dict[str, Any] = {"sensor": sensor_by_id(sensor_id)}
    for entity_type in ["TrafficFlowObserved", "AirQualityObserved", "NoiseLevelObserved", "TrafficEnvironmentImpact", "TrafficEnvironmentImpactForecast", "Device"]:
        try:
            entities = orion_client.list_entities(entity_type=entity_type)
        except Exception:
            entities = []
        for entity in entities:
            if _entity_sensor_id(entity) == sensor_id:
                current[entity_type] = _plain_entity(entity)
                break
    current["weather"] = default_weather_context(sensor_id)
    if "TrafficFlowObserved" in current:
        current["traffic_intensity"] = current["TrafficFlowObserved"].get("intensity", 0.0)
        current["traffic_occupancy"] = current["TrafficFlowObserved"].get("occupancy", 0.0)
        current["traffic_avg_speed"] = current["TrafficFlowObserved"].get("averageSpeed", 0.0)
    if "AirQualityObserved" in current:
        current["no2"] = current["AirQualityObserved"].get("no2", 0.0)
        current["pm25"] = current["AirQualityObserved"].get("pm25", 0.0)
    if "NoiseLevelObserved" in current:
        current["noise_laeq"] = current["NoiseLevelObserved"].get("LAeq", 0.0)
    if "TrafficEnvironmentImpact" in current:
        current["impactScore"] = current["TrafficEnvironmentImpact"].get("impactScore", 0.0)
    return current


def _build_sensor_overview(sensor_id: str) -> Dict[str, Any]:
    state = _current_sensor_state(sensor_id)
    sensor = state["sensor"]
    alerts: List[Dict[str, Any]] = []
    no2 = float(state.get("no2", 0.0))
    impact = float(state.get("impactScore", 0.0))
    noise = float(state.get("noise_laeq", 0.0))
    if no2 > 40.0:
        alerts.append({"severity": "high", "type": "air_quality", "message": f"NO2 por encima de 40 ug/m3 en {sensor['name']}"})
    if impact > 70.0:
        alerts.append({"severity": "high", "type": "impact", "message": f"Impacto ambiental persistente en {sensor['name']}"})
    if noise > 65.0:
        alerts.append({"severity": "medium", "type": "noise", "message": f"Ruido elevado en {sensor['name']}"})
    return {"sensor": sensor, "state": state, "alerts": alerts}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sensors")
def get_sensors() -> List[Dict[str, Any]]:
    return [_build_sensor_overview(sensor["id"]) for sensor in SENSORS]


@app.get("/api/sensors/{sensor_id}/history")
def get_sensor_history(sensor_id: str, hours: int = Query(default=24, ge=1, le=168)) -> Dict[str, Any]:
    try:
        sensor = sensor_by_id(sensor_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Sensor no encontrado") from exc
    rows = quantumleap_client.fetch_rows(sensor_id=sensor_id, hours=hours)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row.get("entity_type", "unknown"), []).append(row)
    summary = build_history_summary(rows)
    return {"sensor": sensor, "hours": hours, "summary": summary, "series": grouped}


@app.get("/api/impact")
def get_impact(sensor_id: Optional[str] = None) -> List[Dict[str, Any]]:
    entities = orion_client.list_entities(entity_type="TrafficEnvironmentImpact")
    if sensor_id:
        entities = [entity for entity in entities if _entity_sensor_id(entity) == sensor_id]
    return [_plain_entity(entity) for entity in entities]


@app.get("/api/forecast")
def get_forecast(sensor_id: Optional[str] = None, refresh: bool = False) -> List[Dict[str, Any]]:
    forecasts: List[Dict[str, Any]] = []
    sensors = [sensor_by_id(sensor_id)] if sensor_id else SENSORS
    for sensor in sensors:
        current = _current_sensor_state(sensor["id"])
        current_traffic = {
            "traffic_intensity": float(current.get("traffic_intensity", 0.0)),
            "traffic_occupancy": float(current.get("traffic_occupancy", 0.0)),
            "traffic_avg_speed": float(current.get("traffic_avg_speed", 0.0)),
            "noise_laeq": float(current.get("noise_laeq", 50.0)),
        }
        impact_entity = current.get("TrafficEnvironmentImpact") or {}
        impact_id = impact_entity.get("id") if isinstance(impact_entity, dict) else None
        generated = generate_forecasts_for_sensor(
            sensor["id"],
            current_traffic,
            current_impact_id=impact_id,
            current_weather=current.get("weather"),
            horizons=settings.forecast_horizons,
        )
        forecasts.extend(generated)
    if refresh and forecasts:
        publish_forecasts(orion_client, forecasts)
    return forecasts


@app.get("/api/alerts")
def get_alerts(sensor_id: Optional[str] = None) -> List[Dict[str, Any]]:
    sensors = [sensor_by_id(sensor_id)] if sensor_id else SENSORS
    alerts: List[Dict[str, Any]] = []
    for sensor in sensors:
        overview = _build_sensor_overview(sensor["id"])
        for alert in overview["alerts"]:
            alerts.append({"sensor_id": sensor["id"], "sensor_name": sensor["name"], **alert})
    return alerts


@app.post("/api/explain")
def explain(request: ExplainRequest) -> Dict[str, Any]:
    try:
        sensor = sensor_by_id(request.sensor_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Sensor no encontrado") from exc
    current = _current_sensor_state(request.sensor_id)
    history_rows = quantumleap_client.fetch_rows(sensor_id=request.sensor_id, hours=request.include_history_hours)
    history_summary = build_history_summary(history_rows)
    forecasts = generate_forecasts_for_sensor(
        request.sensor_id,
        {
            "traffic_intensity": float(current.get("traffic_intensity", 0.0)),
            "traffic_occupancy": float(current.get("traffic_occupancy", 0.0)),
            "traffic_avg_speed": float(current.get("traffic_avg_speed", 0.0)),
            "noise_laeq": float(current.get("noise_laeq", 50.0)),
        },
        current_impact_id=(current.get("TrafficEnvironmentImpact") or {}).get("id") if isinstance(current.get("TrafficEnvironmentImpact"), dict) else None,
        current_weather=current.get("weather"),
        horizons=settings.forecast_horizons,
    )
    if request.force_forecast_refresh:
        publish_forecasts(orion_client, forecasts)
    explanation = llm_explainer.explain(sensor, current, history_summary, forecasts)
    return {"sensor": sensor, "history": history_summary, "forecasts": forecasts, "explanation": explanation}
