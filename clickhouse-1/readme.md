
## FastAPI Service Observability with OpenTelemetry - Otel Collector, ClickHouse & Grafana

Observability provides deep insights into the internal state of an application by analyzing metrics, logs, and traces. It enables faster issue detection, improved performance monitoring, and efficient troubleshooting, ensuring systems remain reliable, scalable, and user-friendly.

This project showcases how observability—encompassing metrics, logs, and traces—can be seamlessly integrated into FastAPI services using OpenTelemetry. It also covers the collection, storage, monitoring, and visualization of telemetry data with the help of the OTEL Collector, ClickHouse, and Grafana.

## Directory Structure
Below is the structure of the project, along with a description of what each file and folder represents.
```
./
├── config_volumes/                 # Configuration files for various services
│   └── otel-config.yaml            # OpenTelemetry Collector configuration
├── data_volumes/                   # Data storage directories for services
│   ├── clickhouse/database         # ClickHouse data storage
│   ├── clickhouse/log              # ClickHouse log storage
│   └── grafana/data                # Grafana dashboard storage
├── docker-compose.yml              # Docker Compose file to orchestrate services
├── commands.md                     # Useful Docker and project commands
├── readme.md                       # Main documentation for the project
└── .gitignore                      # Git ignore file
```

## System Design
<img src="System Design.jpg" alt="System Architecture"/>


## Components

#### 1. FastAPI Services

Current project includes two sample FastAPI services—**Order Service** and **Inventory Service**—designed to generate telemetry data for demonstration purposes.
Below are the endpoints for each service and their respective functionalities:

**Order Service**: Handles the placement of orders.
    
- `/health`: Endpoint for health checks.
- `/list-orders`: List all orders.
- `/list-products`: Interacts with the inventory service to list available products.
- `/order-product`: Place an order for a product.

**Inventory Service**: Manages the inventory of products.
    
- `/health`: Endpoint for health checks.
- `/list-products`: List all available products and their stock levels.
- `/reduce-stock`: Reduces stock for a product.


Refer to the documentation in `order-service/readme.md` and `inventory-service/readme.md` to learn how telemetry is integrated into FastaAPI services.

#### 2. Open Telemetry Collector

The OpenTelemetry (OTel) Collector receives telemetry data from the services and forwards it to appropriate backends:

- **Metrics**: Sent to ClickHouse.
- **Logs**: Sent to ClickHouse.
- **Traces**: Sent to ClickHouse.

```yaml
#  `./config_volumes/otel-config.yaml`

receivers:
  # Prometheus to scrape metrics from otel-collector itself
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          static_configs:
            - targets: ["0.0.0.0:8888"]
  # Receive metrics, traces, and log via grpc and http
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"

processors:
  # Process metrics,log,traces in batch with a timeout of 1s
  batch:
    timeout: 1s

  # Limit memory usage to 400MiB with a spike limit of 100MiB
  memory_limiter:
    check_interval: 1s
    limit_mib: 400
    spike_limit_mib: 100

exporters:
  # Print the output of the pipeline to stdout
  debug:
    verbosity: detailed

  # Export metrics, traces, and logs to clickhouse
  clickhouse:
    endpoint: tcp://clickhouse:9000?dial_timeout=10s&compress=lz4
    username: default
    password: password
    database: default
    timeout: 5s
    retry_on_failure:
     enabled: true
     initial_interval: 5s
     max_interval: 30s
     max_elapsed_time: 300s

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
      exporters: [clickhouse, debug]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [clickhouse, debug]
    traces:
      receivers: [otlp]
      processors: [batch, memory_limiter]
      exporters: [clickhouse, debug]

```

#### 3. ClickHouse

ClickHouse serves as a scalable, high-performance backend for observability data. Metrics, logs, and traces are efficiently stored and queried.

#### 4. Grafana

Data can be directly queried by opening a shell in the ClickHouse server container and using the ClickHouse client. However, using Grafana makes visualization easier.

## Setting Up

#### 1. Clone the repository:
    
```bash
git clone <repository_url>
cd prometheus-loki-jaeger-grafana-1
```

#### 2. Create required directories & grant permissions on files & folders:
    
```bash
mkdir -p ./data_volumes/clickhouse/database
mkdir -p ./data_volumes/clickhouse/log
mkdir -p ./data_volumes/grafana/data
sudo chmod -R 777 ./data_volumes
sudo chmod -R 777 ./config_volumes
```

#### 3. Start the stack using Docker Compose:
    
```bash
docker compose -p ostack up -d --build
```
    
#### 4. Verify that all services are running:
    
```bash
docker compose -p ostack ps
# 5 out of 5 containers should be running
```

#### 5. Access the following services in your browser:
- **Order Service**: `http://localhost:8000/docs`
- **Inventory Service**: `http://localhost:8010/docs`
- **Clikchouse**: `http://localhost:8443`
- **Grafana**: `http://localhost:3000`. Login with default credentials `admin:admin`.

#### 6. Installing the ClickHouse Plugin in Grafana

By default, Grafana does not include the ClickHouse plugin. You need to install it manually:

1. Navigate to **Administration -> Plugins and data -> Plugins**.
2. Search for **ClickHouse**.
3. Select the **official ClickHouse plugin** from Grafana.
4. Click **Install** (top-right corner).
5. Once installed, add a new **Data Source** (top-right corner).
6. Fill in the details:
	- **Server Address**: `clickhouse` (since our service runs at `http://clickhouse:9000` inside Docker).
	- **Server Port**: `9000`
	- **Username**: `default`
	- **Password**: `password`
	- **Protocol**: `Native`
	- **Secure Connection**: Disable the secure connection since we are using HTTP instead of HTTPS.

If using **ClickHouse Cloud** instead of a local ClickHouse server (container):

- Get the connection details `Username, Password & URL`from the **Connect** section of the ClickHouse Cloud UI.
- The **URL** might look like `https://<id><region>.aws.clickhouse.cloud:8443`.
- Set **Server Adddress** to `<id><region>.aws.clickhouse.cloud`
- Set **Server Port** to `8443`.
- Switch **Protocol** from `Native` to `HTTP`.
- Toggle **Secure Connection**.
- Set the retrieved **Username** and **Password** accordingly.
Test and save the connection to add this as a data source. Once added, you can explore and query ClickHouse by navigating to **Datasources** → **Newly Added ClickHouse Datasource** → **Explore**.


#### 7. Viewing Metrics, Logs, and Traces
Once the project is up and running, you can view the metrics, logs, and traces in two ways:

**1. Using ClickHouse Client**
Access the ClickHouse container, start the ClickHouse client, and run queries:

```bash
# Connect to the ClickHouse client for querying the database  
docker exec -it ostack-clickhouse-1 clickhouse-client -h localhost --user default --password password
```

Once the client starts, run the following query:

```bash
SELECT * FROM otel_logs;  -- Visit queries.sql for more useful queries
```

**2. Using Grafana UI**
	
Alternatively, you can explore the data via Grafana:

- Install the **ClickHouse plugin** in Grafana.
- Add ClickHouse as a **data source**.
- Start exploring the data by running queries in the **SQL editor**.

#### 8. Cleaning up
```bash  
  
# Stop the project  
docker compose -p ostack down  
  
# Delete all data volumes(remove all container related data)  
sudo chown -R $USER:$USER ./data_volumes  
rm -rf ./data_volumes/clickhouse/database/*  
rm -rf ./data_volumes/clickhouse/log/*  
rm -rf ./data_volumes/grafana/data/*
  
# Delete images  
docker image rm ostack-order-service  
docker image rm ostack-inventory-service  
  
```

#### **Additional Resources**

- Visit `commands.md` for useful commands related to the project.
- Visit `queries.sql` for useful queries related to ClickHouse.



## Data Retention Policies

Telemetry data—including logs, metrics, and traces—can grow rapidly in ClickHouse, potentially leading to excessive storage consumption. To manage storage efficiently, it’s essential to periodically remove low-value historical data.

While implementing data retention policies can be cumbersome with other tools like Prometheus, Loki, or Tempo, ClickHouse simplifies this process through the use of **Time-to-Live (TTL)** settings. With just a single query, you can define retention periods based on the data's severity or relevance.

Here’s an example of how to set TTL for different log levels:

```sql
ALTER TABLE otel_logs 
MODIFY TTL  
    toDateTime(Timestamp) + INTERVAL 1 MONTH WHERE SeverityText = 'INFO',    -- Retain INFO logs for 1 month  
    toDateTime(Timestamp) + INTERVAL 2 MONTH WHERE SeverityText = 'WARNING', -- Retain WARNING logs for 2 months  
    toDateTime(Timestamp) + INTERVAL 3 MONTH WHERE SeverityText = 'ERROR';   -- Retain ERROR logs for 3 months
```

This query automatically purges logs after their defined retention periods, ensuring optimal storage utilization without manual intervention.

🔍 _For a detailed explanation of the retention policies, refer to_ [`clickhouse-1/retention_policies.sql`](https://chatgpt.com/c/clickhouse-1/retention_policies.sql).


## Monitoring & Alerts

While ClickHouse excels as a high-performance database, it does not offer built-in monitoring and alerting capabilities out of the box. However, its robust ecosystem and compatibility with various programming languages make it easy to implement custom monitoring solutions.

There are two common approaches to setting up alerts with ClickHouse:

1. **Programmatic Monitoring:**  
    Use any supported programming language (such as Python or Go) to run periodic queries against ClickHouse, detect anomalies or errors, and automatically dispatch alerts or reports.
    
2. **Grafana Integration:**  
    Configure ClickHouse as a data source in Grafana to create dashboards and set up alerting rules. Grafana’s built-in alerting feature can monitor query results and trigger notifications via various channels like email, Slack, or webhooks.
    

Both methods ensure that issues are detected and reported in a timely manner, providing comprehensive observability for your system.

## Scaling Up

For medium-sized applications, running the **OTEL Collector** as a container on a virtual machine (VM) is typically sufficient. However, larger organizations with higher telemetry data volumes may require a more scalable architecture.

#### Scaling the OTEL Collector

- **Dedicated Collectors:**  
    Deploy separate collectors for **metrics**, **logs**, and **traces** to distribute the workload effectively.
- **Stateless Architecture:**  
	Since OTEL Collectors are stateless, you can deploy multiple instances and load balance across them to handle increased traffic and ensure high availability.
	
🔗 _For detailed instructions on scaling the collector, refer to the official documentation:_  
[OpenTelemetry Collector Scaling Guide](https://opentelemetry.io/docs/collector/scaling/)



#### Scaling Storage with ClickHouse

When it comes to storage, **ClickHouse Cloud** is a highly efficient solution. It offers:

- **Excellent cost-to-performance ratio** for handling large datasets.
- **Rich tooling** for user management, data organization, and monitoring.
- **Seamless scalability** to accommodate growing telemetry data without significant overhead.

By leveraging ClickHouse Cloud, you can ensure your observability stack remains performant and manageable as your application scales.

## ⚠️ Collector & ClickHouse Exporter Note

We’re using the `opentelemetry-collector-contrib` image instead of the official OpenTelemetry Collector because it provides a ClickHouse exporter and supports more community features. While this isn’t inherently problematic, some parts of the ClickHouse exporter are still in alpha. They generally work fine, but be cautious when upgrading to a newer version—make sure to thoroughly test all features first. You can track the exporter’s status and updates here: [opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib).

## Wrap Up

This document addressed the key challenges of integrating observability into FastAPI services and provided practical solutions for each step of the process. Here's a quick summary of what we covered:

- **Instrumentation:**  
    How to instrument FastAPI services to capture telemetry data.
    
- **Generating Telemetry:**  
    Techniques to generate **logs**, **traces**, and **metrics** within your application.
    
- **Collection & Storage:**  
    Methods to collect telemetry data using the **OTEL Collector** and store it efficiently in **ClickHouse**.
    
- **Retention Policies:**  
    Strategies to manage data growth by applying **TTL-based retention policies** in ClickHouse.
    
- **Monitoring & Alerting:**  
    Approaches to monitor telemetry data and set up **alerts** using programming languages or **Grafana**.
    
- **Scaling Out the System:**  
    Best practices for scaling the **OTEL Collector** and **ClickHouse** to meet the demands of larger applications.
 
By following this guide, you can build a **robust, scalable, and cost-effective observability solution** for FastAPI services, ensuring better visibility, faster troubleshooting, and improved system reliability.


## References

- **ClickHouse Official Integration Guide:**  
  *Storing Traces and Spans with OpenTelemetry in ClickHouse* — [ClickHouse Blog Article](https://clickhouse.com/blog/storing-traces-and-spans-open-telemetry-in-clickhouse)

- **Associated Git Repository:**  
  *ClickHouse OpenTelemetry Demo* — [GitHub Repository](https://github.com/ClickHouse/opentelemetry-demo/tree/main)

