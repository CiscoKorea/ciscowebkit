#!/bin/bash

docker pull mariadb

docker run -d --name cwdb -e MYSQL_ROOT_PASSWORD=cisco123 -d mariadb

echo "Wait Running Mariadb"
sleep 4
echo "Wait Running Mariadb"
sleep 4
echo "Wait Running Mariadb"
sleep 4
echo "Wait Running Mariadb"
sleep 4
echo "Wait Running Mariadb"
sleep 4

docker build --rm --tag ciscowebkit . 
