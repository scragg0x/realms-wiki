/etc/supervisord.conf:
  file.managed:
    - source: salt://supervisor/supervisord.conf


supervisor-pip:
  pip:
    - name: supervisor
    - installed
    - require:
      - pkg.installed: python-pip

supervisor-run:
  cmd.run:
    - unless: test -e /tmp/supervisord.pid
    - name: /usr/local/bin/supervisord
    - require:
      - file.managed: /etc/supervisord.conf
      - file.managed: /etc/rethinkdb/rdb0.conf