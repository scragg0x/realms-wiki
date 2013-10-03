python-pkgs:
  pkg.installed:
    - pkgs:
      - python-dev
      - python-pip
      - build-essential

{% for pkg in ['tornado', 'pyzmq', 'itsdangerous', 'boto', 'redis', 'simplejson', 'sockjs-tornado', 'flask', 'flask-bcrypt', 'flask-login', 'flask-assets', 'gittle', 'gevent', 'lxml', 'markdown2', 'recaptcha-client', 'RethinkORM' ] %}
{{ pkg }}-pip:
  pip:
    - name: {{ pkg }}
    - installed
    - require:
      - pkg.installed: common-pkgs
{% endfor %}