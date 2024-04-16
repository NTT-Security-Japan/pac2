#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath $0))

mkdir ${SCRIPT_PATH}/dropbox 2>/dev/null
URL_CHECKED=false

# run dropbox driver with docker to mount dropbox files
docker run --detach -it --restart=always --name=dropbox \
    --net="host" \
    -e "TZ=$(readlink /etc/localtime | sed 's#^.*/zoneinfo/##')" \
    -e "DROPBOX_UID=$(id -u)" \
    -e "DROPBOX_GID=$(id -g)" \
    -e "POLLING_INTERVAL=10" \
    -v "${SCRIPT_PATH}/dropbox:/opt/dropbox" \
    otherguy/dropbox:latest 2>/dev/null

# monitor docker log
while true; do
    # "This computer is now linked to Dropbox." がログに含まれているか確認
    if docker logs dropbox | grep -q "This computer is now linked to Dropbox."; then
        echo "This computer is now linked to Dropbox."
        exit 0
    fi
    # "Please visit https://..." がログに含まれているか確認
    if [ "$URL_CHECKED" = false ]; then
        if docker logs dropbox | grep -q "Please visit https://www.dropbox.com/cli_link_nonce?nonce=" ; then
            # show the url to link dropbox account.
            docker logs dropbox | grep "Please visit https://www.dropbox.com/cli_link_nonce?nonce=" | tail -n 1
            URL_CHECKED=true
        fi
    fi
    # exit if container gives an alert.
    if docker logs dropbox | grep -q "\[ALERT\]" ; then
        echo "ALERT found in the log."
        exit 1
    fi
    # wait until container setup dropbox driver...
    sleep 1
done

