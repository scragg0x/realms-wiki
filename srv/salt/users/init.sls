deploy:
  user.present:
    - shell: /bin/bash
    - home: /home/deploy
    - fullname: Deploy

sudo:
  pkg:
    - installed

/etc/sudoers.d/mysudoers:
  file.managed:
    - source: salt://users/mysudoers
    - mode: 440
    - user: root
    - group: root
    - require:
      - pkg: sudo

/home/deploy:
  file.directory:
    - user: deploy
    - group: deploy

/home/deploy/.bash_profile:
  file.managed:
    - source: salt://users/.bash_profile
    - mode: 440
    - user: deploy
    - group: deploy
    - require:
      - file.directory: /home/deploy

/home/deploy/.bashrc:
  file.copy:
    - mode: 440
    - user: deploy
    - group: deploy
    - source: /etc/skel/.bashrc

bashrc-append:
  file.append:
    - name: /home/deploy/.bashrc
    - text: . ~/.bash_profile