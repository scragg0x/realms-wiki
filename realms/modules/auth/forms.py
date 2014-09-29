from flask_wtf import Form, RecaptchaField
from wtforms import StringField, PasswordField, validators
from realms import app


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

if app.config['RECAPTCHA_ENABLE']:
    setattr(RegistrationForm, 'recaptcha', RecaptchaField("You Human?"))


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


