#!/bin/bash

# Provision script created for Ubuntu 14.04
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Provisioning..."

add-apt-repository -y ppa:chris-lea/node.js
apt-get update
apt-get install -y python build-essential git libpcre3-dev python-software-properties \
python-pip python-virtualenv python-dev pkg-config curl libxml2-dev libxslt1-dev zlib1g-dev \
libffi-dev nodejs screen node-cleancss

# Default cache is memoization

# Redis
# add-apt-repository -y chris-lea/redis-server
# add-apt-repository -y chris-lea/python-redis
# apt-get update
# apt-get install -y redis-server

# Default DB is sqlite

# Mysql
# apt-get install -y mysql-server mysql-client

# MariaDB
# apt-get install -y mariadb-server mariadb-client

# Postgres
# apt-get install -y postgresql postgresql-contrib

cd ${APP_DIR}

# Install frontend assets
npm install -g bower
bower install

virtualenv .venv
source .venv/bin/activate

pip install -r requirements.txt

cat << EOF > /usr/local/bin/realms-wiki
#!/bin/bash
${APP_DIR}/.venv/bin/python ${APP_DIR}/manage.py "\$@"
EOF
chmod +x /usr/local/bin/realms-wiki

cat << EOF > /etc/init/realms-wiki.conf
description "Realms Wiki"
author "scragg@gmail.com"
start on runlevel [2345]
stop on runlevel [!2345]
respawn
exec /usr/local/bin/realms-wiki run
EOF