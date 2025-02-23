
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
│   │   ├── dev.env            # Env file when running locally
│   │   └── stage.env          # Env file running with docker-compose
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

1. **Install Python 3.11+**  
   Make sure you have Python 3.11 or a newer version installed.

2. **Create a virtual environment and install requirements**  
   ```bash
   cd order-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the Order Service**  
   ```bash
   APP_ENV='dev' uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Set up and start the Inventory Service**  
   Use another virtual environment if desired, then run:
   ```bash
   cd inventory-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   APP_ENV='dev' uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
   ```

5. **Local Development Note**  
   The `dev` environment (`APP_ENV=dev` with `dev.env`) is already set up for local use. You don't need to change anything. When running locally using the above commands, the OpenTelemetry collector and other backends are not yet configured, so you may see some warnings. However, the services themselves will work as expected.

6. **Stage Environment**  
   The `stage` environment (`APP_ENV=stage` with `stage.env`) is also preconfigured and requires no changes. The accompanying `docker-compose.yml` files use this environment to run the services in Docker containers and integrate them with the OpenTelemetry collector and other backends.


## Telemetry  
Check out the following files to see how telemetry metrics, logs, and traces are configured and used:
- **Configuration**:  
  - `order-service/telemetry.py`  
  - `inventory-service/telemetry.py`
- **Usage**:  
  - `order-service/main.py`  
  - `order-service/routes.py`  
  - `inventory-service/main.py`  
  - `inventory-service/routes.py`