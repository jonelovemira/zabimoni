#! flask/bin/python

# import os

# os.environ['DATABASE_URL'] = 'mysql://monitors:monitors@localhost/monitors'

from flup.server.fcgi import WSGIServer
from monitor import app

if __name__ == '__main__':
	WSGIServer(app).run() 