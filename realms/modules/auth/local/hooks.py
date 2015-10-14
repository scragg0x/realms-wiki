from flask import current_app
from flask_wtf import RecaptchaField
from .forms import RegistrationForm


def before_first_request():
    if current_app.config['RECAPTCHA_ENABLE']:
        setattr(RegistrationForm, 'recaptcha', RecaptchaField("You Human?"))
