FROM realms/base

# Packages
RUN apt-get update && apt-get install -y build-essential python-pip python-virtualenv python-dev zlib1g-dev libffi-dev libyaml-dev

# lxml deps
# libxml2-dev libxslt1-dev

# Virtualenv
RUN virtualenv /home/deploy/realms-wiki/.venv

RUN cd /home/deploy/realms-wiki && .venv/bin/pip install realms-wiki

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
