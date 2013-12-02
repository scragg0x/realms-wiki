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

