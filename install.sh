#!/bin/bash

# Provision script created for Ubuntu 14.04

APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -d "/vagrant" ]; then
  # Control will enter here if $DIRECTORY exists.
  APP_DIR="/vagrant"
fi

echo "Provisioning..."

if ! type "add-apt-repository" > /dev/null; then
    sudo apt-get update
    sudo apt-get install -y software-properties-common python-software-properties
fi

# Elastic Search
wget -qO - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' | sudo tee /etc/apt/sources.list.d/elastic.list

sudo add-apt-repository -y ppa:chris-lea/node.js
sudo apt-get update

sudo apt-get install -y python build-essential pkg-config git  \
python-pip python-virtualenv python-dev zlib1g-dev \
libffi-dev libyaml-dev libssl-dev nodejs openjdk-7-jre-headless elasticsearch

# Create swap file because ES eats up RAM and 14.04 doesn't have swap by default
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

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

sudo service elasticsearch start

realms-wiki start