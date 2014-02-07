python-dev:
  pkg.installed

build-essential:
  pkg.installed

python-pip:
  pkg.installed

virtualenvwrapper:
  pip.installed:
    - require:
      - pkg: python-pip

bower:
  npm.installed:
    - user: root
    - require:
      - pkg.installed: common-pkgs

uglify-js:
  npm.installed:
    - user: root
    - require:
      - pkg.installed: common-pkgs

create_virtualenv:
  virtualenv.managed:
    - name: /home/deploy/virtualenvs/realms
    - requirements: /home/deploy/realms/requirements.txt
    - cwd: /home/deploy/realms
    - user: root

vagrant_ownership:
  cmd.run:
    - name: chown -R vagrant.vagrant /home/deploy
    - onlyif: test -d /vagrant
    - user: root

deploy_ownership:
  cmd.run:
    - name: chown -R vagrant.vagrant /home/deploy
    - unless: test -d /vagrant
    - user: root
