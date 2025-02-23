
# FastAPI-Service-Observability-with-OpenTelemetry

This project demonstrates observability in **FastAPI** services using **OpenTelemetry** instrumentation. It showcases how telemetry data can be collected and visualized using various backends like **Prometheus**, **Loki**, **Jaeger**, **Grafana**, and **ClickHouse**.

## Project Structure

Below is an overview of the project’s structure:

- **order-service/**:  
  A simple demo **FastAPI** service representing an **order management system**, instrumented with **OpenTelemetry**.  
  👉 Refer to [order-service/README.md](order-service/README.md) for more information.


- **inventory-service/**:  
  A simple demo **FastAPI** service representing an **inventory system**, instrumented with **OpenTelemetry**.  
  👉 Refer to [inventory-service/README.md](inventory-service/README.md) to learn more.

- **clickhouse-1/**:  
  Contains configuration and setup details for using **ClickHouse & Grafana** as a observability backend.  
  👉 Refer to [clickhouse-1/README.md](clickhouse-1/README.md) for more details.

- **prometheus-loki-jaeger-grafana-1/** and **prometheus-loki-jaeger-grafana-2/**:  
  Directories containing configurations for using **Prometheus**, **Loki**, **Jaeger**, and **Grafana** as observability backends.  
  👉 Check their respective README files for setup instructions:  
  - [prometheus-loki-jaeger-grafana-1/README.md](prometheus-loki-jaeger-grafana-1/README.md)  
  - [prometheus-loki-jaeger-grafana-2/README.md](prometheus-loki-jaeger-grafana-2/README.md)  


## How to Get Started

1. Choose a backend (`clickhouse-1/` (recommended), `prometheus-loki-jaeger-grafana-1/`, or `prometheus-loki-jaeger-grafana-2/`) and follow its README to set up observability.
2. Explore the services (`order-service/`, `inventory-service/`) to understand how OpenTelemetry is integrated.
3. Run the services and observe the telemetry data flow through the chosen backend.


Each subdirectory contains a dedicated **README.md** with step-by-step instructions. Be sure to visit those files for comprehensive setup details. 😊

