from flask import render_template,g
from flask.ext.login import login_user,logout_user,current_user,login_required
from monitor import app,lm
from monitor import db
from monitor.auth.models import User
import os
from flask import send_from_directory




@app.before_request
def before_request():
    g.user = current_user
    # metadata = Base.metadata
    # session_factory = sessionmaker(bind=engine)
    # Session = scoped_session(session_factory)
    # # print Session
    # Session = localSession
    # g.Session = Session
    # print 'Session in before_request ,' ,g.Session

# @app.teardown_request
# def teardown_request(exception):
#     # print 'Session in after_request ,', g.Session
#     g.Session.remove()


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    # print 'Session in dashboard ,' ,g.Session
    return render_template('dashboard.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='img/favicon.icon')