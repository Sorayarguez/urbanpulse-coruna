from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from backend.common import default_weather_context, summarize_series, unwrap_ngsi_value


logger = logging.getLogger(__name__)


class OllamaExplainer:
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def _build_prompt(self, sensor: Dict[str, Any], current_state: Dict[str, Any], history_summary: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> str:
        lines = [
            "Eres un analista urbano de UrbanPulse Coruña.",
            "Redacta una explicacion breve, tecnica pero clara, en espanol.",
            "Incluye causa probable, tendencia esperada y una recomendacion operativa si hay riesgo.",
            "No inventes datos que no esten en el contexto.",
            "",
            f"Sensor: {sensor['id']} ({sensor['name']})",
            f"Ubicacion: {sensor['lat']}, {sensor['lon']}",
            f"Estado actual: {current_state}",
            f"Resumen historico 6h: {history_summary}",
            f"Forecasts: {forecasts}",
        ]
        return "\n".join(lines)

    def explain(self, sensor: Dict[str, Any], current_state: Dict[str, Any], history_summary: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = self._build_prompt(sensor, current_state, history_summary, forecasts)
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2, "num_predict": 220}},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            text = payload.get("response") or payload.get("message", {}).get("content") or ""
            if not text.strip():
                text = self._fallback_text(sensor, current_state, history_summary, forecasts)
            return {"model": self.model, "text": text.strip(), "source": "ollama"}
        except requests.RequestException as exc:
            logger.warning("Ollama request failed for sensor %s: %s", sensor.get("id"), exc)
            return {"model": self.model, "text": self._fallback_text(sensor, current_state, history_summary, forecasts), "source": "fallback"}
        except Exception as exc:
            logger.exception("Unexpected Ollama error for sensor %s", sensor.get("id"))
            return {"model": self.model, "text": self._fallback_text(sensor, current_state, history_summary, forecasts), "source": "fallback"}

    def _fallback_text(self, sensor: Dict[str, Any], current_state: Dict[str, Any], history_summary: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> str:
        def scalar(value: Any, default: float = 0.0) -> float:
            raw = unwrap_ngsi_value(value)
            if isinstance(raw, dict) and "value" in raw:
                return scalar(raw.get("value"), default)
            if isinstance(raw, dict):
                return default
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default
        try:
            no2 = scalar(current_state.get("no2", 0.0))
            impact = scalar(current_state.get("impactScore", 0.0))
            wind_speed = scalar(current_state.get("weather", {}).get("wind_speed", default_weather_context(sensor["id"])["wind_speed"]))
            trend = history_summary.get("no2", {}).get("delta", 0.0) if isinstance(history_summary, dict) else 0.0
            first_forecast = forecasts[0] if forecasts else {}
            forecast_no2 = scalar(first_forecast.get("predictedNO2", 0.0)) if isinstance(first_forecast, dict) else 0.0
            traffic = scalar(current_state.get("traffic_intensity", 0.0))
            noise = scalar(current_state.get("noise_laeq", 0.0))
            return (
                f"El aumento de NO2 en {sensor['name']} se asocia al trafico actual, que marca {traffic:.0f} veh/h, "
                f"junto con un nivel de ruido de {noise:.1f} dB y un impacto ambiental de {impact:.1f}. "
                f"El viento ronda {wind_speed:.1f} m/s, por lo que la dispersion puede ser limitada. "
                f"La tendencia reciente del NO2 es de {trend:+.1f} ug/m3 en 6 horas y el primer horizonte previsto apunta a {forecast_no2:.1f} ug/m3. "
                "La medida operativa mas razonable es reforzar el control del trafico y vigilar la evolucion en las proximas horas."
            )
        except Exception:
            logger.exception("Fallback explanation formatting failed for sensor %s", sensor.get("id"))
            return (
                f"El aumento de NO2 en {sensor['name']} parece estar relacionado con el trafico y el impacto ambiental observado. "
                "Conviene vigilar la evolucion y reforzar medidas de control si la tendencia sigue al alza."
            )

    def build_local_explanation(self, sensor: Dict[str, Any], current_state: Dict[str, Any], history_summary: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "model": self.model,
            "text": self._fallback_text(sensor, current_state, history_summary, forecasts),
            "source": "fallback",
        }


def build_history_summary(history_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    no2_values: List[float] = []
    traffic_values: List[float] = []
    impact_values: List[float] = []
    for row in history_rows:
        entity_type = row.get("entity_type")
        payload = row.get("payload") or {}
        if entity_type == "AirQualityObserved" and payload.get("no2") is not None:
            no2_values.append(float(payload.get("no2", 0.0)))
        if entity_type == "TrafficFlowObserved" and payload.get("intensity") is not None:
            traffic_values.append(float(payload.get("intensity", 0.0)))
        if entity_type == "TrafficEnvironmentImpact" and payload.get("impactScore") is not None:
            impact_values.append(float(payload.get("impactScore", 0.0)))
    return {"no2": summarize_series(no2_values), "traffic": summarize_series(traffic_values), "impact": summarize_series(impact_values)}
