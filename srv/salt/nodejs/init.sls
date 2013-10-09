node-repos:
  pkgrepo.managed:
    - ppa: chris-lea/node.js

nodejs:
  pkg:
  - installed
  - require:
    - pkgrepo.managed: node-repos