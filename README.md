# Realms Wiki Beta

Git based wiki written in Python
Inspired by Gollum, Ghost, and Dillinger.
Basic authentication and registration included.

## Features

- Built with Bootstrap 3
- Currently Markdown (w/ HTML) only
- Syntax highlighting (Ace Editor)
- Live preview
- Collaboration (TogetherJS)
- Drafts saved to localstorage

## Screenshots

TODO thumbnails here

## Requirements
- Python 2.7
- Git
- NodeJS (needed for bower/cleancss, distro packages shouldn't need this in future)

** Optional **
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

TODO nginx config here

## Running

Current there are different ways.

- Daemon mode using upstart

```sudo start realms-wiki```

- Foreground mode

```realms-wiki run```

- Debug mode

```realms-wiki runserver```

Access from your browser

```http://localhost:5000```

## Vagrant

```
git clone https://github.com/scragg0x/realms-wiki
cd realms-wiki
vagrant up
vagrant ssh
realms-wiki runserver
```
