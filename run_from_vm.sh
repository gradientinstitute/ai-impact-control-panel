#!/bin/bash

git checkout demo
docker kill $(docker ps -q)
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.29.0 -f docker-compose.yml -f docker-compose-prod.yml up -d
