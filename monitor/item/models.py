from monitor import db
# from flask.ext.sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

class Itemtype(db.Model):
	itemtypeid = db.Column(db.Integer,primary_key=True)
	itemtypename = db.Column(db.String(80),unique=True)
	itemkey = db.Column(db.String(80),unique=True)
	itemunit = db.Column(db.String(80))
	zabbixvaluetype = db.Column(db.Integer)
	items = db.relationship('Item',backref='itemtype',lazy='dynamic')
	aws_id = db.Column(db.Integer,db.ForeignKey('aws.awsid'))
	series = db.relationship('Series',backref='itemtype',lazy='dynamic')
	Itemdatatype_id = db.Column(db.Integer,db.ForeignKey('itemdatatype.itemdatatypeid'))
	normalitemtype_id = db.Column(db.Integer,db.ForeignKey('normalitemtype.normalitemtypeid'))
	zbxitemtype_id = db.Column(db.Integer,db.ForeignKey('zbxitemtype.zbxitemtypeid'))
	time_frequency = db.Column(db.Integer)
	function_type = db.Column(db.Integer)
	# detailitemtypes = db.relationship('Detailitemtype',backref='itemtype',lazy='dynamic')

	def	__init__(self,itemtypename,itemkey,aws=None,itemdatatype=None,itemunit=None,zabbixvaluetype=None,time_frequency=60,function_type=0):
		self.itemtypename = itemtypename
		self.itemkey = itemkey
		self.aws = aws
		self.itemdatatype = itemdatatype
		self.itemunit = itemunit
		self.zabbixvaluetype = zabbixvaluetype
		if aws != None:
			self.time_frequency = 14400
		else:
			self.time_frequency = 60
		self.function_type = function_type

	def __repr__(self):
		return '<Itemtype %r>' % self.itemtypename

class Zbxitemtype(db.Model):
	zbxitemtypeid = db.Column(db.Integer,primary_key=True)
	itemtypes = db.relationship('Itemtype',backref='zit',lazy='dynamic')

class Normalitemtype(db.Model):
	normalitemtypeid = db.Column(db.Integer,primary_key=True)
	itemtypes = db.relationship('Itemtype',backref='nit',lazy='dynamic')

	def add_itemtype(self,itemtype):
		if not self.has_itemtype(itemtype):
			self.itemtypes.append(itemtype)
			return self

	def rm_itemtype(self,itemtype):
		if self.has_itemtype(itemtype):
			self.itemtypes.remove(itemtype)
			return self

	def has_itemtype(self,itemtype):
		return self.itemtypes.filter_by(itemtypeid = itemtype.itemtypeid).count() > 0

class Itemdatatype(db.Model):
	itemdatatypeid = db.Column(db.Integer,primary_key=True)
	itemdatatypename = db.Column(db.String(80),unique=True)
	itemtypes = db.relationship('Itemtype',backref='itemdatatype',lazy='dynamic')
	

	def __init__(self,itemdatatypename):
	 	self.itemdatatypename = itemdatatypename

	def __repr__(self):
		return "<Itemdatatype %r>" % self.itemdatatypename


# class Detailitemtype(db.Model):
# 	detailitemtypeid = db.Column(db.Integer,primary_key=True)
# 	detailitemtypename = db.Column(db.String(80),unique=True)
# 	items = db.relationship('Item',backref='Detailitemtype',lazy='dynamic')
# 	itemtype_id = db.Column(db.Integer,db.ForeignKey('itemtype.itemtypeid'))
# 	aws_id = db.Column(db.Integer,db.ForeignKey('aws.awsid'))

# 	def __repr__(self):
# 		return '<Detailitemtype %r>' % self.detailitemtypename

service_itemtype = db.Table('service_itemtype',
				db.Column('service_id',db.Integer,db.ForeignKey('service.serviceid')),
				db.Column('itemtype_id',db.Integer,db.ForeignKey('itemtype.itemtypeid')))

class Service(db.Model):
	serviceid = db.Column(db.Integer,primary_key=True,autoincrement=True)
	servicename = db.Column(db.String(80),unique=True)
	hosts = db.relationship('Host',backref='service',lazy='dynamic')
	items = db.relationship('Item',backref='service',lazy='dynamic')
	itemtypes = db.relationship('Itemtype',
				secondary=service_itemtype,
				primaryjoin=(service_itemtype.c.service_id == serviceid),
				secondaryjoin=(service_itemtype.c.itemtype_id == Itemtype.itemtypeid),
				backref=db.backref('service',lazy='dynamic'),
				lazy = 'dynamic'
	)
	
	# def __init__(self,servicename):
	# 	self.servicename = servicename
	
	def __repr__(self):
		return '<Service %r>' % self.servicename

	def add_itemtype(self,itemtype):
		if not self.has_itemtype(itemtype):
			self.itemtypes.append(itemtype)
			return self

	def rm_itemtype(self,itemtype):
		if self.has_itemtype(itemtype):
			self.itemtypes.remove(itemtype)
			return self

	def has_itemtype(self,itemtype):
		return self.itemtypes.filter_by(itemtypeid = itemtype.itemtypeid).count() > 0




area_service = db.Table('area_service',
				db.Column('area_id',db.Integer,db.ForeignKey('area.areaid')),
				db.Column('service_id',db.Integer,db.ForeignKey('service.serviceid')))

area_itemtype = db.Table('area_itemtype',
				db.Column('area_id',db.Integer,db.ForeignKey('area.areaid')),
				db.Column('itemtype_id',db.Integer,db.ForeignKey('itemtype.itemtypeid')))

class Area(db.Model):
	areaid = db.Column(db.Integer,primary_key=True,autoincrement=True)
	areaname = db.Column(db.String(80),unique=True)
	hosts = db.relationship('Host',backref='area',lazy='dynamic')
	items = db.relationship('Item',backref='area',lazy='dynamic')
	awses = db.relationship('Aws',backref='area',lazy='dynamic')

	services = db.relationship('Service',
				secondary=area_service,
				primaryjoin=(area_service.c.area_id == areaid),
				secondaryjoin=(area_service.c.service_id == Service.serviceid),
				backref=db.backref('area',lazy='dynamic'),
				lazy = 'dynamic'
	)

	itemtypes = db.relationship('Itemtype',
				secondary=area_itemtype,
				primaryjoin=(area_itemtype.c.area_id == areaid),
				secondaryjoin=(area_itemtype.c.itemtype_id == Itemtype.itemtypeid),
				backref=db.backref('area',lazy='dynamic'),
				lazy = 'dynamic'
	)

	# def __init__(self,areaname):
	# 	self.areaname = areaname

	def __repr__(self):
		return '<Area %r>' % self.areaname

	def add_service(self,service):
		if not self.has_service(service):
			self.services.append(service)
			return self

	def rm_service(self,service):
		if self.has_service(service):
			self.services.remove(service)
			return self

	def has_service(self,service):
		return self.services.filter_by(serviceid = service.serviceid).count() > 0


	def add_itemtype(self,itemtype):
		if not self.has_itemtype(itemtype):
			self.itemtypes.append(itemtype)
			return self

	def rm_itemtype(self,itemtype):
		if self.has_itemtype(itemtype):
			self.itemtypes.remove(itemtype)
			return self

	def has_itemtype(self,itemtype):
		return self.itemtypes.filter_by(itemtypeid = itemtype.itemtypeid).count() > 0

class Aws(db.Model):
	awsid = db.Column(db.Integer,primary_key=True)
	awsname = db.Column(db.String(80))
	items = db.relationship('Item',backref='aws',lazy='dynamic')
	itemtypes = db.relationship('Itemtype',backref='aws',lazy='dynamic')
	area_id = db.Column(db.Integer,db.ForeignKey('area.areaid'))

	def __init__(self,awsname,area):
		self.awsname = awsname
		self.area = area

	def __repr__(self):
		return '<AWS %r>' % self.awsname

###################################################
###    ATTENTION!!!                             ###
###    You should  maintain the area_service 	###
###    table when create a new host             ###
###################################################

host_itemtype = db.Table('host_itemtype',
				db.Column('host_id',db.Integer,db.ForeignKey('host.hostid')),
				db.Column('itemtype_id',db.Integer,db.ForeignKey('itemtype.itemtypeid')))

class Host(db.Model):
	hostid = db.Column(db.Integer,primary_key=True,autoincrement=False,unique=True)
	hostname = db.Column(db.String(80))
	items = db.relationship('Item',backref='host',lazy='dynamic')
	area_id = db.Column(db.Integer,db.ForeignKey('area.areaid'))
	service_id = db.Column(db.Integer,db.ForeignKey('service.serviceid'))

	itemtypes = db.relationship('Itemtype',
				secondary=host_itemtype,
				primaryjoin=(host_itemtype.c.host_id == hostid),
				secondaryjoin=(host_itemtype.c.itemtype_id == Itemtype.itemtypeid),
				backref=db.backref('host',lazy='dynamic'),
				lazy = 'dynamic'
	)
	
	# def __init__(self,servicename):
	# 	self.servicename = servicename
	
	def __repr__(self):
		return '<Service %r>' % self.servicename

	def add_itemtype(self,itemtype):
		if not self.has_itemtype(itemtype):
			self.itemtypes.append(itemtype)
			return self

	def rm_itemtype(self,itemtype):
		if self.has_itemtype(itemtype):
			self.itemtypes.remove(itemtype)
			return self

	def has_itemtype(self,itemtype):
		return self.itemtypes.filter_by(itemtypeid = itemtype.itemtypeid).count() > 0


	def __init__(self,hostid,hostname,area,service):
		self.hostid = hostid
		self.hostname = hostname
		self.area = area
		self.service = service


	def __repr__(self):
		return '<Host %r>' % self.hostname

class Item(db.Model):
	itemid = db.Column(db.Integer,primary_key=True,autoincrement=False,unique=True)
	itemname = db.Column(db.String(80))
	host_id = db.Column(db.Integer,db.ForeignKey('host.hostid'))
	itemtype_id = db.Column(db.Integer,db.ForeignKey('itemtype.itemtypeid'),nullable=False)
	# detailitemtype_id = db.Column(db.Integer,db.ForeignKey('detailitemtype.detailitemtypeid'))
	area_id = db.Column(db.Integer,db.ForeignKey('area.areaid'))
	service_id = db.Column(db.Integer,db.ForeignKey('service.serviceid'))
	aws_id = db.Column(db.Integer,db.ForeignKey('aws.awsid'))

	def __init__(self,itemid,itemname,host=None,itemtype=None):


		self.itemid = itemid
		self.itemname = itemname
		self.host = host
		self.itemtype = itemtype
		area = None
		service = None
		aws = None
		if host != None:
			area = host.area
			service = host.service

		if itemtype != None:
			aws = itemtype.aws

		self.area = area
		self.service = service
		self.aws = aws

	def set_belong_to_area(self,area):
		if self.area == area:
			return None
		self.area = area
		return self



	def __repr__(self):
		return '<Item %r>' % self.itemname

class Calculateditem(db.Model):
	calculateditemid = db.Column(db.Integer,primary_key=True,autoincrement=False)
	formula = db.Column(db.String(512))
	triggers = db.relationship('Trigger',backref='calcitem',lazy='dynamic')


	def __init__(self,calculateditemid,formula):
		self.calculateditemid = calculateditemid
		self.formula = formula

	def __repr__(self):
		return '<Calculateditem %r>' % (self.formula)

class Action(db.Model):
	actionid = db.Column(db.Integer,primary_key=True,autoincrement=False)
	autoscalegroupname = db.Column(db.String(100))
	autoscaletype = db.Column(db.Integer)
	areaid = db.Column(db.Integer)
	command = db.Column(db.String(512))
	actionname = db.Column(db.String(80))

	def __init__(self,actionid,autoscalegroupname,autoscaletype,areaid,command,actionname):
		self.actionid = actionid
		self.autoscalegroupname = autoscalegroupname
		self.autoscaletype = autoscaletype
		self.areaid = areaid
		self.command = command
		self.actionname = actionname

	def __repr__(self):
		return '<Action %s>' % (self.actionid)

action_trigger = db.Table('action_trigger',
				db.Column('action_id',db.Integer,db.ForeignKey('action.actionid')),
				db.Column('trigger_id',db.Integer,db.ForeignKey('trigger.triggerid')))

	

class Trigger(db.Model):
	triggerid = db.Column(db.Integer,primary_key=True,autoincrement=False)
	triggername = db.Column(db.String(100))
	triggervalue = db.Column(db.Float)
	timeshift = db.Column(db.Integer)
	triggerfunction = db.Column(db.String(64))

	calculateditem_id = db.Column(db.Integer,db.ForeignKey('calculateditem.calculateditemid'))

	actions = db.relationship('Action',
				secondary=action_trigger,
				primaryjoin=(action_trigger.c.trigger_id == triggerid),
				secondaryjoin=(action_trigger.c.action_id == Action.actionid),
				backref=db.backref('triggers',lazy='dynamic'),
				lazy = 'dynamic'
	)

	
	# serviceid = db.Column(db.In)

	def __init__(self,triggerid,triggername,triggervalue,timeshift,calcitem,triggerfunction):
		self.triggerid = triggerid
		self.triggername = triggername
		self.triggervalue = triggervalue
		self.timeshift = timeshift
		self.calcitem = calcitem
		self.triggerfunction = triggerfunction

	def __repr__(self):
		return '<Trigger %r>' % ( self.triggername )

	def add_action(self,action):
		if not self.has_action(action):
			self.actions.append(action)
			return self

	def rm_action(self,action):
		if self.has_action(action):
			self.actions.remove(action)
			return self

	def has_action(self,action):
		return self.actions.filter_by(actionid = action.actionid).count() > 0