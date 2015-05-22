# from monitor import db,app
from monitor import app,db
# from monitor.item.models import Item

engine = db.get_engine(app,bind='zabbix')


def history_data_2_arr(s):
	result = []
	last_count = 0
	for i in range(0,len(s)):
		if len(result) == 0:
			result.append([int(s[i][1]),float(s[i][2]),float(s[i][3]),float(s[i][4]),long(s[i][5]),float(s[i][6])])
			last_count = 1
		else:
			if s[i][5] == result[len(result) -1][4]:
				result[len(result) - 1][0] += int(s[i][1])
				result[len(result) - 1][1] += float(s[i][2])
				if result[len(result) - 1][2] < float(s[i][3]):
					result[len(result) - 1][2] = float(s[i][3])
				if result[len(result) - 1][3] > float(s[i][4]):
					result[len(result) - 1][3] = float(s[i][4])

				result[len(result) -1][5] += float(s[i][6])
				last_count += 1
			else:
				result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
				result.append([int(s[i][1]),float(s[i][2]),float(s[i][3]),float(s[i][4]),long(s[i][5]),float(s[i][6])])
				last_count = 1
	
	if last_count > 1:
		result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
		

	if len(result) != 0:
		return result
	return None

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
					tmp_arr_after_query.append(int(query_result[i].clock)//ground)
					s1.append(tmp_arr_after_query)
					same_count = 1
				else:
					if int(query_result[i].clock)//ground == s1[len(s1) -1][5]:
						s1[len(s1) - 1][1] += 1
						s1[len(s1) - 1][2] += float(query_result[i].value)
						if s1[len(s1) - 1][3] < float(query_result[i].value):
							s1[len(s1) - 1][3] = float(query_result[i].value)
						if s1[len(s1) - 1][4] > float(query_result[i].value):
							s1[len(s1) - 1][4] = float(query_result[i].value)
						same_count += 1
					else:
						s1[len(s1) - 1][2] = s1[len(s1) - 1][2]//same_count
						ttmp_arr_after_query = []
						ttmp_arr_after_query.append(int(query_result[i].itemid))
						ttmp_arr_after_query.append(1)
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(int(query_result[i].clock)//ground)
						s1.append(ttmp_arr_after_query)
						same_count = 1
			if same_count > 1:
				s1[len(s1) - 1][2] = s1[len(s1) - 1][2]//same_count

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
					result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
		
		if len(result) != 0:
			return result		
		return None

	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):
		# tmp_s = []
		# for qi in query_itemids:
		# 	time_frequency = Item.query.get(qi).itemtype.time_frequency
		# 	s1 = db.session.query(cls.itemid,\
		# 		db.func.count(cls.itemid).label('count'),\
		# 		db.func.avg(cls.value).label('avg'),\
		# 		db.func.max(cls.value).label('max'),\
		# 		db.func.min(cls.value).label('min'),\
		# 		db.func.floor((cls.clock)/ground).label('minute'),
		# 		cls.value ).\
		# 	filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
		# 	group_by('minute').all()

		# 	# print s1
		# 	tmp_s += s1

		# s = sorted(tmp_s,key = lambda x:x[5])

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
		# return history_data_2_arr(s)

	@classmethod
	def get_interval_last_few_records(cls,query_itemids,time_since,time_till):
		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			order_by(cls.clock.desc()).\
			limit(2*len(query_itemids)).all()

		return last_record_2_arr(s)

	@classmethod
	def get_interval_condition_record(cls,query_itemids,time_since,time_till,condition):
		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			filter('value ' + condition).all()

		return s if len(s) > 0 else None

	@classmethod
	def get_interval_history_no_ground(cls,query_itemids,time_since,time_till):
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
					tmp_arr_after_query.append(int(query_result[i].clock)//ground)
					s1.append(tmp_arr_after_query)
					same_count = 1
				else:
					if int(query_result[i].clock)//ground == s1[len(s1) -1][5]:
						s1[len(s1) - 1][1] += 1
						s1[len(s1) - 1][2] += float(query_result[i].value)
						if s1[len(s1) - 1][3] < float(query_result[i].value):
							s1[len(s1) - 1][3] = float(query_result[i].value)
						if s1[len(s1) - 1][4] > float(query_result[i].value):
							s1[len(s1) - 1][4] = float(query_result[i].value)
						same_count += 1
					else:
						s1[len(s1) - 1][2] = s1[len(s1) - 1][2]//same_count
						ttmp_arr_after_query = []
						ttmp_arr_after_query.append(int(query_result[i].itemid))
						ttmp_arr_after_query.append(1)
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(float(query_result[i].value))
						ttmp_arr_after_query.append(int(query_result[i].clock)//ground)
						s1.append(ttmp_arr_after_query)
						same_count = 1

			if same_count > 1:
				s1[len(s1) - 1][2] = s1[len(s1) - 1][2]//same_count

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
					result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
					result.append(list(s[i][1:6]))
					last_count = 1
		if last_count > 1:
			result[len(result) - 1][1] = result[len(result) - 1][1]//last_count
			
		if len(result) != 0:
			return result		
		return None

	@classmethod
	def get_interval_history(cls,query_itemids,ground,time_since,time_till):
		# tmp_s = []
		# for qi in query_itemids:
		# 	time_frequency = Item.query.get(qi).itemtype.time_frequency
		# 	s1 = db.session.query(cls.itemid,\
		# 		db.func.count(cls.itemid).label('count'),\
		# 		db.func.avg(cls.value).label('avg'),\
		# 		db.func.max(cls.value).label('max'),\
		# 		db.func.min(cls.value).label('min'),\
		# 		db.func.floor((cls.clock)/ground).label('minute'),\
		# 		cls.value).\
		# 	filter_by(itemid = qi).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).\
		# 	group_by('minute').all()

		# 	# print s1
		# 	tmp_s += s1

		# s = sorted(tmp_s,key = lambda x:x[5])

		# return history_data_2_arr(s)

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
		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			order_by(cls.clock.desc()).\
			limit(2*len(query_itemids)).all()

		return last_record_2_arr(s)

	@classmethod
	def get_interval_history_no_ground(cls,query_itemids,time_since,time_till):
		s = db.session.query(\
			db.func.count(cls.itemid).label('count'),\
			db.func.avg(cls.value).label('avg'),\
			db.func.max(cls.value).label('max'),\
			db.func.min(cls.value).label('min'),\
			db.func.sum(cls.value)).filter(cls.itemid.in_(query_itemids)).filter('clock >=' + str(time_since)).filter('clock <=' + str(time_till)).all()

		return query_data_no_ground_2_arr(s)


	@classmethod
	def get_interval_condition_record(cls,query_itemids,time_since,time_till,condition):
		s = db.session.query(cls.itemid,cls.clock,cls.value).\
			filter(cls.itemid.in_(query_itemids)).\
			filter('clock >=' + str(time_since)).\
			filter('clock <=' + str(time_till)).\
			filter('value ' + condition).all()

		return s if len(s) > 0 else None
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
