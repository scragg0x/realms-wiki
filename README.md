# Realms Wiki Beta

Git based wiki written in Python
Inspired by [Gollum][gollum], [Ghost][ghost], and [Dillinger][dillinger].
Basic authentication and registration included.

Demo: http://realms.io
This domain is being used temporarily as a demo so expect it to change.

## Features

- Built with Bootstrap 3
- Currently Markdown (w/ HTML) only
- Syntax highlighting (Ace Editor)
- Live preview
- Collaboration (TogetherJS)
- Drafts saved to localstorage
- Handlebars

## Screenshots

[<img src="https://db.tt/Q2XHGRnT" width=340 />](https://db.tt/Q2XHGRnT)&nbsp;[<img  width=340 src="https://db.tt/pIZ4w2oN" />](https://db.tt/pIZ4w2oN)&nbsp;[<img  width=340 src="https://db.tt/ERLmDHrk" />](https://db.tt/ERLmDHrk)&nbsp;[<img width=340 src="https://db.tt/Ls08ocLh" />](https://db.tt/Ls08ocLh)&nbsp;[<img width=340 src="https://db.tt/7QVfXFQ4" />](https://db.tt/7QVfXFQ4)&nbsp;[<img width=340 src="https://db.tt/Lna3BOm1" />](https://db.tt/Lna3BOm1)


## Requirements
- Python 2.7
- Git
- NodeJS (needed for bower, distro packages shouldn't need this in future)

**Optional**
- Nginx (if you want proxy requests, this is recommended)
- Memcached or Redis, default is memonization
- MariaDB, MySQL, Postgresql, or another database supported by SQLAlchemy, default is sqlite.  
Anon or single user does not require a database.

## Installation

### Ubuntu

If you are using Ubuntu 14.04, you can use install.sh.
    
```
git clone https://github.com/scragg0x/realms-wiki
cd realms-wiki
sudo bash install.sh
```

### OSX / Windows

This app is designed to run in Linux and I recommend using Vagrant to install on OSX or Windows.

### Vagrant

Vagrantfile is included for development or running locally.
To get started with Vagrant, download and install Vagrant and Virtualbox for your platform with the links provided

https://www.vagrantup.com/downloads.html
https://www.virtualbox.org/wiki/Downloads

Then execute the following in the terminal:

    git clone https://github.com/scragg0x/realms-wiki
    cd realms-wiki
    vagrant up
    vagrant ssh
    realms-wiki dev

Check ```http://127.0.0.1:5000/``` to make sure it's running.

### Docker

Make sure you have docker installed. http://docs.docker.com/installation/
Here is an example run command, it will pull the image from docker hub initially.

    docker run --name realms-wiki -p 5000:5000 -d realms/realms-wiki
    
You can build your own image if you want.  Mine is based off https://github.com/phusion/baseimage-docker
The Dockerfile is located in [docker/Dockerfile](docker/Dockerfile)  realms/base just creates the deploy user.

## Config and Setup

You should be able to run this right out of the box with the default config values.
You may want to customize your app and the easiest way is the setup command.

    realms-wiki setup
    
This will ask you questions and create a config.json file in the app root directory.
Of course you can manually edit this file as well.
Any config value set in config.json will override values set in ```realms/config/__init__.py```

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

Current there are different ways.

- Daemon mode using upstart

```sudo start realms-wiki```

- Foreground mode

```realms-wiki run```

- Debug mode

```realms-wiki dev```

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

## Author

Matthew Scragg <scragg@gmail.com>


[gollum]: https://github.com/gollum/gollum
[ghost]: https://github.com/tryghost/Ghost
[dillinger]: https://github.com/joemccann/dillinger/

