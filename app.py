#!/usr/bin/env python3
"""
Unified entrypoint for UrbanPulse Coruña.
Run `python3 app.py` to start a server at http://localhost:8000
This reuses the FastAPI `app` defined in `backend/main.py` and mounts
the `frontend/` directory as static files. It does not duplicate backend logic.
"""
from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Reuse the existing FastAPI app implemented in backend/main.py
from backend.main import app  # type: ignore


ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"

if FRONTEND_DIR.exists():
    # Serve frontend assets under /static
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def _root() -> FileResponse | dict:
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Frontend not found. Backend API available under /api"}


if __name__ == "__main__":
    # Start Uvicorn with the existing FastAPI app. Bind to localhost:8000 as required.
    uvicorn.run(app, host="127.0.0.1", port=8000)
