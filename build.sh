#!/bin/bash

docker build -t niceygy/eddatacollector .

docker tag niceygy/eddatacollector ghcr.io/niceygy/eddatacollector:latest

docker push ghcr.io/niceygy/eddatacollector:latest

cd /opt/stacks/elite_db

docker compose pull

docker compose down

docker compose up -d

cd /opt/stacks/elite_apps

docker compose restart

docker logs eddn_connector -f