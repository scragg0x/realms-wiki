/etc/supervisor/conf.d/realms.conf:
  file.managed:
    - source: salt://supervisor/supervisord.conf