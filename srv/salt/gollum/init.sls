ruby-repos:
  pkgrepo.managed:
    - ppa: brightbox/ruby-ng-experimental

ruby1.9.3:
  pkg.installed:
    - require:
      - pkgrepo.managed: ruby-repos

asciidoc:
  pkg.installed

{% for gem in ['gollum', 'creole', 'redcarpet', 'github-markdown', 'org-ruby', 'RedCloth', 'wikicloth'] %}
{{ gem }}-gem:
  gem:
    - installed
    - name: {{ gem }}
    - require:
      - pkg.installed: ruby1.9.3
{% endfor %}
