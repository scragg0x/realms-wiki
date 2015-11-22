from flask_wtf import Form
from wtforms import StringField, PasswordField, validators


class LoginForm(Form):
    login = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])