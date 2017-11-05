#!/bin/bash

# Provision script for Ubuntu 16.04
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -d "/vagrant" ]; then
  # Control will enter here if $DIRECTORY exists.
  APP_DIR="/vagrant"
fi

echo "Provisioning..."

sudo apt-get -qq update && sudo apt-get -y upgrade

# install deps
sudo apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev

# install pipenv
sudo pip install -U pipenv

# install node
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g bower

# Elastic Search
# wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
# echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-5.x.list
# sudo apt-get -qq update && sudo apt-get install -y elasticsearch

# Default cache is memoization

# Redis
# sudo add-apt-repository -y chris-lea/redis-server && sudo apt-get -qq update && sudo apt-get install -y redis-server

# Default DB is sqlite

# Mysql
# sudo apt-get install -y mysql-server mysql-client

# MariaDB
# sudo apt-get install -y mariadb-server mariadb-client

# Postgres
# sudo apt-get install -y postgresql postgresql-contrib

cd ${APP_DIR}

# install virtualenv and python deps
pipenv install --two

# install frontend deps
bower --config.interactive=false install
