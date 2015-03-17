from monitor import db
from monitor.models import Attr
# from monitor.auth.models import User
# from monitor.models import series_item




class Window(db.Model):
	windowid = db.Column(db.Integer,primary_key=True)
	windowname = db.Column(db.String(80))
	type = db.Column(db.Integer)
	index = db.Column(db.Integer)
	user_id = db.Column(db.Integer,db.ForeignKey('user.userid'))
	page_id = db.Column(db.Integer,db.ForeignKey('page.pageid'))


	selectedmetrics = db.relationship('Selectedmetrics',backref='window',lazy='dynamic')
	chartconfig = db.relationship('Chartconfig',backref='window',lazy='dynamic')

	def __init__(self,windowname,type,index,user,page):
		self.windowname = windowname
		self.type = type
		self.index = index
		self.owner = user
		self.page = page
	
	def __repr__(self):
		return '<Window %r>' % self.windowname

class Selectedmetrics(db.Model):
	selectedmetricsid = db.Column(db.Integer,primary_key=True)
	window_id = db.Column(db.Integer,db.ForeignKey('window.windowid'))
	report_id = db.Column(db.Integer,db.ForeignKey('report.reportid'))

	options = db.relationship('Option',backref='selectedmetrics',lazy='dynamic')

	def __init__(self,window,report=None):
		self.window = window
		self.report = report

	def __repr__(self):
		return '<Selectedmetrics %r>' % self.selectedmetricsid

class Option(db.Model):
	optionid = db.Column(db.Integer,primary_key=True)
	optionname = db.Column(db.String(80))
	selectedmetrics_id = db.Column(db.Integer,db.ForeignKey('selectedmetrics.selectedmetricsid'))

	displaytables = db.relationship('Displaytable',backref='option',lazy='dynamic')

	def __init__(self,optionname,selectedmetrics):
		self.optionname = optionname
		self.selectedmetrics = selectedmetrics

	def __repr__(self):
		return '<Option %r>' % self.optionname

class Displaytable(db.Model):
	displaytableid = db.Column(db.Integer,primary_key=True)
	displaytablename = db.Column(db.String(80))

	option_id = db.Column(db.Integer,db.ForeignKey('option.optionid'))

	rows = db.relationship('Displaytablerow',backref='displaytable',lazy='dynamic')

	def __init__(self,displaytablename,option):
		self.displaytablename = displaytablename
		self.option = option

	def __repr__(self):
		return '<Displaytable %r>' % self.displaytablename

class Displaytablerow(db.Model):
	displaytablerowid = db.Column(db.Integer,primary_key=True)

	displaytable_id = db.Column(db.Integer,db.ForeignKey('displaytable.displaytableid'))

	attrs = db.relationship('Attr',backref = 'displaytablerow',lazy='dynamic')

	def __init__(self,displaytable):
		self.displaytable = displaytable

	def __repr__(self):
		return '<Displaytablerow %r>' % self.displaytablerowid



class Chartconfig(db.Model):
	chartconfigid = db.Column(db.Integer,primary_key=True)
	attrs = db.relationship('Attr',backref = 'chartconfig',lazy='dynamic')

	window_id = db.Column(db.Integer,db.ForeignKey('window.windowid'))

	def __init__(self,window):
		self.window = window

	def __repr__(self):
		return '<Chartconfig %r>' % self.chartconfigid


class Report(db.Model):
	reportid = db.Column(db.Integer,primary_key=True)
	scaletype = db.Column(db.Integer)
	functiontype = db.Column(db.Integer)
	reportname = db.Column(db.String(80))
	user_id = db.Column(db.Integer,db.ForeignKey('user.userid'))
	title = db.Column(db.String(80))
	discription = db.Column(db.String(200))
	imgs = db.relationship('Reportimg',backref='report',lazy = 'dynamic')

	selectedmetrics = db.relationship('Selectedmetrics',backref='report',lazy='dynamic')
	
	def __init__(self,scaletype,functiontype,reportname,owner,title=None,discription=None):
		self.scaletype = scaletype
		self.functiontype = functiontype
		self.reportname = reportname
		self.owner = owner
		self.title = title
		self.discription = discription

	def __repr__(self):
		return '<Report %r>' % self.reportname

class Page(db.Model):
	pageid = db.Column(db.Integer,primary_key=True)
	pagename = db.Column(db.String(80))
	windows = db.relationship('Window',backref='page',lazy='dynamic')
	user_id = db.Column(db.Integer,db.ForeignKey('user.userid'))

	def __init__(self,pagename,owner):
		self.pagename = pagename
		self.owner = owner

	def __repr__(self):
		return '<Page %r>' % self.pagename

email_report = db.Table('email_report',
				db.Column('email_id',db.Integer,db.ForeignKey('emailschedule.emailscheduleid')),
				db.Column('report_id',db.Integer,db.ForeignKey('report.reportid')))

class Receiver(db.Model):
	receiverid = db.Column(db.Integer,primary_key=True)
	mailaddress = db.Column(db.String(80))

	def __init__(self,mailaddress):
		self.mailaddress = mailaddress

	def __repr__(self):
		return '<Receiver %r>' % self.mailaddress

email_receiver = db.Table('email_receiver',
				db.Column('email_id',db.Integer,db.ForeignKey('emailschedule.emailscheduleid')),
				db.Column('receiver_id',db.Integer,db.ForeignKey('receiver.receiverid')))


class Emailschedule(db.Model):
	emailscheduleid = db.Column(db.Integer,primary_key=True)
	frequency = db.Column(db.Integer)
	starttime = db.Column(db.String(80))
	subject = db.Column(db.String(80))
	timezone = db.Column(db.Integer)
	user_id = db.Column(db.Integer,db.ForeignKey('user.userid'))
	imgs = db.relationship('Reportimg',backref='es',lazy = 'dynamic')
	reports = db.relationship('Report',
				secondary=email_report,
				primaryjoin=(email_report.c.email_id == emailscheduleid),
				secondaryjoin=(email_report.c.report_id == Report.reportid),
				lazy = 'dynamic'
	)

	receivers = db.relationship('Receiver',
				secondary=email_receiver,
				primaryjoin=(email_receiver.c.email_id == emailscheduleid),
				secondaryjoin=(email_receiver.c.receiver_id == Receiver.receiverid),
				lazy = 'dynamic'
	)

	def __init__(self,subject,frequency,starttime,owner,timezone=0):
		self.subject = subject
		self.frequency = frequency
		self.starttime = starttime
		self.owner = owner
		self.timezone = timezone

	def add_report(self,report):
		if not self.has_report(report):
			self.reports.append(report)
			return self

	def rm_report(self,report):
		if self.has_report(report):
			self.reports.remove(report)
			return self

	def has_report(self,report):
		return self.reports.filter_by(reportid = report.reportid).count() > 0


	def add_receiver(self,receiver):
		if not self.has_receiver(receiver):
			self.receivers.append(receiver)
			return self

	def rm_receiver(self,receiver):
		if self.has_receiver(receiver):
			self.receivers.remove(receiver)
			return self

	def has_receiver(self,receiver):
		return self.receivers.filter_by(receiverid = receiver.receiverid).count() > 0

	def __repr__(self):
		return '<Emailschedule %r>' % self.subject


class Reportimg(db.Model):
	reportimgid = db.Column(db.Integer,primary_key=True)
	reportimgname = db.Column(db.String(80))
	report_id = db.Column(db.Integer,db.ForeignKey('report.reportid'))
	daytime = db.Column(db.String(80))
	emailschedule_id = db.Column(db.Integer,db.ForeignKey('emailschedule.emailscheduleid'))

	def __init__(self,reportimgname,daytime,report,es):
		self.reportimgname = reportimgname
		self.daytime = daytime
		self.report = report
		self.es = es

	def __repr__(self):
		return '<Reportimg %r>' % self.reportimgname
