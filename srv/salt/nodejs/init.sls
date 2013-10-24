nodejs:
  pkg.installed

nodejs-dev:
  pkg.installed

npm:
  pkg.installed

bower:
  npm.installed:
    - require:
      - pkg.installed: npm