#!/bin/bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
FLASK_APP=${SCRIPT_PATH}/wsgi.py
DROPBOX_PATH=${SCRIPT_PATH}/../mount/dropbox/Dropbox/pac2

rm -rf ${SCRIPT_PATH}/migrations
rm ${SCRIPT_PATH}/data.db
rm -rf ${DROPBOX_PATH}

poetry run flask db init
poetry run flask db migrate
poetry run flask db upgrade
