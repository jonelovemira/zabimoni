# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask.ext.login import logout_user,login_user,login_required

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from monitor import db

# Import module forms
from monitor.auth.forms import LoginForm,AddUserForm

# Import module models (i.e. User)
from monitor.auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@mod_auth.route('/', methods=['GET', 'POST'])
@mod_auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash('Welcome %s' % user.username)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Wrong username or password', 'error-message')
    return render_template("auth/login.html")

@mod_auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('auth.login'))

@mod_auth.route('/config/')
@login_required
def config():
    users = User.query.all()
    return render_template('auth/config.html',users=users)

@mod_auth.route('/add/', methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        usertype = request.form.get('usertype')
        loginpermission = request.form.get('loginpermission')
        email = request.form.get('emailaddress')

        try:
            user = User(username,password,usertype,loginpermission,email)
            db.session.add(user)
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            flash(str(e),'error')
        else:
            flash('you add an user')
            return redirect(url_for('auth.config'))
        finally:
            db.session.remove()
        # print username,password,confirmpassword,usertype,loginpermission,email
    return render_template("auth/add.html")


@mod_auth.route('/user/delete/<userid>', methods=['GET'])
@login_required
def userdelete(userid):
    try:
        user = User.query.filter_by(userid=userid).first()
        db.session.delete(user)
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        flash(str(e),'error')
    else:
        flash('you delete an user')
    finally:
        db.session.remove()

    return redirect(url_for('auth.config'))
