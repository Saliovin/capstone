#!/bin/bash
mkdir -p ./data/api
mkdir -p ./data/app
mkdir -p ./data/db
docker network create docker-net
docker pull postgres
docker run --rm --name pg-docker --network docker-net -e POSTGRES_PASSWORD=docker -e POSTGRES_DB=harvester_api -d postgres -v ./data/db:/var/lib/postgresql/data postgres
docker build ./harvester_api -t harvester_api
docker run --rm  --name harvester_api --network docker-net  -v ./data/api:/app/downloads -d harvester_api
docker build ./harvestingapp -t harvester_api
