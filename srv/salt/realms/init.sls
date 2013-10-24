python-dev:
  pkg.installed

python-pip:
  pkg.installed

build-essential:
  pkg.installed

realms-repo:
  git.latest:
    - unless: test -e /vagrant
    - name: git@github.com:scragg0x/realms.git
    - target: /home/deploy
    - rev: master
    - user: deploy
    - identity: /home/deploy/.ssh/id_rsa

realms-link:
  cmd.run:
    - onlyif: test -e /vagrant
    - name: ln -s /vagrant /home/deploy/realms

/home/deploy/virtualenvs/realms:
  file.directory:
    - user: deploy
    - group: deploy
    - makedirs: True
    - recurse:
      - user
      - group
    - require:
      - user.present: deploy
  virtualenv.managed:
    - name: /home/deploy/virtualenvs/realms
    - requirements: /home/deploy/realms/requirements.txt
    - watch:
      - git: realms-repo
    - require:
      - file.directory: /home/deploy/virtualenvs/realms