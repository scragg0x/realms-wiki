extra-repos:
  pkgrepo.managed:
    - ppa: chris-lea/python-redis
    - ppa: brianmercer/redis
    - ppa: chris-lea/node.js
    - ppa: nginx/stable

common-pkgs:
  pkg.installed:
    - pkgs:
      - python
      - vim
      - build-essential
      - screen
      - htop
      - git
      - ntp
      - libpcre3-dev
      - libevent-dev
      - iptraf
      - python-software-properties
      - python-pip
      - python-virtualenv
      - python-dev
      - pkg-config
      - curl
      - libxml2-dev
      - libxslt-dev
    - require:
      - pkgrepo.managed: extra-repos