#!/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/python

from flup.server.fcgi import WSGIServer
from hisep_app import app as application

# application.debug = True
WSGIServer(application).run()
