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
python-pip python-virtualenv python-dev zlib1g-dev \
libffi-dev libyaml-dev libssl-dev nodejs

# lxml deps
# libxml2-dev libxslt1-dev

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

cd /home/vagrant


virtualenv .venv
source .venv/bin/activate

cd /vagrant
bower --config.interactive=false install
pip install -r requirements.txt

echo "Installing start scripts"

cat << EOF > /tmp/realms-wiki
#!/bin/bash
/home/vagrant/.venv/bin/realms-wiki "\$@"
EOF

sudo mv /tmp/realms-wiki /usr/local/bin

sudo chmod +x /usr/local/bin/realms-wiki

realms-wiki start