#!/bin/bash

# Provision script created for Ubuntu 14.04

APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -d "/vagrant" ]; then
  # Control will enter here if $DIRECTORY exists.
  APP_DIR="/vagrant"
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

cd ${APP_DIR}

bower --config.interactive=false install
virtualenv .venv
source .venv/bin/activate

pip install -r requirements.txt

echo "Installing start scripts"

cat << EOF > /usr/local/bin/realms-wiki
#!/bin/bash
${APP_DIR}/.venv/bin/realms-wiki "\$@"
EOF

sudo chmod +x /usr/local/bin/realms-wiki

realms-wiki start