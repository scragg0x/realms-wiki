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

nginx-stable-repo:
  pkgrepo.managed:
    - ppa: nginx/stable
    - required_in: nginx

postgres-repo:
  pkgrepo.managed:
    - name: deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main
    - key_url: https://www.postgresql.org/media/keys/ACCC4CF8.asc
    - required_in: postgresql

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
      - libxslt1-dev
      - nodejs
      - supervisor
    - require:
      - pkgrepo.managed: nodejs-lea-repo
      - pkgrepo.managed: redis-lea-repo
      - pkgrepo.managed: python-redis-lea-repo
      - pkgrepo.managed: nginx-stable-repo
      - pkgrepo.managed: postgres-repo