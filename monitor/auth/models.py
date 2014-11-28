from monitor import db
from werkzeug.security import generate_password_hash, \
     check_password_hash

# from monitor.chart.models import Window,Page,Report

class User(db.Model):

	userid = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	pw_hash = db.Column(db.String(200))
	role = db.Column(db.Integer)
	loginpermission = db.Column(db.Integer)
	email = db.Column(db.String(120), unique=True)
	windows = db.relationship('Window',backref='owner',lazy = 'dynamic')
	pages = db.relationship('Page',backref='owner', lazy='dynamic')
	reports = db.relationship('Report',backref='owner',lazy='dynamic')
	schedules = db.relationship('Emailschedule',backref='owner',lazy='dynamic')

	def __init__(self, username, password,role,loginpermission,email):
		self.username = username
		self.set_password(password)
		self.role = role
		self.loginpermission = loginpermission
		self.email = email

	def is_authenticated(self):
		return True

	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.userid)  # python 2
		except NameError:
			return str(self.userid)  # python 3


	def set_password(self, password):
		self.pw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pw_hash, password)


	def __repr__(self):
		return '<User %r>' % self.username