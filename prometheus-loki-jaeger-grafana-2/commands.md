
### Create Required Directories
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

### Start and manage the services
```bash

# Start the project for the first time, ostack is just the name given to the compose project 
docker compose -p ostack up -d --build

# Start the project
docker compose -p ostack up -d  

# Stop the project
docker compose -p ostack down

# Check the status of the project
docker compose -p ostack ps

# List the no of containers running in the project
docker compose -p ostack ls
# 10 out of 11 containers should be running

# Check the logs of a specific service, replace `order-service` with desired service name
docker compose -p ostack logs order-service --tail 100

# Check the logs of all services
docker compose -p ostack logs --tail 100


# sh into a container to debug it if needed
docker exec -it ostack-order-service sh

```

### Cleaning up
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