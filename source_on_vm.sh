#!/bin/bash


# Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
# Kills all the current containers, spins up new ones based on latest images
# assuming we're running docker-compose in docker (see sock mapping)
#  https://cloud.google.com/community/tutorials/docker-compose-on-container-optimized-os

# Requires the docker daemon to be logged into the artifact repo see
# https://cloud.google.com/artifact-registry/docs/docker/authentication#standalone-helper

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.29.0 down --rmi all

docker pull australia-southeast1-docker.pkg.dev/ongoing-236000/aicontrolpanel/backend
docker pull australia-southeast1-docker.pkg.dev/ongoing-236000/aicontrolpanel/frontend

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD:$PWD" -w="$PWD" docker/compose:1.29.0 -f docker-compose-prod.yml up -d
