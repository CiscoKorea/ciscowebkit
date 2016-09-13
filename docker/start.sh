#!/bin/bash

docker run -d --link cwdb:mysql --name cwweb ciscowebkit
