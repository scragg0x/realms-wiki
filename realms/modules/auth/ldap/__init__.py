from __future__ import absolute_import

from realms.modules.auth.models import Auth

Auth.register('ldap')


def init(app):
    ldap_config = app.config['LDAP']
    print(ldap_config)
    if 'URI' not in ldap_config:
        raise RuntimeError("LDAP is required, but the LDAP URI has not been defined")
    if 'BIND_DN' not in ldap_config and 'USER_SEARCH' not in ldap_config:
        raise RuntimeError("For LDAP authentication, you need to provide BIND_DN and/or USER_SEARCH option")
