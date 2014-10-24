# Realms Wiki Beta

Git based wiki written in Python
Inspired by [Gollum][gollum], [Ghost][ghost], and [Dillinger][dillinger].
Basic authentication and registration included.

Demo: http://realms.io
This domain is being used temporarily as a demo so expect it to change.

Source: https://github.com/scragg0x/realms-wiki

## Features

- Built with Bootstrap 3
- Markdown (w/ HTML Support)
- Syntax highlighting (Ace Editor)
- Live preview
- Collaboration (TogetherJS / Firepad)
- Drafts saved to local storage
- Handlebars for templates and logic

## Screenshots

[<img src="https://db.tt/Q2XHGRnT" width=340 />](https://db.tt/Q2XHGRnT)&nbsp;[<img  width=340 src="https://db.tt/pIZ4w2oN" />](https://db.tt/pIZ4w2oN)&nbsp;[<img  width=340 src="https://db.tt/ERLmDHrk" />](https://db.tt/ERLmDHrk)&nbsp;[<img width=340 src="https://db.tt/Ls08ocLh" />](https://db.tt/Ls08ocLh)&nbsp;[<img width=340 src="https://db.tt/7QVfXFQ4" />](https://db.tt/7QVfXFQ4)&nbsp;[<img width=340 src="https://db.tt/Lna3BOm1" />](https://db.tt/Lna3BOm1)

## Requirements

- Python 2.7

### Optional

- Nginx (if you want proxy requests, this is recommended)
- Memcached or Redis, default is memonization
- MariaDB, MySQL, Postgresql, or another database supported by SQLAlchemy, default is sqlite.  
Anon or single user does not require a database.

## Installation

You will need to following packages to get started

    sudo apt-get install -y python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev

### Install from Pypi

Easiest way.

    pip install realms-wiki

### Installing from Git (Ubuntu)

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki

    sudo apt-get install -y software-properties-common python-software-properties
    sudo add-apt-repository -y ppa:chris-lea/node.js
    sudo apt-get update
    sudo apt-get install -y nodejs python-pip python-dev libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libyaml-dev libssl-dev
    sudo npm install -g bower
    bower install

    virtualenv .venv
    source .venv/bin/activate

    pip install -r requirements.txt
    realms-wiki start
    
NodeJS is for installing [bower](http://bower.io) and it's used for pulling front end dependencies

### OSX / Windows

This app is designed for Linux and I recommend using Vagrant to install on OSX or Windows.

### Vagrant

Vagrantfile is included for development or running locally.
To get started with Vagrant, download and install Vagrant and Virtualbox for your platform with the links provided

https://www.vagrantup.com/downloads.html
https://www.virtualbox.org/wiki/Downloads

Then execute the following in the terminal:

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki
    vagrant up

Check ```http://127.0.0.1:5000/``` to make sure it's running.

### Docker

Make sure you have docker installed. http://docs.docker.com/installation/
Here is an example run command, it will pull the image from docker hub initially.

    docker run --name realms-wiki -p 5000:5000 -d realms/realms-wiki
    
You can build your own image if you want.  Mine is based off https://github.com/phusion/baseimage-docker
The Dockerfile is located in [docker/Dockerfile](docker/Dockerfile)  realms/base just creates the deploy user.

## Config and Setup

You should be able to run the wiki without configuration with the default config values.
You may want to customize your app and the easiest way is the setup command.

    realms-wiki setup
    
This will ask you questions and create a realms-wiki.json file in where it can find it.
You can manually edit this file as well.
Any config value set in realms-wiki.json will override values set in ```realms/config/__init__.py```

### Nginx Setup

    sudo apt-get install -y nginx

Create a file called realms.conf in /etc/nginx/conf.d

    sudo nano /etc/nginx/conf.d/realms.conf

Put the following sample configuration in that file.

    server {
      listen 80;
      
      # Your domain here
      server_name wiki.example.org;
      
      # Settings to by-pass for static files 
      location ^~ /static/  {
        # Example:
        root /full/path/to/realms/static/;
      }
        
      location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
      
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
        
      }
    }


Test Nginx config
    
    sudo nginx -t

Reload Nginx

    sudo service nginx reload

### Mysql Setup
    
    sudo apt-get install -y mysql-server mysql-client libmysqlclient-dev
    realms-wiki pip install python-memcached
    
### MariaDB Setup
    
    sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
    realms-wiki pip install MySQL-Python

### Postgres

    sudo apt-get install -y libpq-dev postgresql postgresql-contrib postgresql-client
    realms-wiki pip install psycopg2

_Don't forget to create your database._

## Running

    realms-wiki start
    
### Upstart
    
Setup upstart with this command.

    sudo realms-wiki setup_upstart

This command requires root privs because it creates an upstart script.
Also note that ports below 1024 require user root.
After your config is in place use the following commands:

    sudo start realms-wiki
    sudo stop realms-wiki
    sudo restart realms-wiki
    

### Developement mode

This will start the server in the foreground with auto reloaded enabled

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

Access from your browser

http://localhost:5000

## Templating

Realms uses handlebars partials to create templates.
Each page that you create can be imported as a partial.

This page imports and uses a partial:

http://realms.io/_edit/hbs

This page contains the content of the partial:

http://realms.io/_edit/example-tmpl
    
I locked these pages to preserve them.  
You may copy and paste into a new page to test.


## Contributing

Issues and pull requests are welcome.

[Python style guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html)

## Author

Matthew Scragg <scragg@gmail.com>

[gollum]: https://github.com/gollum/gollum
[ghost]: https://github.com/tryghost/Ghost
[dillinger]: https://github.com/joemccann/dillinger/
