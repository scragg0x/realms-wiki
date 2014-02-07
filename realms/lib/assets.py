from flask.ext.assets import Bundle, Environment

assets = Environment()


def register(*files):
    assets.debug = True
    filters = 'uglifyjs'
    output = 'assets/%(version)s.js'
    assets.add(Bundle(*files, filters=filters, output=output))
