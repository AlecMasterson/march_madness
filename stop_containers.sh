#!/bin/bash

BASE_PORT=8000
NUM_CONTAINERS=4

for ((i=0; i<NUM_CONTAINERS; i++)); do
    PORT=$((BASE_PORT+i))
    docker stop march_madness-$PORT
done
