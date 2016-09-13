#!/bin/bash

docker run -d --link cwdb:mysql --name cwweb -p 80:80 ciscowebkit
