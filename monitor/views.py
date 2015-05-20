from flask import render_template,g,request
from flask.ext.login import login_user,logout_user,current_user,login_required
from monitor import app,lm
from monitor import db
from monitor.auth.models import User
import os,json
from flask import send_from_directory




@app.before_request
def before_request():
    g.user = current_user



@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    # print 'Session in dashboard ,' ,g.Session
    return render_template('chart/main.html')

# @app.route('/testlogin/',methods=['POST','GET'])
# def testlogin():
#     if request.method == 'POST':
#         # print dir(request)
#         print request.form.get('username')
#         print request.form.get('password')
#         # print request.form.get('username')
#         # print request.data.get('username')
#         # print request.data.get('password')
#         # print request.data
#     # print 'Session in dashboard ,' ,g.Session
#     return json.dumps(0)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html',referer=request.referrer),403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='img/favicon.icon')