#!/bin/bash

MAX_DEVICE_NUM=20
for i in $(seq 1 "$MAX_DEVICE_NUM"); do
    export TUNNEL_PORT=$((i + 2000))
    sudo -E lsof -i :${TUNNEL_PORT} | awk 'NR>1 {print $2; exit}' | sort -u | xargs -r -I{} sh -c 'echo "Killing PID {} associated with port ${TUNNEL_PORT}; kill {}"'
done
