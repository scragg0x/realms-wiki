from flask_wtf import Form
from wtforms import StringField, PasswordField, validators


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])