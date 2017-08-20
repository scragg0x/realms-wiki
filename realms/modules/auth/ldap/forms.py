from __future__ import absolute_import

from flask_wtf import Form
from wtforms import StringField, PasswordField, validators


class LoginForm(Form):
    username = StringField('User ID', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
