# from monitor import db,app
from monitor import app,db

engine = db.get_engine(app,bind='zabbix')

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
	def get_update_history(cls,query_itemids,ground,time_since,time_till):
		tmp_s = []
		for qi in query_itemids:
			query_result = cls.query.filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).all()
			s1 = []
			same_count = 0
			for i in range(0,len(query_result)):
				if len(s1) == 0:
					tmp_arr_after_query = []
					tmp_arr_after_query.append(int(query_result[i].itemid))
					tmp_arr_after_query.append(1)
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(int(query_result[i].clock)/ground)
					s1.append(tmp_arr_after_query)
					same_count = 1
				else:
					if int(query_result[i].clock)/ground == s1[len(s1) -1][5]:
						s1[len(s1) - 1][1] += 1
						s1[len(s1) - 1][2] += float(query_result[i].value)
						if s1[len(s1) - 1][3] < float(query_result[i].value):
							s1[len(s1) - 1][3] = float(query_result[i].value)
						if s1[len(s1) - 1][4] > float(query_result[i].value):
							s1[len(s1) - 1][4] = float(query_result[i].value)
						same_count += 1
					else:
						s1[len(s1) - 1][2] = s1[len(s1) - 1][2]/same_count
						ttmp_arr_after_query = []
						ttmp_arr_after_query.append(int(query_result[i].itemid))
						ttmp_arr_after_query.append(1)
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(int(query_result[i].clock)/ground)
						s1.append(ttmp_arr_after_query)
						same_count = 1
			if same_count > 1:
				s1[len(s1) - 1][2] = s1[len(s1) - 1][2]/same_count

			s1 = db.session.query(cls.itemid,\
				db.func.count(cls.itemid).label('count'),\
				db.func.avg(cls.value).label('avg'),\
				db.func.max(cls.value).label('max'),\
				db.func.min(cls.value).label('min'),\
				db.func.floor((cls.clock)/ground).label('minute') ). \
			filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
			group_by('minute').all()

			# print s1
			tmp_s += s1

		s = sorted(tmp_s,key = lambda x:x[5])

		result = []
		last_count = 0
		for i in range(0,len(s)):
			if len(result) == 0:
				result.append(list(s[i][1:6]))
				last_count = 1
			else:
				if s[i][5] == result[len(result) -1][4]:
					result[len(result) - 1][0] += s[i][1]
					result[len(result) - 1][1] += s[i][2]
					if result[len(result) - 1][2] < s[i][3]:
						result[len(result) - 1][2] = s[i][3]
					if result[len(result) - 1][3] > s[i][4]:
						result[len(result) - 1][3] = s[i][4]
					last_count += 1
				else:
					result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
		
		if len(result) != 0:
			return result		
		return None

	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):
		tmp_s = []
		for qi in query_itemids:
			s1 = db.session.query(cls.itemid,\
				db.func.count(cls.itemid).label('count'),\
				db.func.avg(cls.value).label('avg'),\
				db.func.max(cls.value).label('max'),\
				db.func.min(cls.value).label('min'),\
				db.func.floor((cls.clock)/ground).label('minute') ). \
			filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
			group_by('minute').all()

			# print s1
			tmp_s += s1

		s = sorted(tmp_s,key = lambda x:x[5])

		result = []
		last_count = 0
		for i in range(0,len(s)):
			if len(result) == 0:
				result.append(list(s[i][1:6]))
				last_count = 1
			else:
				if s[i][5] == result[len(result) -1][4]:
					result[len(result) - 1][0] += s[i][1]
					result[len(result) - 1][1] += s[i][2]
					if result[len(result) - 1][2] < s[i][3]:
						result[len(result) - 1][2] = s[i][3]
					if result[len(result) - 1][3] > s[i][4]:
						result[len(result) - 1][3] = s[i][4]
					last_count += 1
				else:
					result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
		
		if len(result) != 0:
			return result		
		return None


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
	def get_update_history(cls,query_itemids,ground,time_since,time_till):
		tmp_s = []
		for qi in query_itemids:
			query_result = cls.query.filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).all()
			s1 = []
			same_count = 0
			for i in range(0,len(query_result)):
				if len(s1) == 0:
					tmp_arr_after_query = []
					tmp_arr_after_query.append(int(query_result[i].itemid))
					tmp_arr_after_query.append(1)
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(float(query_result[i].value))
					tmp_arr_after_query.append(int(query_result[i].clock)/ground)
					s1.append(tmp_arr_after_query)
					same_count = 1
				else:
					if int(query_result[i].clock)/ground == s1[len(s1) -1][5]:
						s1[len(s1) - 1][1] += 1
						s1[len(s1) - 1][2] += float(query_result[i].value)
						if s1[len(s1) - 1][3] < float(query_result[i].value):
							s1[len(s1) - 1][3] = float(query_result[i].value)
						if s1[len(s1) - 1][4] > float(query_result[i].value):
							s1[len(s1) - 1][4] = float(query_result[i].value)
						same_count += 1
					else:
						s1[len(s1) - 1][2] = s1[len(s1) - 1][2]/same_count
						ttmp_arr_after_query = []
						ttmp_arr_after_query.append(int(query_result[i].itemid))
						ttmp_arr_after_query.append(1)
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(int(query_result[i].clock)/ground)
						s1.append(ttmp_arr_after_query)
						same_count = 1

			if same_count > 1:
				s1[len(s1) - 1][2] = s1[len(s1) - 1][2]/same_count

			tmp_s += s1

		s = sorted(tmp_s,key = lambda x:x[5])

		result = []
		last_count = 0
		for i in range(0,len(s)):
			if len(result) == 0:
				result.append(list(s[i][1:6]))
				last_count = 1
			else:
				if s[i][5] == result[len(result) -1][4]:
					result[len(result) - 1][0] += s[i][1]
					result[len(result) - 1][1] += s[i][2]
					if result[len(result) - 1][2] < s[i][3]:
						result[len(result) - 1][2] = s[i][3]
					if result[len(result) - 1][3] > s[i][4]:
						result[len(result) - 1][3] = s[i][4]
					last_count += 1
				else:
					result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
			
		if len(result) != 0:
			return result		
		return None

	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):
		tmp_s = []
		for qi in query_itemids:
			s1 = db.session.query(cls.itemid,\
				db.func.count(cls.itemid).label('count'),\
				db.func.avg(cls.value).label('avg'),\
				db.func.max(cls.value).label('max'),\
				db.func.min(cls.value).label('min'),\
				db.func.floor((cls.clock)/ground).label('minute') ). \
			filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
			group_by('minute').all()

			# print s1
			tmp_s += s1

		s = sorted(tmp_s,key = lambda x:x[5])

		result = []
		last_count = 0
		for i in range(0,len(s)):
			if len(result) == 0:
				result.append(list(s[i][1:6]))
				last_count = 1
			else:
				if s[i][5] == result[len(result) -1][4]:
					result[len(result) - 1][0] += s[i][1]
					result[len(result) - 1][1] += s[i][2]
					if result[len(result) - 1][2] < s[i][3]:
						result[len(result) - 1][2] = s[i][3]
					if result[len(result) - 1][3] > s[i][4]:
						result[len(result) - 1][3] = s[i][4]
					last_count += 1
				else:
					result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]/last_count
		
		if len(result) != 0:
			return result		
		return None

# def get_init_result(query_itemids,ground):

# 	return Zabbixhistory.get_init_history(query_itemids,ground) + Zabbixhistoryuint.get_init_history(query_itemids,ground)

# def get_update_result(query_itemids,ground,time_since,time_till):

# 	return Zabbixhistory.get_update_history(query_itemids,ground) + Zabbixhistoryuint.get_update_history(query_itemids,ground)

# Base = db.make_declarative_base()

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