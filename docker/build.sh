#!/bin/bash

echo "Start CWDB Container"
docker run --name cwdb -e MYSQL_ROOT_PASSWORD=cisco123 -d mariadb

while true; do
        echo "Wait to start CWDB"
        docker run -it --link cwdb:mysql --rm mariadb sh -c 'exec mysql -e"exit" -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"' >> /dev/null
        if [ "$?" == "0" ]; then
                break
        fi
        sleep 2
done

echo "Confirm CWDB and Setting Ciscowebkit Database"
docker run -it --link cwdb:mysql --rm mariadb sh -c 'exec mysql -e"CREATE DATABASE ciscowebkit; GRANT ALL PRIVILEGES ON ciscowebkit.* TO \"cisco\"@\"localhost\" IDENTIFIED BY \"cisco123\"; GRANT ALL PRIVILEGES ON ciscowebkit.* TO \"cisco\"@\"%\" IDENTIFIED BY \"cisco123\";" -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'

echo "Show Databases"
docker run -it --link cwdb:mysql --rm mariadb sh -c 'exec mysql -e"show databases;" -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD"'

echo "Show Container"
docker ps

docker build --rm --tag ciscowebkit Dockerfile_Ubuntu
