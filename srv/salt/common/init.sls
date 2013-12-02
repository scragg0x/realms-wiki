redis-lea-repo:
  pkgrepo.managed:
    - name: 'deb http://ppa.launchpad.net/chris-lea/redis-server/ubuntu precise main'

nodejs-lea-repo:
  pkgrepo.managed:
    - name: 'deb http://ppa.launchpad.net/chris-lea/node.js/ubuntu precise main'

python-redis-lea-repo:
  pkgrepo.managed:
    - name: 'deb http://ppa.launchpad.net/chris-lea/python-redis/ubuntu precise main'

nginx-stable-repo:
  pkgrepo.managed:
    - name: 'deb http://ppa.launchpad.net/nginx/stable/ubuntu  precise main'

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
    - require:
      - pkgrepo.managed: nodejs-lea-repo
      - pkgrepo.managed: redis-lea-repo
      - pkgrepo.managed: python-redis-lea-repo
      - pkgrepo.managed: nginx-stable-repo