from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db

# Import routers
from app.auth.router import router as auth_router
from app.modules.inputs.router import router as inputs_router
from app.modules.process_design.router import router as process_design_router
from app.modules.daily_operations.router import router as daily_operations_router
from app.modules.measurement.router import router as measurement_router
from app.modules.control.router import router as control_router
from app.ai.router import router as ai_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="IGAMS API",
    description="Intelligent Goal Achievement Management System - Management Control & Execution System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(inputs_router, prefix="/api/inputs", tags=["Inputs Module"])
app.include_router(process_design_router, prefix="/api/processes", tags=["Process Design"])
app.include_router(daily_operations_router, prefix="/api/operations", tags=["Daily Operations"])
app.include_router(measurement_router, prefix="/api/measurements", tags=["Measurement & Inspection"])
app.include_router(control_router, prefix="/api/control", tags=["Control & Reengineering"])
app.include_router(ai_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "IGAMS API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
