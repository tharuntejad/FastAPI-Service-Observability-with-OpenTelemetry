
## Fastapi Service Observability with Opentelemetry - Otel Collector, Prometheus, Loki, Jaeger, and Grafana 1


This project is a demonstration of an observability stack that integrates Prometheus, Loki, Jaeger, and Grafana, alongside FastAPI services instrumented with OpenTelemetry. The stack enables monitoring and troubleshooting through metrics, logs, and traces collected from the services and visualized on unified dashboards.

## Directory Structure
Below is the structure of the project, along with a description of what each file and folder represents.
```
./
├── config_volumes/                  # Configuration files for various services
│   ├── grafana-datasources.yaml    # Grafana data source configuration
│   ├── jaeger-all.yaml             # Jaeger configuration for traces
│   ├── jaeger-ui-config.json       # Jaeger UI-specific configuration
│   ├── loki-config.yaml            # Loki configuration
│   ├── otel-config.yaml            # OpenTelemetry Collector configuration
│   └── prometheus.yml              # Prometheus scrape configuration
├── data_volumes/                   # Data storage directories for services
│   ├── jaeger/data                 # Jaeger trace storage
│   ├── grafana/data                # Grafana dashboard storage
│   ├── loki/data                   # Loki log storage
│   └── prometheus/data             # Prometheus metric storage
├── docker-compose.yml              # Docker Compose file to orchestrate services
├── commands.md                     # Useful Docker and project commands
├── readme.md                       # Main documentation for the project
└── .gitignore                      # Git ignore file

```

## System Design
<img src="System Design.jpg" alt="System Architecture" width="800"/>

## Components

#### 1. FastAPI Services

Current project includes two sample FastAPI services—**Order Service** and **Inventory Service**—designed to generate telemetry data for demonstration purposes.
Below are the endpoints for each service and their respective functionalities:

- **Order Service**: Handles the placement of orders.
    
    - `/health`: Endpoint for health checks.
    - `/list-orders`: List all orders.
    - `/list-products`: Interacts with the inventory service to list available products.
    - `/order-product`: Place an order for a product.
- **Inventory Service**: Manages the inventory of products.
    
    - `/health`: Endpoint for health checks.
    - `/list-products`: List all available products and their stock levels.
    - `/reduce-stock`: Reduces stock for a product.


Refer to the documentation in `order-service/readme.md` and `inventory-service/readme.md` to learn how telemetry is integrated into FastaAPI services.

#### 2. OpenTelemetry Collector

The OpenTelemetry (OTel) Collector receives telemetry data from the services and forwards it to appropriate backends:

- Metrics: Sent to Prometheus.
- Logs: Sent to Loki.
- Traces: Sent to Jaeger.

```yaml
#  `./config_volumes/otel-config.yaml`
# visit https://www.otelbin.io/ for validating the config  
  
receivers:  
  # Prometheus to scrape metrics from otel-collector itself  
  prometheus:  
    config:  
      scrape_configs:  
        - job_name: 'otel-collector'  
          static_configs:  
            - targets: ["0.0.0.0:8888"]  
  
  # Receive metrics, traces, and logs via grpc and http  
  otlp:  
    protocols:  
      grpc:  
        endpoint: "0.0.0.0:4317"  
      http:  
        endpoint: "0.0.0.0:4318"  
  
  
processors:  
  # Process metrics,logs,traces in batch with a timeout of 1s  
  batch:  
    timeout: 1s  
  
  # Limit memory usage to 400MiB with a spike limit of 100MiB  
  memory_limiter:  
    check_interval: 1s  
    limit_mib: 400  
    spike_limit_mib: 100  
  
  # Add a severity_text attribute to logs/ used later by loki for log retention policy  
  attributes:  
    actions:  
      - key: severity  
        from_attribute: severity_text  
        action: insert  
  
# only [otlp otlphttp file opencensus prometheus zipkin debug nop kafka prometheusremotewrite] are supported in official otel-collector  
exporters:  
  # Print the output of the pipeline to stdout  
  debug:  
    verbosity: detailed  
  
  # Export metrics to Prometheus  
  prometheus:  
    endpoint: "0.0.0.0:8889"  
  
  # Export traces to Jaeger  
  otlphttp/jaeger:  
    endpoint: http://jaeger-all:4318  
  
  # Export logs to Loki (protocol_name/<custom name>(  
  otlphttp/loki:  
    endpoint: http://loki:3100/otlp  
  
  
  
extensions:  
  health_check:  
    endpoint: "0.0.0.0:13133"  
  pprof:  
    endpoint: "0.0.0.0:1777"  
  zpages:  
    endpoint: localhost:55679  
  
  
service:  
  extensions: [health_check, pprof]  
  pipelines:  
    metrics:  
      receivers: [otlp]  
      processors: [batch, memory_limiter]  
      exporters: [prometheus, debug]  
    logs:  
      receivers: [otlp]  
      processors: [attributes, batch]  
      exporters: [otlphttp/loki, debug]  
    traces:  
      receivers: [otlp]  
      processors: [attributes, batch, memory_limiter]  
      exporters: [otlphttp/jaeger, debug]
```


#### 3. Prometheus

- Collects and stores metrics from the OpenTelemetry Collector.
- Metrics are exposed on port `9090` and stored in `./data_volumes/prometheus/data`.

Configuration: `./config_volumes/prometheus.yml`

#### 4. Loki

- Collects and stores logs from the OpenTelemetry Collector.
- Logs are stored in `./data_volumes/loki/data`.

Configuration: `./config_volumes/jaeger-all.yaml`, `./config_volumes/loki-config.json`

#### 5. Jaeger

- Collects and stores traces from the OpenTelemetry Collector.
- Exposes the Query UI on port `16686`.
- Traces are stored in `./data_volumes/jaeger/data`.

 **Clarification on Jaeger Versions**
Starting from **Jaeger v2**, Jaeger no longer provides separate images like `jaeger-all-in-one`, `jaeger-query`, `jaeger-collector`, or `jaeger-ingestor`. Instead, it offers a single image:

👉 **`jaegertracing/jaeger`**

This image is modular and can be configured via **extensions** to act as a **collector, query, ingestor, or all-in-one**. Here, we are using it as **Jaeger Collector and Query**. 🚀
Configuration: `./config_volumes/jaeger-all.yaml`, `./config_volumes/jaeger-ui-config.json`

#### 6. Grafana

- Provides a unified dashboard to visualize metrics, logs, and traces.
- Pre-configured data sources:
    - Prometheus for metrics.
    - Loki for logs.
    - Jaeger for traces.
- Accessible on port `3000` with default credentials (`admin:admin`).

Configuration: `./config_volumes/grafana-datasources.yaml`

## Setting Up

1. Clone the repository:
    
    ```bash
    git clone <repository_url>
    cd prometheus-loki-jaeger-grafana-1
    ```
    
2. Create required directories & grant permissions on files & folders:
    
    ```bash
	  # Create data volumes  
	  mkdir -p ./data_volumes/jaeger/data  
	  mkdir -p ./data_volumes/grafana/data  
	  mkdir -p ./data_volumes/loki/data  
	  mkdir -p ./data_volumes/prometheus/data  
	  
	  # Grant permissions to the directories so containers can access them  
	  sudo chmod -R 777 ./data_volumes  
	  sudo chmod -R 777 ./config_volumes
    ```
    
3. Start the stack using Docker Compose:
    
    ```bash
    docker compose -p ostack up -d --build
    ```
    
4. Verify that all services are running :
    
    ```bash
    docker compose -p ostack ps 
    # 7 out of 7 containers should be running
    ```
    
5. Access the following services in your browser:
	- **Order Service**: `http://localhost:8000/docs`
	- **Inventory Service**: `http://localhost:8010/docs`
	- **Prometheus**: `http://localhost:9090` to view metrics.  
	- **Jaeger UI**: `http://localhost:16686` to view traces.  
	- **Grafana**: `http://localhost:3000` login with default credentials `admin` and `admin` visit data sources and explore the pre-configured data sources prometheus, loki, jaeger.  

6. Cleaning up
```bash  
  
# Stop the project  
docker compose -p ostack down  
  
# Delete all data volumes(remove all container related data)  
sudo chown -R $USER:$USER ./data_volumes  
rm -rf ./data_volumes/jaeger/data/*  
rm -rf ./data_volumes/grafana/data/*  
rm -rf ./data_volumes/loki/data/*  
rm -rf ./data_volumes/prometheus/data/*  
  
# Delete images  
docker image rm ostack-order-service  
docker image rm ostack-inventory-service  
  
```
**Note** 
Visit `commands.md` for more useful commands related to the project.
## Known Limitations

This setup is not production-ready due to:

- Local disk storage for Prometheus, Loki, and Jaeger.
- Single instances of all services, making scaling difficult.
- No retention policies for metrics, logs, or traces.
- No sampling strategies for logs or traces.

For a production-grade implementation, consider:

- Moving Loki data to S3.
- Moving Jaeger data to Elasticsearch.
- Deploying separate Jaeger instances for collection and querying.

If you're looking for an observability stack that's easy to set up, maintain, and cost-effective, consider the adjacent `clickhouse-1` project. Check out `clickhouse-1/readme.md` for more details.

## References

- [OpenTelemetry Collector Configuration](https://opentelemetry.io/docs/collector/configuration/#basics)
- [Jaeger Configuration Docs](https://www.jaegertracing.io/docs/2.2/configuration/#jaeger-storage)
