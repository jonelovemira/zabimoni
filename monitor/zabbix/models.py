# from monitor import db,app
from monitor import app,db
from monitor.item.models import Item

engine = db.get_engine(app,bind='zabbix')


def query_data_2_arr(s):
	result = [[int(x[0]),float(x[1]),float(x[2]),float(x[3]),long(x[4]),float(x[5])] for x in s]
	if len(result) > 0:
		return result
	return None

def query_data_no_ground_2_arr(s):
	if s[0][0] == 0:
		return None
	result = [[int(x[0]),float(x[1]),float(x[2]),float(x[3]),float(x[4])] for x in s]
	if len(result) > 0:
		return result
	return None

def last_record_2_arr(s):
	result = [[int(x[0]),int(x[1]),float(x[2])] for x in s]

	if len(result) > 0:
		return result

	return None

class Zabbixhistory(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'history'
	itemid = db.Column('itemid',db.Integer,primary_key=True)
	clock = db.Column('clock',db.BigInteger,primary_key=True)
	value = db.Column('value',db.Float)
	ns = db.Column('ns',db.Integer)

	def __repr__(self):
		return "<zabbix history itemid - %s value - %s at %s>" % (self.itemid,self.value,self.clock)


	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):

		if len(query_itemids) <= 0 :
			return query_data_2_arr([])

		offset = ground // 10

		s = db.session.query(\
			db.func.count(cls.itemid).label('count'),\
			db.func.avg(cls.value).label('avg'),\
			db.func.max(cls.value).label('max'),\
			db.func.min(cls.value).label('min'),\
			db.func.floor((cls.clock + offset)/ground).label('minute'),\
			db.func.sum(cls.value)).filter(cls.itemid.in_(query_itemids)).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
			group_by('minute').all()


		return query_data_2_arr(s)


	@classmethod
	def get_interval_last_few_records(cls,query_itemids,time_since,time_till):

		if len(query_itemids) <= 0:
			return last_record_2_arr([])

		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			order_by(cls.clock.desc()).\
			limit(2*len(query_itemids)).all()

		return last_record_2_arr(s)

	@classmethod
	def get_interval_condition_record(cls,query_itemids,time_since,time_till,condition):

		if len(query_itemids) <= 0:
			return None

		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			filter('value ' + condition).all()

		return s if len(s) > 0 else None

	@classmethod
	def get_interval_history_no_ground(cls,query_itemids,time_since,time_till):

		if len(query_itemids) <= 0:
			return query_data_no_ground_2_arr([])

		s = db.session.query(\
			db.func.count(cls.itemid).label('count'),\
			db.func.avg(cls.value).label('avg'),\
			db.func.max(cls.value).label('max'),\
			db.func.min(cls.value).label('min'),\
			db.func.sum(cls.value)).filter(cls.itemid.in_(query_itemids)).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).all()

		return query_data_no_ground_2_arr(s)

class Zabbixhistoryuint(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'history_uint'
	itemid = db.Column('itemid',db.Integer,primary_key=True)
	clock = db.Column('clock',db.BigInteger,primary_key=True)
	value = db.Column('value',db.Float)
	ns = db.Column('ns',db.Integer)

	def __repr__(self):
		return "<zabbix history_uint itemid - %s value - %s at %s>" % (self.itemid,self.value,self.clock)

	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):

		if len(query_itemids) <= 0:
			return query_data_2_arr([])

		offset = ground // 10

		s = db.session.query(\
			db.func.count(cls.itemid).label('count'),\
			db.func.avg(cls.value).label('avg'),\
			db.func.max(cls.value).label('max'),\
			db.func.min(cls.value).label('min'),\
			db.func.floor((cls.clock + offset)/ground).label('minute'),\
			db.func.sum(cls.value)).filter(cls.itemid.in_(query_itemids)).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
			group_by('minute').all()


		return query_data_2_arr(s)


	@classmethod
	def get_interval_last_few_records(cls,query_itemids,time_since,time_till):

		if len(query_itemids) <= 0:
			return last_record_2_arr([])

		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			order_by(cls.clock.desc()).\
			limit(2*len(query_itemids)).all()

		return last_record_2_arr(s)

	@classmethod
	def get_interval_history_no_ground(cls,query_itemids,time_since,time_till):


		if len(query_itemids) <= 0:
			return query_data_no_ground_2_arr([])


		s = db.session.query(\
			db.func.count(cls.itemid).label('count'),\
			db.func.avg(cls.value).label('avg'),\
			db.func.max(cls.value).label('max'),\
			db.func.min(cls.value).label('min'),\
			db.func.sum(cls.value)).filter(cls.itemid.in_(query_itemids)).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).all()

		return query_data_no_ground_2_arr(s)


	@classmethod
	def get_interval_condition_record(cls,query_itemids,time_since,time_till,condition):

		if len(query_itemids) <= 0:
			return None

		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			filter('value ' + condition).all()

		return s if len(s) > 0 else None


class Zabbixhosts(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'hosts'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return "<zabbix host name - %s hostid - %s>" % (self.name,self.hostid)



class Zabbixitems(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'items'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return "<zabbix item name - %s itemid - %s>" % (self.name,self.itemid)

class Zabbixhostgroup(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'groups'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return "<zabbix group name - %s groupid - %s>" % (self.name,self.groupid)

def loadSession():
	session = db.create_scoped_session({'bind':engine})
	return session


class Zabbixinterface(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'interface'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return "<zabbix interface hostid - %s ip - %s>" % (self.hostid,self.ip)

class Zabbixapplication(db.Model):
	__tablename__ = 'applications'
	__bind_key__ = 'zabbix'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return '<zabbix applications applicationid %s name - %s>' % (self.applicationid,self.name)

class Zabbixitemapplication(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'items_applications'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return '<zabbix items_applications itemappid %s>' % (self.itemappid)

class Zabbixfunctions(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'functions'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return '<zabbix functions %s>' % (self.function)

class Zabbixtriggers(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'triggers'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return '<zabbix triggers %s>' % (self.expression)

class Zabbixactions(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'actions'
	__table_args__ = {'autoload':True,'autoload_with':engine}
	def __repr__(self):
		return '<zabbix actions %s>' % (self.name)


class Zabbixdrules(db.Model):
	__bind_key__ = 'zabbix'
	__tablename__ = 'drules'
	__table_args__ = {'autoload':True,'autoload_with':engine}
