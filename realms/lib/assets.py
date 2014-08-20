from flask.ext.assets import Bundle, Environment

# This can be done better, make it better

assets = Environment()
filters = 'uglifyjs'
output = 'assets/%(version)s.js'


def register(name, *files):
    assets.register(name, Bundle(*files, filters=filters, output=output))
