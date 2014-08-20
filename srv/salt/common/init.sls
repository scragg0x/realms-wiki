redis-lea-repo:
  pkgrepo.managed:
    - ppa: chris-lea/redis-server
    - required_in: redis-server

nodejs-lea-repo:
  pkgrepo.managed:
    - ppa: chris-lea/node.js

python-redis-lea-repo:
  pkgrepo.managed:
    - ppa: chris-lea/python-redis

common-pkgs:
  pkg.installed:
    - pkgs:
      - python
      - build-essential
      - git
      - libpcre3-dev
      - libevent-dev
      - python-software-properties
      - python-pip
      - python-virtualenv
      - python-dev
      - pkg-config
      - curl
      - libxml2-dev
      - libxslt1-dev
      - zlib1g-dev
      - libffi-dev
      - nodejs
    - require:
      - pkgrepo: nodejs-lea-repo
      - pkgrepo: redis-lea-repo
      - pkgrepo: python-redis-lea-repo
