#!/bin/bash
docker-compose down &&\
docker-compose up -d &&\
docker exec -it starrocks_mysql_1 bash