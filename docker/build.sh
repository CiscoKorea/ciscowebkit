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

docker run -it --link cwdb:mysql --rm mariadb sh -c 'exec mysql -e "CREATE DATABASE ciscowebkit; GRANT ALL PRIVILEGES ON ciscowebkit.* TO 'cisco'@'localhost' IDENTIFIED BY 'cisco123'; GRANT ALL PRIVILEGES ON ciscowebkit.* TO 'cisco'@'%' IDENTIFIED BY 'cisco123';" -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'

docker build --rm --tag ciscowebkit . 
