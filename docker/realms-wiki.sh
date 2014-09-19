#!/bin/sh

chdir /home/deploy/realms-wiki

if [ "${REALMS_WIKI_CONFIG}" != "" ]; then
    realms-wiki configure ${REALMS_WIKI_CONFIG}
fi

exec /sbin/setuser deploy /home/deploy/realms-wiki/.venv/bin/python realms-wiki run >>/var/log/realms-wiki/realms-wiki.log 2>&1
