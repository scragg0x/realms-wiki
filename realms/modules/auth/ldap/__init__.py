from __future__ import absolute_import

import ssl
import warnings
from os.path import exists

import ldap3.core.tls

from realms.modules.auth.models import Auth

Auth.register('ldap')


VALIDATE_MAP = {
    'NONE': ssl.CERT_NONE,
    'REQUIRED': ssl.CERT_REQUIRED,
    'OPTIONAL': ssl.CERT_OPTIONAL
}

VERSION_MAP = {
    'TLS': 'TLS',
    'SSLV23': 'SSLv23',
    'TLSV1': 'TLSv1',
    'TLSV1_1': 'TLSv1_1',
    'TLSV1_2': 'TLSv1_2'
}


def init(app):
    try:
        ldap_config = app.config['LDAP']
    except KeyError:
        raise RuntimeError("Provide a LDAP configuration to enable LDAP authentication")
    if not isinstance(ldap_config, dict):
        raise RuntimeError("LDAP configuration must be a dict of options")

    if 'URI' not in ldap_config:
        raise RuntimeError("LDAP is required, but the LDAP URI has not been defined")
    if 'BIND_DN' not in ldap_config and 'USER_SEARCH' not in ldap_config:
        raise RuntimeError("For LDAP authentication, you need to provide BIND_DN and/or USER_SEARCH option")

    ldap_config['URI'] = ldap_config['URI'].lower()

    if ldap_config.get('USER_SEARCH', {}).get('filter'):
        if not ldap_config['USER_SEARCH']['filter'].startswith('('):
            ldap_config['USER_SEARCH']['filter'] = "({})".format(ldap_config['USER_SEARCH']['filter'])

    # compatibility with flask-ldap-login
    if ldap_config.get('OPTIONS', {}).get('OPT_PROTOCOL_VERSION') and not ldap_config.get('LDAP_PROTO_VERSION'):
        ldap_config['LDAP_PROTO_VERSION'] = ldap_config['OPTIONS']['OPT_PROTOCOL_VERSION']

    # default ldap protocol version = 3
    try:
        ldap_config['LDAP_PROTO_VERSION'] = int(ldap_config.get('LDAP_PROTO_VERSION', 3))
    except ValueError:
        raise RuntimeError("LDAP_PROTO_VERSION must be a integer")

    # Python < 2.7.9 has problems with TLS
    if ldap_config['START_TLS'] or ldap_config['URI'].startswith('ldaps://'):
        if not ldap3.core.tls.use_ssl_context:
            warnings.warn("The Python version is old and it does not perform TLS correctly. You should upgrade.",
                          DeprecationWarning)
            if ldap_config.get('TLS_OPTIONS', {}).get('CLIENT_PRIVKEY_PASSWORD'):
                raise RuntimeError("The Python version is too old and does not support private keys with password")

    # check that TLS options, if provided, are really valid
    if ldap_config.get('TLS_OPTIONS', {}).get('VALIDATE'):
        try:
            ldap_config['TLS_OPTIONS']['VALIDATE'] = VALIDATE_MAP[ldap_config['TLS_OPTIONS']['VALIDATE'].upper()]
        except KeyError:
            raise RuntimeError("The 'VALIDATE' TLS option must be one of: {}".format(", ".join(VALIDATE_MAP.keys())))

    if ldap_config.get('TLS_OPTIONS', {}).get('VERSION'):
        try:
            ldap_config['TLS_OPTIONS']['VERSION'] = getattr(
                ssl,
                "PROTOCOL_{}".format(VERSION_MAP[ldap_config['TLS_OPTIONS']['VERSION'].upper()])
            )
        except KeyError:
            raise RuntimeError("The 'VERSION' TLS option must be one of: {}".format(", ".join(VERSION_MAP.keys())))
        except AttributeError:
            raise RuntimeError("The running Python does not support TLS protocol: {}".format(
                ldap_config['TLS_OPTIONS']['VERSION']
            ))

    if ldap_config.get('TLS_OPTIONS', {}).get('CA_CERTS_FILE'):
        if not exists(ldap_config['TLS_OPTIONS']['CA_CERTS_FILE']):
            raise RuntimeError("CA_CERTS_FILE '{}' does not exist".format(ldap_config['TLS_OPTIONS']['CA_CERTS_FILE']))

    if ldap_config.get('TLS_OPTIONS', {}).get('CLIENT_CERT_FILE'):
        if not exists(ldap_config['TLS_OPTIONS']['CLIENT_CERT_FILE']):
            raise RuntimeError(
                "CLIENT_CERT_FILE '{}' does not exist".format(ldap_config['TLS_OPTIONS']['CLIENT_CERT_FILE']))

    if ldap_config.get('TLS_OPTIONS', {}).get('CLIENT_PRIVKEY_FILE'):
        if not exists(ldap_config['TLS_OPTIONS']['CLIENT_PRIVKEY_FILE']):
            raise RuntimeError(
                "CLIENT_PRIVKEY_FILE '{}' does not exist".format(ldap_config['TLS_OPTIONS']['CLIENT_PRIVKEY_FILE']))

