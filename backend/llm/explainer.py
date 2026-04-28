from __future__ import annotations

from typing import Any, Dict, List

import requests

from backend.common import default_weather_context, summarize_series


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
        except requests.RequestException:
            return {"model": self.model, "text": self._fallback_text(sensor, current_state, history_summary, forecasts), "source": "fallback"}

    def _fallback_text(self, sensor: Dict[str, Any], current_state: Dict[str, Any], history_summary: Dict[str, Any], forecasts: List[Dict[str, Any]]) -> str:
        no2 = float(current_state.get("no2", 0.0))
        impact = float(current_state.get("impactScore", 0.0))
        wind_speed = float(current_state.get("wind_speed", default_weather_context(sensor["id"]) ["wind_speed"]))
        trend = history_summary.get("no2", {}).get("delta", 0.0) if isinstance(history_summary, dict) else 0.0
        first_forecast = forecasts[0] if forecasts else {}
        forecast_no2 = float(first_forecast.get("predictedNO2", 0.0)) if isinstance(first_forecast, dict) else 0.0
        return (
            f"En {sensor['name']} el NO2 actual es {no2:.1f} ug/m3 y el impacto estimado es {impact:.1f}. "
            f"La ventilacion es moderada con viento de {wind_speed:.1f} m/s, por lo que la dispersion puede ser limitada si el trafico se mantiene alto. "
            f"La serie reciente muestra una variacion de {trend:+.1f} ug/m3 en 6 horas y el primer horizonte previsto apunta a {forecast_no2:.1f} ug/m3. "
            "Si se confirma una tendencia ascendente, conviene anticipar medidas de gestion del trafico y comunicar recomendaciones preventivas."
        )


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
