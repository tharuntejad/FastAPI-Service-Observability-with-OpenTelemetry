
## Fastapi Service Observability with Opentelemetry - Otel Collector, Prometheus, Loki, Jaeger, and Grafana  2


This project extends the previous project, `Prometheus-Loki-Jaeger-Grafana-1`, introducing improvements such as:

- External storage for Loki and Jaeger (MinIO and Elasticsearch, respectively).
- Separate Jaeger components for trace collection and querying.

**Directory Structure**
```
./
├── config_volumes/                  # Configuration files for various services
│   ├── grafana-datasources.yaml    # Grafana data source configuration
│   ├── jaeger-collector.yaml       # Jaeger Collector configuration
│   ├── jaeger-query.yaml           # Jaeger Query configuration
│   ├── jaeger-ui-config.json       # Jaeger UI-specific configuration
│   ├── loki-config.yaml            # Loki configuration
│   ├── otel-config.yaml            # OpenTelemetry Collector configuration
│   └── prometheus.yml              # Prometheus scrape configuration
├── data_volumes/                   # Data storage directories for services
│   ├── jaeger/data                 # Jaeger trace storage in Elasticsearch
│   ├── grafana/data                # Grafana dashboard storage
│   ├── loki/data                   # Loki log storage (via MinIO)
│   ├── prometheus/data             # Prometheus metric storage
│   ├── minio/data                  # MinIO storage backend for Loki
│   └── elasticsearch/data          # Elasticsearch storage for Jaeger
├── docker-compose.yml              # Docker Compose file to orchestrate services
├── commands.md                     # Useful Docker and project commands
├── image.png                       # Diagram of the system architecture
├── readme.md                       # Main documentation for the project
└── .gitignore                      # Git ignore file
```

## System Design
<img src="System Design.jpg" alt="System Architecture"/>
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
- Traces: Sent to Jaeger running as Collector.

Configuration: `./config_volumes/otel-config.yaml`

#### 3. Prometheus

- Collects and stores metrics from the OpenTelemetry Collector.
- Metrics are exposed on port `9090` and stored in `./data_volumes/prometheus/data`.

Configuration: `./config_volumes/prometheus.yml`

#### 4. Loki

- Collects logs from the OpenTelemetry Collector and stores them in MinIO for scalability.
- Logs are accessed through Grafana dashboards.

Configuration:

- Loki: `./config_volumes/loki-config.yaml`
- MinIO: Exposed on port `9000` (API) and `9001` (UI).

#### 5. Jaeger

The enhanced Jaeger setup comprises:

- **Jaeger as Collector**:
    
    - Receives traces from the OpenTelemetry Collector.
    - Stores traces in Elasticsearch.
    - Configuration: `./config_volumes/jaeger-collector.yaml`
- **Jaeger as Query Service**:
    
    - Exposes the Query UI on port `16686`.
    - Retrieves traces from Elasticsearch.
    - Configuration: `./config_volumes/jaeger-query.yaml`, `./config_volumes/jaeger-ui-config.json`
- **Elasticsearch**:
    
    - Stores Jaeger traces.
    - Exposed on ports `9200` and `9300`.

#### 6. Grafana

- Serves as a unified tool for viewing and visualizing metrics, logs, and traces.  
- Prometheus, Loki, and Jaeger have already been configured as data sources in Grafana and are directly visible among its data sources.  
- Accessible on port `3000` with default credentials (`admin:admin`).
Configuration: `./config_volumes/grafana-datasources.yaml`

## Setting Up

1. Clone the repository:
    
    ```bash
    git clone <repository_url>
    cd prometheus-loki-jaeger-grafana-2
    ```
    
2. Create required directories:
    
    ```bash
      # Create data volumes  
	  mkdir -p ./data_volumes/elasticsearch/data  
	  mkdir -p ./data_volumes/grafana/data  
	  mkdir -p ./data_volumes/loki/data  
	  mkdir -p ./data_volumes/minio/data  
	  mkdir -p ./data_volumes/prometheus/data  
	  
	  # Grant permissions to the directories so containers can access them  
	  sudo chmod -R 777 ./data_volumes  
	  sudo chmod -R 777 ./config_volumes
    ```
    
3. Start the stack using Docker Compose:
    
    ```bash
    docker compose -p ostack up -d --build
    ```
    
4. Verify that all services are running:
    
    ```bash
    docker compose -p ostack ps
    # 10 out of 11 containers should be running
    ```
    
5. Access the following services in your browser:
	- **Order Service**: `http://localhost:8000/docs`
	- **Inventory Service**: `http://localhost:8010/docs`
	- **Prometheus**: `http://localhost:9090` to view metrics.  
	- **Jaeger UI**: `http://localhost:16686` to view traces.  
	- **Grafana**: `http://localhost:3000` login with default credentials `admin` and `admin` visit data sources and explore the pre-configured data sources prometheus, loki, jaeger.  
	- **MinIO Console**: `http://localhost:9001` login with default credentials `admin` and `password` to manage Loki storage.

6. Cleaning up
    ```bash
    # Stop the project  
    docker compose -p ostack down  
      
    # Delete all data volumes(remove all container related data)  
    sudo chown -R $USER:$USER ./data_volumes  
    rm -rf ./data_volumes/elasticsearch/data/*  
    rm -rf ./data_volumes/grafana/data/*  
    rm -rf ./data_volumes/loki/data/*  
    rm -rf ./data_volumes/minio/data/*  
    rm -rf ./data_volumes/minio/data/.minio.sys  
    rm -rf ./data_volumes/prometheus/data/*  
      
      
    # Delete images  
    docker image rm ostack-order-service  
    docker image rm ostack-inventory-service
    
    ```

**Note** 
Visit `commands.md` for more useful commands related to the project.

## Known Limitations

This setup improves scalability but is not fully production-ready due to:

- MinIO and Elasticsearch configurations are basic and may require fine-tuning.
- Single-node Elasticsearch deployment.

For a production-grade implementation, consider:

- Deploying Elasticsearch as a multi-node cluster.
- Using managed solutions for storage (e.g., AWS S3 for Loki, managed Elasticsearch for Jaeger).

## References

- [OpenTelemetry Collector Configuration](https://opentelemetry.io/docs/collector/configuration/#basics)
- [Jaeger Configuration Docs](https://www.jaegertracing.io/docs/2.2/configuration/#jaeger-storage)
- [Loki Configuration Docs](https://grafana.com/docs/loki/latest/configure/)
