FROM ubuntu:trusty

RUN apt-get update
RUN    apt-get install -y software-properties-common python-software-properties python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev npm git python-virtualenv && \
    apt-get clean  && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN ln -s /usr/bin/nodejs /usr/bin/node && \
    npm install -g bower

RUN useradd -ms /bin/bash wiki

USER wiki

RUN git clone https://github.com/scragg0x/realms-wiki /home/wiki/realms-wiki

WORKDIR /home/wiki/realms-wiki

RUN virtualenv .venv && \
    . .venv/bin/activate && \
    pip install -r requirements.txt

RUN bower install

ENV WORKERS=3
ENV GEVENT_RESOLVER=ares

ENV REALMS_ENV=docker
ENV REALMS_WIKI_PATH=/home/wiki/data/repo
ENV REALMS_DB_URI='sqlite:////home/wiki/data/wiki.db'
ENV REALMS_SQLALCHEMY_DATABASE_URI=${REALMS_DB_URI}

RUN mkdir /home/wiki/data && touch /home/wiki/data/.a
VOLUME /home/wiki/data

EXPOSE 5000

CMD . .venv/bin/activate && \
    gunicorn \
        --name realms-wiki \
        --access-logfile - \
        --error-logfile - \
        --worker-class gevent \
        --workers ${WORKERS} \
        --bind 0.0.0.0:5000 \
        --chdir /home/wiki/realms-wiki \
        'realms:create_app()'

