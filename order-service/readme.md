
# Order Service

Order Service is a FastAPI-based microservice that handles order management, including placing orders, fetching order lists, and interacting  
with an inventory service. The service integrates telemetry using OpenTelemetry for tracing, metrics, and logging and exports these to  
the OpenTelemetry Collector for further processing.

---

## Project Structure

```
order-service/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── dev.env            # Environment file for development
│   │   └── stage.env          # Environment file for staging
│   ├── __init__.py
│   ├── db.py                  # Database connection and initialization
│   ├── main.py                # Entry point for FastAPI app
│   ├── models.py              # Pydantic models for request/response validation
│   ├── routes.py              # API endpoints for order operations
│   └── telemetry.py           # OpenTelemetry setup for tracing, metrics, and logging
├── venv/                      # Virtual environment
├── .dockerignore              # Docker ignore file
├── .gitignore                 # Git ignore file
├── Dockerfile                 # Docker configuration
├── readme.md                  # Project documentation (this file)
└── requirements.txt           # Python dependencies
```

---

## Setup Environment

1. Ensure Python 3.11+ is installed.
2. Set the environment variable `APP_ENV` to one of the following:
   - `dev` for local development
   - `stage` for staging
3. Use the respective `.env` file to configure the environment.

For example, in `dev.env`:
```env
# Name of the service
service_name = "order-service"
# Endpoint of OpenTelemetry Collector for exporting telemetry data
otlp_grpc_endpoint = "http://localhost:4317"
otlp_http_endpoint = "http://localhost:4318"
# Inventory service URL
inventory_service_url = "http://localhost:8010"
```
- The `dev.env` file is preconfigured for local development and testing. It does not require any external services to be running.
- For staging, use the `stage.env` file, which works with the provided `docker-compose.yml` file. This file automatically starts the OpenTelemetry Collector and other backend services.

---

## Start the Service

### Local (Development Mode)

Run the service with:
```bash
APP_ENV='dev' uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Note: When running locally, you may see warnings because metric, logging, and tracing backends are not configured for development.

### Containerized (Staging Mode)

To run the service with the provided `docker-compose.yml` file, set the environment variable `APP_ENV` to `stage` in the `docker-compose.yml` file.

---

## Metrics, Logging, and Tracing

The service integrates with OpenTelemetry for tracing, metrics, and logging, as defined in `app/telemetry.py`. Review the comments in the code for detailed information on the integration.

- **Development Mode**: When running locally, metrics, logs, and traces are generated but not sent to the OpenTelemetry Collector, as it is not running in `dev` mode.
- **Staging Mode**: When running as part of the provided `docker-compose.yml` file, metrics, logs, and traces are sent to the OpenTelemetry Collector, which then exports them to the respective backends.

---
