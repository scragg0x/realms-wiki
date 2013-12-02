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

realms-repo:
  git.latest:
    - unless: test -e /vagrant
    - name: git@github.com:scragg0x/realms.git
    - target: /home/deploy
    - rev: master
    - user: deploy
    - identity: /home/deploy/.ssh/id_rsa

/home/deploy/virtualenvs/realms:
  virtualenv.managed:
    - requirements: /home/deploy/realms/requirements.txt
    - cwd: /home/deploy/realms
    - runas: deploy

