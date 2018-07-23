# Realms Wiki Beta

Git based wiki written in Python
Inspired by [Gollum][gollum], [Ghost][ghost], and [Dillinger][dillinger].
Basic authentication and registration included.

Demo: http://realms.io

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

[<img src="https://storage.googleapis.com/realms-wiki/img/1.png" width=340 />](https://storage.googleapis.com/realms-wiki/img/1.png)&nbsp;[<img  width=340 src="https://storage.googleapis.com/realms-wiki/img/2.png" />](https://storage.googleapis.com/realms-wiki/img/2.png)&nbsp;[<img  width=340 src="https://storage.googleapis.com/realms-wiki/img/3.png" />](https://storage.googleapis.com/realms-wiki/img/3.png)&nbsp;[<img width=340 src="https://storage.googleapis.com/realms-wiki/img/4.png" />](https://storage.googleapis.com/realms-wiki/img/4.png)&nbsp;[<img width=340 src="https://storage.googleapis.com/realms-wiki/img/5.png" />](https://storage.googleapis.com/realms-wiki/img/5.png)&nbsp;[<img width=340 src="https://storage.googleapis.com/realms-wiki/img/6.png" />](https://storage.googleapis.com/realms-wiki/img/6.png)

### File Uploads

When an S3 bucket is setup in the configuration, you can upload files by dropping them into the wiki page. Files are stored in S3 and downloads use signed urls so the bucket does not need to be public. Attachments are stored in the front matter of the page. 

```
---
attachments:
- filename: data_export-out_v4.csv
  handler: S3
  key: wiki/files/201807120616_F8sZrW/data_export-out_v4.csv
---


# Test Page

This is a test example page. 
```

![](https://raw.githubusercontent.com/thomaskcr/realms-wiki/master/docs/screenshot-filemanager.png)


## Requirements

- Python 2.7 (Python 3.x is a WIP)

### Optional

- Nginx (if you want proxy requests, this is recommended).
- Memcached or Redis, default is memonization.
- MariaDB, MySQL, Postgresql, or another database supported by SQLAlchemy, default is sqlite.
    Anon or single user does not require a database.

## Installation

You will need the following packages to get started:

#### Ubuntu 16.04

    sudo apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev

#### CentOS / RHEL

    yum install -y python-pip python-devel.x86_64 libxslt-devel.x86_64 libxml2-devel.x86_64 libffi-devel.x86_64 libyaml-devel.x86_64 libxslt-devel.x86_64 zlib-devel.x86_64 openssl-devel.x86_64 openldap2-devel cyrus-sasl-devel python-pbr gcc
    
#### OSX / Windows

This app is designed for Linux. Vagrant can be used to run on OSX/Windows host.

### Realms Wiki installation via PyPI

The easiest way. Install it using Python Package Index:

    pip install realms-wiki

### Realms Wiki installation via Git

#### Ubuntu

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki

    curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    sudo apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev libsasl2-dev libldap2-dev
    sudo npm install -g bower
    bower install

    sudo pip install -U pipenv
    pipenv install --two

    # development
    pipenv run python realms-wiki dev

    # install / start
    pipenv run python setup.py install
    pipenv run realms-wiki start
    
NodeJS is required for installing [bower](http://bower.io) and it's used for pulling front end dependencies.

### Vagrant

Vagrantfile is included for development and testing with compatible backends.
To get started with Vagrant, download and install Vagrant and VirtualBox for your platform with the links provided:

- https://www.vagrantup.com/downloads.html
- https://www.virtualbox.org/wiki/Downloads

### Realms Wiki via Docker

Make sure you have docker installed. http://docs.docker.com/installation/
Here is an example run command, it will pull the image from docker hub initially.

    docker run --name realms-wiki -p 5000:5000 -d realms/realms-wiki
    
The Dockerfile is located in [docker/Dockerfile](docker/Dockerfile)

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

**Installing Elasticsearch**

https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html

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

Realms can authenticate users with a LDAP directory. It supports "direct bind" and "bind by search". 

Use these examples as a guide and place it in your realms-wiki.json config.

An optional KEY_MAP can be used to map LDAP attributes to the Realms user object.

#### "Bind by search" example

In this example, BIND_DN and BIND_AUTH are used to bind to the LDAP directory (omit them for anonymous bind).
After binding, a LDAP SEARCH is performed using the template "USER_SEARCH". In this template, `%(username)s` is the
UserID that the user entered in the Realms authentication form. If the user is found in LDAP, a final BIND is tried
with his credentials to check the password.


    "LDAP": {
        "URI": "ldap://127.0.0.1:389",
        "BIND_DN": "cn=realms,ou=apps,dc=realms,dc=io",
        "BIND_AUTH": "wlvksdfknv:dsqc9893",
        "USER_SEARCH": {"base": "ou=users, dc=realms,dc=io", "filter": "(uid=%(username)s)"},
        "KEY_MAP": {
            "username": "cn",
            "email": "mail"
        }
    }

#### "Direct bind" example

Here authentication is just a simple BIND using the user's credentials. The user DN is given by the BIND_DN template.
In this template, `%(username)s` is the UserID that the user entered in the Realms authentication form.

    "LDAP": {
        "URI": "ldap://127.0.0.1:389",
        "BIND_DN": "uid=%(username)s,ou=People,dc=realms,dc=io",
        "KEY_MAP": {
            "username": "cn",
            "email": "mail",
        }
    }

#### LDAP/TLS

(for brevity we don't repeat the Bind By Search configurations or the KEY_MAP, but they can be used with TLS too)

LDAP over TLS is typically done like this:

    "LDAP": {
        "URI": "ldaps://127.0.0.1:686",
        "BIND_DN": "uid=%(username)s,ou=People,dc=realms,dc=io",
        "TLS_OPTIONS": {
            "CA_CERTS_FILE": "PATH TO THE CERTIFICATE PEM OF THE AUTHORITY THAT SIGNED THE LDAP SERVER CERTIFICATE"
        }
    }

If the LDAP server certificate has been emitted by an authority that's trusted at system-level (and your Python version
is not too old), it might be possible to omit `CA_CERTS_FILE`.

If you don't want Realms to validate at all the LDAP server certificate (don't do that in production), pass an
additional VALIDATE option:

    "LDAP": {
        "URI": "ldaps://127.0.0.1:686",
        "BIND_DN": "uid=%(username)s,ou=People,dc=realms,dc=io",
        "TLS_OPTIONS": {
            "VALIDATE": "NONE"
        }        
    }

#### LDAP with START_TLS

It is similar to LDAP/TLS. Just add a START_TLS option:

    "LDAP": {
        "URI": "ldap://127.0.0.1:389",
        "BIND_DN": "uid=%(username)s,ou=People,dc=realms,dc=io",
        "CA_CERTS_FILE": "PATH TO THE CERTIFICATE PEM OF THE AUTHORITY THAT SIGNED THE LDAP SERVER CERTIFICATE",
        "TLS_OPTIONS": {
            "CA_CERTS_FILE": "PATH TO THE CERTIFICATE PEM OF THE AUTHORITY THAT SIGNED THE LDAP SERVER CERTIFICATE"
        }
        "START_TLS": true
    }

The VALIDATE option can be used here too.

#### Configuration change for TLS

Please note that the TLS/START_TLS configuration changed from previous versions of Realms. The old way that was from
flask-ldap-login using LDAP options like `OPT_X_TLS_REQUIRE_CERT` does not work anymore.

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
        },
        "google": {
            "key": "",
            "secret": "",
            "domain": ""    # this is optional if you want to restrict to a GSuite domain
    }

### Authentication by reverse proxy

If you configured realms behind a reverse-proxy or a single-sign-on, it is possible to delegate authentication to
the proxy.

    "AUTH_PROXY": true
    
Note: of course with that setup you must ensure that **Realms is only accessible through the proxy**.

Example Nginx configuration:
    
    location / {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header REMOTE_USER $remote_user;
    
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
    }    
    
By default, Realms will look for the user ID in `REMOTE_USER` HTTP header. You can specify another header name with:

    "AUTH_PROXY_HEADER_NAME": "LOGGED_IN_USER"
    


## Running

    realms-wiki start
    
### Upstart (Ubuntu 14.04)
    
Setup upstart with this command:

    sudo realms-wiki setup_upstart

This command requires root priveleges because it creates an upstart script.
Also note that ports below `1024` require user root.
After your config is in place use the following commands:

    sudo start realms-wiki
    sudo stop realms-wiki
    sudo restart realms-wiki
    
### Systemd (Ubuntu 16.04)
    
Setup systemd by creating the file **/etc/systemd/system/realms-wiki.service**:

    [Unit]
    Description=Realms Wiki

    [Service]
    User=ubuntu
    Group=ssl-cert
    Type=forking

    ExecStart=/home/ubuntu/realms-wiki/.venv/bin/python /home/ubuntu/realms-wiki/.venv/bin/gunicorn \
    --certfile=/etc/ssl/certs/ssl-cert-snakeoil.pem   \
    --keyfile=/etc/ssl/private/ssl-cert-snakeoil.key  \
    --name realms-wiki     \
    --access-logfile -     \
    --error-logfile -      \
    --worker-class gevent  \
    --workers 5            \
    --bind 0.0.0.0:5000    \
    --user ubuntu          \
    --group ssl-cert       \
    --chdir /home/ubuntu/realms-wiki/.venv  \
    'realms:create_app()'

    Restart=on-failure
    LimitNOFILE=65335
    WorkingDirectory=/home/ubuntu/realms-wiki/.venv
    Environment=PATH=/home/ubuntu/realms-wiki/.venv/bin:/usr/local/bin:/usr/bin:/bin:$PATH
    Environment=LC_ALL=en_US.UTF-8
    Environment=GEVENT_RESOLVER=ares

    [Install]
    WantedBy=multi-user.target

This file must be created as user root. Also note that ports below `1024` 
require user root.

Globally replace /home/ubuntu/realms-wiki/ in the example above with your local 
Realms-wiki install path.

Note that this example uses the HTTPS (SSL) support built in to gunicorn.
It references the self-signed certificate that gets created if you run 
**sudo apt-get install ssl-cert**. The private key is only visible to the group 
ssl-cert, so in this example gunicorn runs with group *ssl-cert*.

Finally, let systemd know about the new config file:

    sudo systemctl daemon-reload

After your config is in place use the following commands:
    
    sudo systemctl start realms-wiki.service
    sudo systemctl stop realms-wiki.service
    sudo systemctl restart realms-wiki.service
    
    # Enable auto-start of this service on reboot:
    sudo systemctl enable realms-wiki.service

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

[Python style guide](https://www.python.org/dev/peps/pep-0008/)

## Author

Matthew Scragg <scragg@gmail.com>

[gollum]: https://github.com/gollum/gollum
[ghost]: https://github.com/tryghost/Ghost
[dillinger]: https://github.com/joemccann/dillinger/
