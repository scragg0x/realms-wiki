postgresql:
  pkg.installed:
    - name: postgresql-9.3

libpq-dev:
  pkg.installed

createdb:
  cmd.run:
    - name: createdb -T template1 realms
    - user: postgres
    - require:
      - pkg.installed: postgresql-9.3

initdb:
  cmd.run:
    - name: psql realms < /srv/salt/postgres/init.sql
    - user: postgres
