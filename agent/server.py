"""FastAPI application factory and uvicorn entry point.

Binds ONLY to 127.0.0.1:5001.
CORS: allow localhost and GitHub Pages origins.
All routers under /api/v1 prefix.
"""

import asyncio
import sys
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.config import APP_NAME, APP_VERSION, CORS_ORIGINS, HOST, PORT
from agent.routers import device, flash, status, wifi, images
from agent.services.image_manager import download_missing_images_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    print(f"[{APP_NAME}] Starting up...", flush=True)

    # Start background image download task
    asyncio.create_task(download_missing_images_task())

    yield

    print(f"[{APP_NAME}] Shutting down...", flush=True)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
    description="Local agent for flashing Rockchip IoT devices via rkdeveloptool.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register routers under versioned prefix
app.include_router(status.router, prefix="/api/v1", tags=["Device Status"])
app.include_router(device.router, prefix="/api/v1", tags=["Subprocess Flash Logic"])
app.include_router(flash.router, prefix="/api/v1", tags=["Flashing"])
app.include_router(wifi.router, prefix="/api/v1", tags=["WiFi Injector via ADB"])
app.include_router(images.router, prefix="/api/v1", tags=["Image Downloader"])


def start() -> None:
    """Launch the uvicorn server (PyInstaller-safe)."""

    # 🔥 CRITICAL FIX 1: Handle missing stdout/stderr (no-console EXE)
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    print(f"Starting {APP_NAME} on http://{HOST}:{PORT}/api/v1/status")

    # 🔥 CRITICAL FIX 2: Disable uvicorn logging config (prevents crash)
    uvicorn.run(
        "agent.server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_config=None,   # 🔥 VERY IMPORTANT
    )


if __name__ == "__main__":
    start()