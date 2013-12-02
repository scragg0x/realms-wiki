nginx:
  pkg:
    - installed
  service.running:
    - enable: True
    - reload: True
    - require:
      - pkg: nginx
    - watch:
      - file: /etc/nginx/conf.d/realms.conf

/etc/nginx/conf.d/realms.conf:
  file.managed:
    - template: jinja
    - source: salt://nginx/nginx.conf