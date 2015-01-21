# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for,current_app
from flask.ext.login import logout_user,login_user,login_required,current_user

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from monitor import db,app

# Import module models (i.e. User)
from monitor.auth.models import User

import urllib2,urllib, json
from config import AUTHORIZATION_SERVER,AUTHORIZATION_VIEW,AUTHORIZATION_PROTOCAL,IN_LOCAL

#register principle
from flask.ext.principal import Identity, AnonymousIdentity,identity_changed,identity_loaded, RoleNeed,UserNeed,Permission

admin_permission = Permission(RoleNeed('1')).union(Permission(RoleNeed('0')))

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@mod_auth.route('/', methods=['GET', 'POST'])
@mod_auth.route('/login/', methods=['GET', 'POST'])
def login():

    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not IN_LOCAL:
            login_result = try_login(username,password)

            if login_result['success'] == True:
                return after_login(    login_result['result']['userid'],\
                    login_result['result']['username'],\
                    login_result['result']['usertype'],
                    login_result['result']['email'])
            else:
                error = login_result['info']
                flash(error,'danger')

            return render_template("auth/login.html")

        else:
            user = User.query.filter_by(username=username).first()
            if user == None:
                flash('user do not exists','danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            identity_changed.send(current_app._get_current_object(),identity=Identity(user.userid))
            flash('Welcome %s' % user.username,'info')
            return redirect(request.args.get('next') or url_for('index'))

    return render_template("auth/login.html")

        

        

def try_login(username,password):
    url = AUTHORIZATION_PROTOCAL + AUTHORIZATION_SERVER + AUTHORIZATION_VIEW
    data = urllib.urlencode({'username':username,'password':password})
    result = urllib2.urlopen(url=url, data=data).read()
    return json.loads(result)

def after_login(userid,username,usertype,emailaddress):
    try:
        user = User.query.get(userid)
        if user == None:
            user = User(userid,username,usertype,emailaddress)
        else:
            user.username = username
            user.role = usertype
            user.email = emailaddress
        db.session.add(user)
        db.session.commit()
        login_user(user)
        identity_changed.send(current_app._get_current_object(),identity=Identity(user.userid))
    except Exception, e:
        db.session.rollback()
        flash(str(e),'danger')
        return render_template("auth/login.html")
    else:
        flash('Welcome,' + username,'info')
        return redirect(request.args.get('next') or url_for('index'))
    finally:
        db.session.remove()

@mod_auth.route('/logout/')
@login_required
def logout():
    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),identity=AnonymousIdentity())
    flash('You were logged out.','info')
    return redirect(url_for('auth.login'))

@mod_auth.route('/config/')
@login_required
@admin_permission.require(http_exception=403)
def config():
    users = User.query.all()
    return render_template('auth/config.html',users=users)

# @mod_auth.route('/add/', methods=['GET', 'POST'])
# @admin_permission.require(http_exception=403)
# @login_required
# def add():

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         confirmpassword = request.form.get('confirmpassword')
#         usertype = request.form.get('usertype')
#         loginpermission = request.form.get('loginpermission')
#         email = request.form.get('emailaddress')

#         try:
#             user = User(username,password,usertype,loginpermission,email)
#             db.session.add(user)
#             db.session.commit()
#         except Exception, e:
#             db.session.rollback()
#             flash(str(e),'danger')
#         else:
#             flash('you add an user','success')
#             return redirect(url_for('auth.config'))
#         finally:
#             db.session.remove()
#         # print username,password,confirmpassword,usertype,loginpermission,email
#     return render_template("auth/add.html")


@mod_auth.route('/user/delete/<userid>', methods=['GET'])
@login_required
def userdelete(userid):
    try:
        user = User.query.filter_by(userid=userid).first()
        db.session.delete(user)
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        flash(str(e),'danger')
    else:
        flash('you delete an user','success')
    finally:
        db.session.remove()

    return redirect(url_for('auth.config'))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'userid'):
        identity.provides.add(UserNeed(current_user.userid))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'role'):
        identity.provides.add(RoleNeed(unicode(current_user.role)))