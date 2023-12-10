#!/bin/bash
docker-compose down &&\
docker-compose up -d --remove-orphans &&\
docker exec -it mysql_container bash