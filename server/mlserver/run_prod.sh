#!/bin/bash

if [ ! -f "server.secret" ]; then
    echo "server.secret does not exist. Run gen_key.sh"
    exit 1
fi

export DEVA_MLSERVER_CONFIG=./prod.cfg
export SECRET_KEY="$(cat server.secret)"
FLASK_ENV=production gunicorn -b 0.0.0.0:80 app:app
