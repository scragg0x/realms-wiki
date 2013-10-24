redis-server:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - reload: True
    - require:
      - pkg: redis-server