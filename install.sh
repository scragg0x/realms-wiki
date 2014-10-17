#!/bin/bash

# Provision script created for Ubuntu 14.04

APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_USER="$( stat -c '%U' ${APP_DIR} )"

if [ -d "/vagrant" ]; then
  # Control will enter here if $DIRECTORY exists.
  APP_DIR="/vagrant"
  APP_USER="vagrant"
fi

if [ "${APP_USER}" == "root" ]; then
    echo "Installing app as root is not recommended"
    echo "Username is determined by owner of application directory."
fi

echo "Provisioning..."
sudo apt-get update
sudo apt-get install -y software-properties-common python-software-properties
sudo add-apt-repository -y ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install -y python build-essential pkg-config git  \
python-pip python-virtualenv python-dev libxml2-dev libxslt1-dev zlib1g-dev \
libffi-dev libyaml-dev libssl-dev nodejs

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

# Install frontend assets
sudo npm install -g bower
sudo -iu ${APP_USER} bower --allow-root --config.cwd=${APP_DIR} --config.directory=realms/static/vendor --config.interactive=false install

sudo -iu ${APP_USER} virtualenv ${APP_DIR}/.venv

cd ${APP_DIR} && sudo -iu ${APP_USER} ${APP_DIR}/.venv/bin/pip install -r ${APP_DIR}/requirements-dev.txt

echo "Installing start scripts"
cat << EOF > /usr/local/bin/realms-wiki
#!/bin/bash
${APP_DIR}/realms-wiki "\$@"
EOF

sudo chmod +x /usr/local/bin/realms-wiki

cat << EOF > /etc/init/realms-wiki.conf
limit nofile 65335 65335

respawn

description "Realms Wiki"
author "scragg@gmail.com"

chdir ${APP_DIR}

env PATH=${APP_DIR}/.venv/bin:/usr/local/bin:/usr/bin:/bin:$PATH
env LC_ALL=en_US.UTF-8
env GEVENT_RESOLVER=ares

export PATH
export LC_ALL
export GEVENT_RESOLVER

setuid ${APP_USER}
setgid ${APP_USER}

start on runlevel [2345]
stop on runlevel [!2345]

respawn

exec gunicorn \
  --name realms-wiki \
  --access-logfile - \
  --error-logfile - \
  --worker-class gevent \
  --workers 2 \
  --bind 0.0.0.0:5000 \
  --user ${APP_USER} \
  --group ${APP_USER} \
  --chdir ${APP_DIR} \
  wsgi:app
EOF
