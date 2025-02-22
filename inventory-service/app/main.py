


from app.core.config import settings
from fastapi import FastAPI, HTTPException
from app.telemetry import initialize_telemetry
from app.db import get_db_connection
import logging
from opentelemetry import trace

# Import routers
from app.routes import inventory_router

# Set up logger
logger = logging.getLogger(settings.service_name)
logger.setLevel(logging.INFO)

# Get tracer instance
tracer = trace.get_tracer(__name__)


# Initialize FastAPI app
app = FastAPI()

# Initialize telemetry
initialize_telemetry(app)

# Health check endpoint
@app.get("/health")
def health():
    # Start a new span for the health check endpoint
    with tracer.start_as_current_span("health_endpoint") as span:
        # Log a message with the current environment
        logger.info(f"Health check , {settings.app_env}", extra={'environment': settings.app_env})

        # Add an event to the span to indicate that the health check was successful
        span.add_event("Health check completed successfully")
        return {"status": "ok", "environment": settings.app_env, "service_name": settings.service_name}

# Add routers
app.include_router(inventory_router)
