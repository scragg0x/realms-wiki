rethink-repo:
  pkgrepo.managed:
    - ppa: rethinkdb/ppa

rethinkdb:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - reload: True
    - require:
      - pkg: rethinkdb

python-pip:
  pkg.installed

build-essential:
  pkg.installed

rethinkdb-pip:
  pip:
    - name: rethinkdb
    - installed
    - require:
      - pkg: python-pip
      - pkg: rethinkdb
      - pkg: build-essential
