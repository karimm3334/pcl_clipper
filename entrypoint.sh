#!/bin/bash
set -e

if [[ "$1" == "visualize" ]]; then
    shift
    exec /app/install/visualize.py "$@"
elif [[ "$1" == "clip" ]]; then
    shift
fi

exec /app/install/clip "$@"
