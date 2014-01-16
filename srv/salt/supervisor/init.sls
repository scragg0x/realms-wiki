/etc/supervisor/conf.d/realms.conf:
  file.managed:
    - source: salt://supervisor/supervisord.conf

supervisor-run:
  cmd.run:
    - unless: test -e /tmp/supervisord.pid
    - name: /usr/local/bin/supervisord
    - require:
      - file.managed: /etc/supervisor/conf.d/realms.conf