
# Inventory Service

Inventory Service is a FastAPI-based microservice that handles inventory management, including adding, updating, and querying inventory data. 
The service includes telemetry integration using OpenTelemetry for tracing, metrics, and logging, and exports these to the 
OpenTelemetry Collector for further processing.

The **Inventory Service** is designed to work alongside the **Order Service**, and both are intended to run together as part of the overall system.

---

## Project Structure

```
inventory-service/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── dev.env            # Environment file for development
│   │   └── stage.env          # Environment file for staging
│   ├── __init__.py
│   ├── db.py                  # Database connection and initialization
│   ├── inventory.db           # SQLite database for inventory management
│   ├── main.py                # Entry point for FastAPI app
│   ├── models.py              # Pydantic models for request/response validation
│   ├── routes.py              # API endpoints for inventory operations
│   └── telemetry.py           # OpenTelemetry setup for tracing, metrics, and logging
├── .dockerignore              # Docker ignore file
├── .gitignore                 # Git ignore file
├── Dockerfile                 # Docker configuration
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
service_name = "inventory-service"
# Endpoint of OpenTelemetry Collector for exporting telemetry data
otlp_grpc_endpoint = "http://localhost:4317"
otlp_http_endpoint = "http://localhost:4318"
```
- The `dev.env` file is preconfigured for local development and testing. It does not require any external services to be running.
- For staging, use the `stage.env` file, which works with the provided `docker-compose.yml` file. This file automatically starts the OpenTelemetry Collector and other backend services.

---

## Start the Service

### Local (Development Mode)

Run the service with:
```bash
APP_ENV='dev' uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
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

## Integration with Order Service

The **Inventory Service** and **Order Service** are designed to work together to manage orders and inventory effectively. When deployed, both services should be started and configured to interact with each other. Ensure the `inventory_service_url` in the **Order Service's** environment file points to the **Inventory Service's** running endpoint.

For example, in `dev.env` for the **Order Service**:
```env
inventory_service_url = "http://localhost:8010"
```

In staging, the `docker-compose.yml` file will ensure both services run together with the required configurations.

---