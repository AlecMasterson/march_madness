#!/bin/bash

BASE_PORT=8000
NUM_CONTAINERS=4

for ((i=0; i<NUM_CONTAINERS; i++)); do
    PORT=$((BASE_PORT+i))
    docker run --env-file .env -p $PORT:8000 --name march_madness-$PORT --rm -itd --mount type=bind,source="$(pwd)",target=/scripts march_madness_selenium
done
