from flask import Flask
from configloader import ConfigLoader

# If you get an error on the next line on Python 3.4.0, change to: Flask('app')
# where app matches the name of this file without the .py extension.
app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

ConfigLoader(app)

app.secret_key = app.config['secret_key']

from routes import *

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app
if __name__ == '__main__':
    import os
    host = os.environ.get('SERVER_HOST', app.config['host'])
    try:
        port = int(app.config['port'])
    except ValueError:
        port = 5555
    app.run(host, port)
