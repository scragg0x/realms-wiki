deploy:
  user.present:
    - shell: /bin/bash
    - home: /home/deploy
    - fullname: Deploy

sudo:
  pkg:
    - installed

/etc/sudoes.d/mysudoers:
  file:
    - managed
    - source: salt://users/mysudoers
    - mode: 440
    - user: root
    - group: root
    - require:
      - pkg: sudo
