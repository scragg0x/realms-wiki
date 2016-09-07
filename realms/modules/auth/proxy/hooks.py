from __future__ import absolute_import

import logging

from flask import request, current_app
from flask_login import current_user, logout_user

from .models import User as ProxyUser


logger = logging.getLogger("realms.auth")


def before_request():
    header_name = current_app.config["AUTH_PROXY_HEADER_NAME"]
    remote_user = request.headers.get(header_name)
    if remote_user:
        if current_user.is_authenticated:
            if current_user.id == remote_user:
                return
            logger.info("login in realms and login by proxy are different: '{}'/'{}'".format(
                current_user.id, remote_user))
            logout_user()
        logger.info("User logged in by proxy as '{}'".format(remote_user))
        ProxyUser.do_login(remote_user)
