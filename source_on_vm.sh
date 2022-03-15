#!/bin/bash


# Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
# Kills all the current containers, spins up new ones based on latest images
# assuming we're running docker-compose in docker (see sock mapping)
#  https://cloud.google.com/community/tutorials/docker-compose-on-container-optimized-os

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.29.0 down --rmi all
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.29.0 -f docker-compose-prod.yml up -d
