from __future__ import annotations

from dataclasses import dataclass
from typing import List

from backend.common import env, env_float, env_list


@dataclass(frozen=True)
class BackendSettings:
    orion_base_url: str
    quantumleap_base_url: str
    crate_http_url: str
    ollama_base_url: str
    ollama_model: str
    fastapi_title: str
    cors_origins: List[str]
    request_timeout_seconds: float
    forecast_horizons: List[int]


def load_settings() -> BackendSettings:
    return BackendSettings(
        orion_base_url=env("ORION_BASE_URL", "http://localhost:1026"),
        quantumleap_base_url=env("QUANTUMLEAP_BASE_URL", "http://localhost:8668"),
        crate_http_url=env("CRATEDB_HTTP_URL", "http://localhost:4200"),
        ollama_base_url=env("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=env("OLLAMA_MODEL", "mistral"),
        fastapi_title=env("FASTAPI_TITLE", "UrbanPulse Backend"),
        cors_origins=env_list("CORS_ORIGINS", ["*"]),
        request_timeout_seconds=env_float("BACKEND_REQUEST_TIMEOUT", 15.0),
        forecast_horizons=[int(item) for item in env_list("FORECAST_HORIZONS", ["6", "12", "24"])]
    )
