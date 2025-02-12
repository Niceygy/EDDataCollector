#!/bin/bash

docker build -t niceygy/eddatacollector .

docker tag niceygy/eddatacollector ghcr.io/niceygy/eddatacollector:latest

docker push ghcr.io/niceygy/eddatacollector:latest

