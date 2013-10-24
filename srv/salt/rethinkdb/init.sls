rethink-repo:
  pkgrepo.managed:
    - ppa: rethinkdb/ppa

rethinkdb:
  user.present:
    - shell: /bin/bash
    - home: /home/rethinkdb
  pkg:
    - installed

rethinkdb-pip:
  pip:
    - name: rethinkdb
    - installed
    - require:
      - pkg: python-pip
      - pkg: rethinkdb
      - pkg: build-essential

/etc/rethinkdb/rdb0.conf:
  file.managed:
    - source: salt://rethinkdb/rdb0.conf
