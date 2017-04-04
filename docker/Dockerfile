FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get install -y software-properties-common python-software-properties build-essential\
    python python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev \
    pkg-config libssl-dev libsasl2-dev libldap2-dev git python-virtualenv && \
    add-apt-repository -y ppa:chris-lea/node.js && \
    apt-get install -y npm nodejs && \
    apt-get clean  && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    npm install -g bower clean-css@3 && \
    useradd -ms /bin/bash wiki && \
    gpasswd -a wiki sudo

# copy the cloned repo recursively
COPY ./ /home/wiki/realms-wiki/
RUN chown -R wiki:wiki /home/wiki && \
    echo "wiki:wiki" | chpasswd && \
    echo "wiki    ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers

USER wiki

WORKDIR /home/wiki/realms-wiki/

RUN virtualenv /home/wiki/realms-wiki/.venv && \
    . /home/wiki/realms-wiki/.venv/bin/activate && \
    bower --config.interactive=false install && \
    pip install -r requirements.txt && \
    mkdir /home/wiki/data && \
    touch /home/wiki/data/.a

ENV WORKERS=3
ENV GEVENT_RESOLVER=ares

ENV REALMS_ENV=docker
ENV REALMS_WIKI_PATH=/home/wiki/data/repo
ENV REALMS_DB_URI='sqlite:////home/wiki/data/wiki.db'

VOLUME /home/wiki/data

EXPOSE 5000

RUN /home/wiki/realms-wiki/.venv/bin/realms-wiki create_db && \
    echo '#!/bin/bash \n\
/home/wiki/realms-wiki/.venv/bin/realms-wiki $@ \n' >> /tmp/realms-wiki && \
    sudo mv /tmp/realms-wiki /usr/local/bin && \
    sudo chmod +x /usr/local/bin/realms-wiki

CMD . /home/wiki/realms-wiki/.venv/bin/activate && \
    gunicorn \
        --name realms-wiki \
        --access-logfile - \
        --error-logfile - \
        --worker-class gevent \
        --workers ${WORKERS} \
        --bind 0.0.0.0:5000 \
        --chdir /home/wiki/realms-wiki \
        'realms:create_app()'
#    /usr/local/bin/realms-wiki start
