rethinkdb-repo:
  pkgrepo.managed:
    - name: 'deb http://ppa.launchpad.net/rethinkdb/ppa/ubuntu precise main'

rethinkdb:
  pkg.installed:
    - require:
      - pkgrepo.managed: rethinkdb-repo

rethinkdb-user:
  user.present:
    - name: rethinkdb
    - shell: /bin/bash
    - home: /home/rethinkdb

rethinkdb-pip:
  pip:
    - name: rethinkdb
    - installed
    - require:
      - pkg: python-pip
      - pkg: rethinkdb
      - pkg: build-essential

/home/rethinkdb/rdb0:
  file.directory:
    - user: rethinkdb
    - group: rethinkdb
    - makedirs: True

/etc/rethinkdb/instances.d/rdb0.conf:
  file.managed:
    - source: salt://rethinkdb/rdb0.conf

rethinkdb-service:
  service.running:
    - name: rethinkdb
    - enable: True
    - reload: True
    - watch:
      - file.managed: /etc/rethinkdb/instances.d/rdb0.conf