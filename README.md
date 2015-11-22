# Realms Wiki Beta

Git based wiki written in Python
Inspired by [Gollum][gollum], [Ghost][ghost], and [Dillinger][dillinger].
Basic authentication and registration included.

Demo: http://realms.io
This domain is being used temporarily as a demo so expect it to change.

Source: https://github.com/scragg0x/realms-wiki

## Features

- Built with Bootstrap 3.
- Markdown (w/ HTML Support).
- Syntax highlighting (Ace Editor).
- Live preview.
- Collaboration (TogetherJS / Firepad).
- Drafts saved to local storage.
- Handlebars for templates and logic.

## Screenshots

[<img src="https://db.tt/Q2XHGRnT" width=340 />](https://db.tt/Q2XHGRnT)&nbsp;[<img  width=340 src="https://db.tt/pIZ4w2oN" />](https://db.tt/pIZ4w2oN)&nbsp;[<img  width=340 src="https://db.tt/ERLmDHrk" />](https://db.tt/ERLmDHrk)&nbsp;[<img width=340 src="https://db.tt/Ls08ocLh" />](https://db.tt/Ls08ocLh)&nbsp;[<img width=340 src="https://db.tt/7QVfXFQ4" />](https://db.tt/7QVfXFQ4)&nbsp;[<img width=340 src="https://db.tt/Lna3BOm1" />](https://db.tt/Lna3BOm1)

## Requirements

- Python 2.7

### Optional

- Nginx (if you want proxy requests, this is recommended).
- Memcached or Redis, default is memonization.
- MariaDB, MySQL, Postgresql, or another database supported by SQLAlchemy, default is sqlite.
    Anon or single user does not require a database.

## Installation

### Requirements installation

You will need the following packages to get started:

#### Ubuntu

    sudo apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev

#### CentOS / RHEL

    yum install -y python-pip python-devel.x86_64 libxslt-devel.x86_64 libxml2-devel.x86_64 libffi-devel.x86_64 libyaml-devel.x86_64 libxslt-devel.x86_64 zlib-devel.x86_64 openssl-devel.x86_64 openldap2-devel cyrus-sasl-devel python-pbr gcc
    
#### OSX / Windows

This app is designed for Linux and I recommend using Vagrant to install on OSX or Windows.

### Realms Wiki installation via PyPI

The easiest way. Install it using Python Package Index:

    pip install realms-wiki

### Realms Wiki installation via Git

#### Ubuntu

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki

    sudo apt-get install -y software-properties-common python-software-properties
    sudo add-apt-repository -y ppa:chris-lea/node.js
    sudo apt-get update
    sudo apt-get install -y nodejs python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev
    sudo npm install -g bower
    bower install

    virtualenv .venv
    source .venv/bin/activate

    pip install -r requirements.txt
    realms-wiki start
    
NodeJS is required for installing [bower](http://bower.io) and it's used for pulling front end dependencies.

### Realms Wiki via Vagrant

Vagrantfile is included for development or running locally.
To get started with Vagrant, download and install Vagrant and VirtualBox for your platform with the links provided:

- https://www.vagrantup.com/downloads.html
- https://www.virtualbox.org/wiki/Downloads

Then execute the following in the terminal:

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki
    vagrant up

Check [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to make sure it's running.

### Realms Wiki via Docker

Make sure you have docker installed. http://docs.docker.com/installation/
Here is an example run command, it will pull the image from docker hub initially.

    docker run --name realms-wiki -p 5000:5000 -d realms/realms-wiki
    
You can build your own image if you want. Mine is based off https://github.com/phusion/baseimage-docker
The Dockerfile is located in [docker/Dockerfile](docker/Dockerfile) `realms/base` just creates the deploy user.

## Config and Setup

You should be able to run the wiki without configuration using the default config values.
You may want to customize your app and the easiest way is the setup command:

    realms-wiki setup
    
This will ask you questions and create a `realms-wiki.json` file.
You can manually edit this file as well.
Any config value set in `realms-wiki.json` will override values set in `realms/config/__init__.py`.

### Nginx Setup

    sudo apt-get install -y nginx

Create a file called `realms.conf` in `/etc/nginx/conf.d`

    sudo nano /etc/nginx/conf.d/realms.conf

Put the following sample configuration in that file:

    server {
      listen 80;
      
      # Your domain here
      server_name wiki.example.org;
      
      # Settings to by-pass for static files 
      location ^~ /static/  {
        # Example:
        root /full/path/to/realms/;
      }
        
      location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
      
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
      }
    }


Test Nginx config:
    
    sudo nginx -t

Reload Nginx:

    sudo service nginx reload

### Apache + mod_wsgi Setup

    sudo apt-get install -y apache2 libapache2-mod-wsgi

Create a virtual host configuration in `/etc/apache2/sites-available/realms_vhost`

    <VirtualHost *:80>
        ServerName wiki.example.org

        WSGIDaemonProcess realms_wsgi display-name=%{GROUP}
        WSGIProcessGroup realms_wsgi
        WSGIScriptAlias / /var/www/my-realms-dir/wsgi.py

        Alias /static /full/path/to/realms/static
    </VirtualHost>

Create `/var/www/my-realms-dir/wsgi.py`

    import os
    import site

    # Uncomment the following lines if you are using a virtual environment

    # ----------------------------------
    # Enter path to your virtualenv's site-packages directory
    # VENV_SITE_DIR = ".venv/lib/python2.7/site-packages"
    # PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    # site.addsitedir(os.path.abspath(os.path.join(PROJECT_ROOT, VENV_SITE_DIR)))
    # ----------------------------------

    from realms import create_app
    application = create_app()

Enable the virtual host:

    sudo a2ensite realms_vhost

Test your configuration:

    apache2ctl configtest

Reload apache:

    sudo service apache2 reload

### MySQL Setup
    
    sudo apt-get install -y mysql-server mysql-client libmysqlclient-dev
    realms-wiki pip install python-memcached
    
### MariaDB Setup
    
    sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
    realms-wiki pip install MySQL-Python

### Postgres Setup

    sudo apt-get install -y libpq-dev postgresql postgresql-contrib postgresql-client
    realms-wiki pip install psycopg2

_Don't forget to create your database._

## Search

Realms wiki comes with basic search capabilities, however this is not recommended
for large wikis or if you require more advanced search capabilities.
We currently support Elasticsearch and Whoosh as alternative backend.

### Elasticsearch Setup

There are multiple ways to install/run Elasticsearch. An easy way is to use your their
repositories.  

**apt**

    wget -qO - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch.list
    apt-get update && apt-get install elasticsearch
    
For `yum` instructions or more details, follow the link below:

http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html

**Configuring Elasticsearch**

In your Realms Config, have the following options set:

    "SEARCH_TYPE": "elasticsearch"
    "ELASTICSEARCH_URL": "http://127.0.0.1:9200"

Optionally, also set the following option to configure which fields are searchable:

    "ELASTICSEARCH_FIELDS": ["name"]

Allowable values are `"name"`, `"content"`, `"username"`, `"message"`. The default is `["name"]`.

### Whoosh Setup

Simply install Whoosh to your Python environment, e.g.

    pip install Whoosh

**Configuring Whoosh**

To use Whoosh, set the following in your Realms config:

    "SEARCH_TYPE": "whoosh"
    "WHOOSH_INDEX": "/path/to/your/whoosh/index"
    "WHOOSH_LANGUAGE": "en"

WHOOSH_INDEX has to be a path readable and writeable by Realm's user. It will be created automatically if it doesn't exist.

Whoosh is set up to use language optimization, so set WHOOSH_LANGUAGE to the language used in your wiki. For available languages, check `whoosh.lang.languages`.
If your language is not supported, Realms will fall back to a simple text analyzer.

## Authentication

### Local

Local default will be done using a backend database as defined in the config.
To disable local authentication, put the following your config.

    "AUTH_LOCAL_ENABLE": false


### LDAP (beta)

Realms uses the following library to authenticate using LDAP.  https://github.com/ContinuumIO/flask-ldap-login
It supports direct bind and bind by search. 
Use these examples as a guide and place it in your realms-wiki.json config.


#### Bind By Search Example

In this example, BIND_DN and BIND_AUTH are used to search and authenticate.  Leaving them blank implies anonymous authentication.

    "LDAP": {
        "URI": "ldap://localhost:8389",
        "BIND_DN": "",
        "BIND_AUTH": "",
        "USER_SEARCH": {"base": "dc=realms,dc=io", "filter": "uid=%(username)s"},
        "KEY_MAP": {
            "username":"cn",
            "email": "mail"
        }
    }

#### Direct Bind Example

    "LDAP": {
        "URI": "ldap://localhost:8389",
        "BIND_DN": "uid=%(username)s,ou=People,dc=realms,dc=io",
        "KEY_MAP": {
            "username":"cn",
            "email": "mail",
        },
        "OPTIONS": {
            "OPT_PROTOCOL_VERSION": 3,
        }
    }


### OAuth (beta)

Realms currently supports Github, Twitter, Facebook and Google.  Each provider requires a key and secret.
Put them in your `realms-wiki.json` config file.  Use the example below.

    "OAUTH": {
        "twitter": {
            "key": "",
            "secret": ""
        },
        "github": {
            "key": "",
            "secret": ""
        }
    }

## Running

    realms-wiki start
    
### Upstart
    
Setup upstart with this command:

    sudo realms-wiki setup_upstart

This command requires root priveleges because it creates an upstart script.
Also note that ports below `1024` require user root.
After your config is in place use the following commands:

    sudo start realms-wiki
    sudo stop realms-wiki
    sudo restart realms-wiki
    

### Development mode

This will start the server in the foreground with auto reloaded enabled:

    realms-wiki dev

### Other commands

    Usage: realms-wiki [OPTIONS] COMMAND [ARGS]...
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      auth
      configure      Set config.json, expects JSON encoded string
      create_db      Creates DB tables
      dev            Run development server
      drop_db        Drops DB tables
      pip            Execute pip commands, useful for virtualenvs
      restart        Restart server
      run            Run production server (alias for start)
      setup          Start setup wizard
      setup_upstart  Start upstart conf creation wizard
      start          Run server daemon
      status         Get server status
      stop           Stop server
      test           Run tests
      version        Output version

Access from your browser:

http://localhost:5000

## Templating

Realms uses Handlebars partials to create templates.
Each page that you create can be imported as a partial.

This page imports and uses a partial:

http://realms.io/_edit/hbs

This page contains the content of the partial:

http://realms.io/_edit/example-tmpl
    
I locked these pages to preserve them.  
You can copy and paste into a new page for testing purposes.

## Contributing

Issues and pull requests are welcome.
Please follow the code style guide.

[Python style guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)

## Author

Matthew Scragg <scragg@gmail.com>

[gollum]: https://github.com/gollum/gollum
[ghost]: https://github.com/tryghost/Ghost
[dillinger]: https://github.com/joemccann/dillinger/
