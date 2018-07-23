FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

# install prereqs
RUN apt-get -qq update && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get install -y sudo git curl python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev

# install pipenv
RUN pip install -U pipenv

# install node
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g bower clean-css@3

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# create wiki user
RUN useradd -ms /bin/bash wiki && gpasswd -a wiki sudo

# copy the cloned repo recursively
COPY ./ /home/wiki/realms-wiki/
RUN chown -R wiki:wiki /home/wiki && \
    echo "wiki:wiki" | chpasswd && \
    echo "wiki    ALL=(ALL:ALL) NOPASSWD: ALL" | tee -a /etc/sudoers

USER wiki

WORKDIR /home/wiki/realms-wiki/

<<<<<<< HEAD
=======
ENV PIPENV_VENV_IN_PROJECT=1

RUN virtualenv /home/wiki/realms-wiki/.venv && \
    . /home/wiki/realms-wiki/.venv/bin/activate && \
    bower --config.interactive=false install && \
    pip install pipenv && \
    pipenv install --two && \
    pipenv run python /home/wiki/realms-wiki/setup.py install && \
    mkdir /home/wiki/data && \
    touch /home/wiki/data/.a

>>>>>>> deps: update gunicorn, markdown2
ENV WORKERS=3
ENV GEVENT_RESOLVER=ares

ENV REALMS_ENV=docker
ENV REALMS_WIKI_PATH=/home/wiki/data/repo
ENV REALMS_DB_URI='sqlite:////home/wiki/data/wiki.db'
ENV PIPENV_VENV_IN_PROJECT=1

RUN pipenv install --two --dev && \
    bower --config.interactive=false install && \
    mkdir /home/wiki/data

RUN pipenv run python setup.py install

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
