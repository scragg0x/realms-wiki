FROM realms/base

# Packages
RUN add-apt-repository -y ppa:chris-lea/node.js && apt-get update
RUN apt-get install -y python build-essential git libpcre3-dev python-software-properties \
    python-pip python-virtualenv python-dev pkg-config curl libxml2-dev libxslt1-dev zlib1g-dev \
    libffi-dev nodejs libyaml-dev

# Realms Code
RUN cd /home/deploy && git clone https://github.com/scragg0x/realms-wiki

# Bower stuff for frontend assets
RUN npm install -g bower
RUN bower --allow-root --config.cwd=/home/deploy/realms-wiki --config.directory=realms/static/vendor --config.interactive=false install

# Virtualenv building
RUN virtualenv /home/deploy/realms-wiki/.venv
RUN /home/deploy/realms-wiki/.venv/bin/pip install /home/deploy/realms-wiki

# Logging
RUN mkdir /var/log/realms-wiki && chown deploy.deploy /var/log/realms-wiki

# Upstart
RUN mkdir /etc/service/realms-wiki
ADD realms-wiki.sh /etc/service/realms-wiki/run
RUN chmod +x /etc/service/realms-wiki/run

# Clear some fat
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Hand over to deploy user
RUN chown -R deploy.deploy /home/deploy

EXPOSE 5000
