#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath $0))

echo "[-] Remove dropbox container."
docker kill dropbox 2>/dev/null && docker rm dropbox 2>/dev/null

echo "[-] Cleanup dropbox directory."
sudo rm -rf ${SCRIPT_PATH}/dropbox
mkdir ${SCRIPT_PATH}/dropbox
touch ${SCRIPT_PATH}/dropbox/.gitkeep