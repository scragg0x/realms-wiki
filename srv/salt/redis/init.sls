redis-repos:
  pkgrepo.managed:
    - ppa: chris-lea/python-redis
    - ppa: brianmercer/redis

redis-server:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - reload: True
    - require:
      - pkg: redis-server
      - pkgrepo.managed: redis-repos
