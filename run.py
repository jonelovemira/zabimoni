#!flask/bin/python

#from werkzeug.contrib.profiler import ProfilerMiddleware
#from monitor import app

#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
#app.run(host='0.0.0.0',port=5001,debug = True)

from monitor import app

app.run(host='0.0.0.0',port=5001,debug=True)
