import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.core.config import settings
from backend.app.core.database import Base, engine, init_db
from backend.app.api.v1.api import api_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce security checks on startup
    settings.validate_startup_secrets()
    # Initialize Database Tables once on startup
    init_db()
    logger.info("[*] %s database initialized.", settings.APP_NAME)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-Stack AI Web Platform for Professional Profiling, Skill Gap Analysis & Career Trajectory Prediction (Indus University)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration: Never combine "*" with allow_credentials=True
allow_all_origins = "*" in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Static Frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

if os.path.exists(FRONTEND_DIR):
    css_path = os.path.join(FRONTEND_DIR, "css")
    js_path = os.path.join(FRONTEND_DIR, "js")
    if os.path.exists(css_path):
        app.mount("/css", StaticFiles(directory=css_path), name="css")
    if os.path.exists(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV
    }
