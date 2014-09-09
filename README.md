# Realms Wiki Beta

Git based wiki written in Python
Inspired by Gollum, Ghost, and Dillinger.
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

TODO thumbnails here

## Requirements
- Python 2.7
- Git
- NodeJS (needed for bower/cleancss, distro packages shouldn't need this in future)

**Optional**
- Nginx (if you want proxy requests, this is recommended)
- Memcached or Redis, default is memonization
- MariaDB, MySQL, Postgresql, or another database supported by SQLAlchemy, default is sqlite.  
Anon or single user does not require a database.

## Installation
Install script only tested with Ubuntu 14.04.
Please refer to the script for package requisites if needed

```
git clone https://github.com/scragg0x/realms-wiki
cd realms-wiki
sudo bash install.sh
```

**Nginx**

```sudo apt-get install -y nginx```

Create a file called realms.conf in /etc/nginx/conf.d

```
/etc/nginx/conf.d/realms.conf
```

Put the following sample configuration in that file.

    server {
      listen 80;
      
      # Your domain here
      server_name wiki.example.org;
      
      location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
      
        proxy_pass http://127.0.0.1:5000/;
        proxy_redirect off;
        
      }
    }


Test Nginx config
```sudo nginx -t```

Reload Nginx
```sudo service nginx reload```

## Running

Current there are different ways.

- Daemon mode using upstart

```sudo start realms-wiki```

- Foreground mode

```realms-wiki run```

- Debug mode

```realms-wiki runserver```

Access from your browser

http://localhost:5000

## Vagrant

Vagrantfile is included for development.

```
git clone https://github.com/scragg0x/realms-wiki
cd realms-wiki
vagrant up
vagrant ssh
realms-wiki runserver
```

## Author

Matthew Scragg <scragg@gmail.com>
