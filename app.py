#!/usr/bin/env python3
"""
Unified entrypoint for UrbanPulse Coruña.

Run `python3 app.py` to start a server at http://localhost:8000.
This module reuses the FastAPI app already defined in `backend/main.py`,
keeps existing API routes untouched, and serves the web frontend from `frontend/`.

The frontend now includes:
- Modular component architecture (Sidebar, Header, Map, SensorCard)
- Professional UI with light palette (beige, soft blues, soft accents)
- Search functionality for zones
- Navigation sidebar with main pages: Dashboard, Traffic, Air Quality, Noise, Forecasts, GreenRoute, EcoZones
"""
from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles

# Reuse the existing FastAPI app implemented in backend/main.py
from backend.main import app  # type: ignore


ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"

if FRONTEND_DIR.exists():
    # Serve the frontend at the site root so relative asset URLs keep working.
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    # Start Uvicorn with the existing FastAPI app. Bind to localhost:8000 as required.
    host = os.getenv("LISTEN_ADDR", "0.0.0.0")
    port = int(os.getenv("LISTEN_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
