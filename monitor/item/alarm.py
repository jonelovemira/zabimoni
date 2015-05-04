from monitor.item.models import Action,Trigger,Item,Calculateditem,Operation
from monitor.models import Attr
from monitor import db
from monitor.chart.displaychart import Chart
from monitor.zabbix.models import loadSession,Zabbixitems,Zabbixhosts
from monitor.functions import get_zabbix_server_ip,construct_random_str
import json
from datetime import datetime
from config import AREA,EMAIL_SNS_PATH,SNS_TOPIC_NAME_LABEL,SNS_SEND_SNS_2_LABLE,\
			ASG_FROM_GROUP_LABEL,ASG_ACTION_TYPE_LABEL,ASG_ACTION_NUMBER,\
			SNS_OPERATION_NAME,SNS_OPERATION_ATTR,ASG_OPERATION_NAME,ASG_OPERATION_ATTR,\
			AUTOSCALE_COMMAND_PATH,EMAIL_SNS_NEW_PATH
import boto.sns
from monitor.decorators import async

class Alarm():
	"""docstring for Alarm"""

	@classmethod
	def delete_alarm(cls,zabbix,triggerid):
		t = Trigger.query.get(triggerid)
		if t == None:
			raise Exception('Alarm do not exist')

		if t.calcitem is not None:
			zabbix.item_delete([t.calcitem.calculateditemid])
			cali = Calculateditem.query.get(t.calcitem.calculateditemid)
			if cali != None:
				db.session.delete(cali)

		zabbix.trigger_delete([t.triggerid])
		actionids = []
		for a in t.actions.all():
			actionids.append(a.actionid)

			for op in a.operations.all():
				for attr in op.attrs.all():
					db.session.delete(attr)

				db.session.delete(op)
			db.session.delete(a)
			
		zabbix.action_delete(actionids)
		db.session.delete(t)
	
	@classmethod
	def create_alarm(cls,args,zabbix):

		alarmname_values = args.get('alarmname',None)
		if alarmname_values == None:
			raise Exception('empty alarm name')

		comparetype_values = args.get('comparetype',None)
		if comparetype_values == None:
			raise Exception('empty compare type')

		alarmvalue_values = args.get('alarmvalue',None)
		if alarmvalue_values == None:
			raise Exception('empty alarm value')

		timeshift_values = args.get('timeshift',None)
		if timeshift_values is None:
			raise Exception('empty time shift')

		selected_metric_values = args.get('hiddenselectedmetric',None)
		if selected_metric_values is None:
			raise Exception('empty selected metrics')

		cls.action_cannot_empty_check(args)

		topicname_values = args.get('topicname',None)
		asggroups = args.get('asggroup',None)
		asgscaletypes = args.get('asgactiontype',None)

		receivers_values = args.get('receivers',None)
		
		# cls.topic_receiver_check(topicname_values,receivers_values)
		# cls.asg_check(asggroups,asgscaletypes)

		# alarm = Trigger(triggerid,triggername,triggervalue,timeshift,calcitem,triggerfunction)

		item = Chart.smr_2_itemlist(json.loads(selected_metric_values[0]))

		trigger_info = cls.get_trigger_info_from_items(item)


		trigger_expression = cls.get_trigger_expression(trigger_info['hostname'],trigger_info['itemname'],'last',alarmvalue_values[0],60,comparetype_values[0])



		triggerid = zabbix.trigger_create(trigger_expression,trigger_info['itemname'])

		trigger = Trigger(triggerid,alarmname_values[0],alarmvalue_values[0],timeshift_values[0],trigger_info['calculateditem'],'last',trigger_info['itemname'],comparetype_values[0])
		# triggerid,triggername,triggervalue,timeshift,calcitem,triggerfunction
		db.session.add(trigger)

		operations_args = cls.create_operations_args(args,trigger_info,alarmvalue_values[0],triggerid)

		actionid = cls.create_actions_for_trigger(zabbix,triggerid,trigger_info['hostid'],operations_args,alarmname_values[0])

		action = Action(actionid,trigger_info['itemname'],trigger)
		db.session.add(action)

		cls.create_operations(args,action)

	# @classmethod
	# def get_operation_str(operation):
	# 	op_attr_map = {SNS_OPERATION_NAME:SNS_OPERATION_ATTR,ASG_OPERATION_NAME:ASG_OPERATION_ATTR}

	# 	result = ''

	# 	attrs = op_attr_map.get(operation.operationname,None)

	# 	if attrs is None:
	# 		raise Exception('can not find operation in map')



	@classmethod
	def load_alarm(cls,triggerid):

		trigger = Trigger.query.get(triggerid)
		if trigger == None:
			raise Exception('alarm do not exist')

		load_result = {}

		load_result['Threshold'] = trigger.metricname + trigger.comparetype + str(trigger.triggervalue) + ' for ' + str(trigger.timeshift) + 's'

		actions_str = ''
		for a in trigger.actions.all():
			for op in a.operations.all():
				actions_str += op.operationname + ' '
				# cls.get_operation_str(op)
				for attr in op.attrs.all():
					actions_str += attr.attrname + ':' + str(attr.attrvalue) + ' '

		load_result['Actions'] = actions_str
		load_result['Metric Name'] = trigger.metricname

		return load_result
		# load_result['Period'] = 
		# load_result['Statistic'] = 'Average'

	@classmethod
	def create_operations(cls,args,action):
		topicname_values = args.get('topicname',None)
		asggroup = args.get('asggroup',None)
		asgscaletypes = args.get('asgactiontype',None)
		receivers_values = args.get('receivers',None)

		cls.action_cannot_empty_check(args)
		cls.asg_check(asggroup,asgscaletypes)
		cls.topic_receiver_check(topicname_values,receivers_values)

		if topicname_values != None:
			for x in range(len(topicname_values)):
				operation = Operation(SNS_OPERATION_NAME,action)
				db.session.add(operation)
				attr_topic_name = Attr(SNS_OPERATION_ATTR[0],topicname_values[x],None,None,operation)
				db.session.add(attr_topic_name)
				if x < len(receivers_values):
					attr_receivers = Attr(SNS_OPERATION_ATTR[1],receivers_values[x],None,None,operation)
					db.session.add(attr_receivers)

		if asggroup is not None:
			for x in range(len(asggroup)):
				operation = Operation(ASG_OPERATION_NAME,action)
				db.session.add(operation)
				attr_asggroup_name = Attr(ASG_OPERATION_ATTR[0],asggroup[x],None,None,operation)
				db.session.add(attr_asggroup_name)
				attr_asgscale_type = Attr(ASG_OPERATION_ATTR[1],asgscaletypes[x],None,None,operation)
				db.session.add(attr_asgscale_type)


	@classmethod
	def get_trigger_info_from_items(cls,item):
		trigger_info = None
		if len(item) == 0:
			raise Exception('Metric do not exist')
		elif len(item) > 1:
			trigger_info = cls.create_calculated_item(item,zabbix,alarmname_values[0])	
		else:
			trigger_info = cls.get_trigger_info_for_one_item(item[0])

		if trigger_info == {}:
			raise Exception('get trigger info error')

		return trigger_info

	@classmethod
	def topic_receiver_check(cls,topicname_values,receivers_values):
		# if topicname_values is not None :
		# 	if receivers_values is None or len(topicname_values) != len(receivers_values):
		# 		raise Exception('receivers for topic is not defined')
		return None

	@classmethod
	def asg_check(cls,asggroups,asgscaletypes):
		if asggroups is not None:
			if asgscaletypes is None or len(asggroups) != len(asgscaletypes):
				raise Exception('asggroups or asgscaletypes missing')


	@classmethod
	def create_actions_for_trigger(cls,zabbix,triggerid,hostid,operations,action_name):

		eventsource = 0
		conditions = [{"conditiontype": 1,
						"operator": 0,
						"value": hostid
						},
						{
							"conditiontype": 2,
							"operator": 0,
							"value": triggerid
						},
						{
							"conditiontype": 5,
							"operator": 0,
							"value": 1
						},
					]

		actionid = zabbix.action_create(action_name,eventsource,conditions,operations)

		# action =  Action(actionid,'','','',command,'mixed')
		# db.session.add(action)
		return actionid

	@classmethod
	def action_cannot_empty_check(cls,args):

		topicname_values = args.get('topicname',None)
		asggroup = args.get('asggroup',None)

		if topicname_values is None and asggroup is None:
			raise Exception('no actions defined')

	@classmethod
	def create_operations_args(cls,args,trigger_info,alarmvalue_value,triggerid):
		topicname_values = args.get('topicname',None)
		asggroup = args.get('asggroup',None)
		asgscaletypes = args.get('asgactiontype',None)

		receivers_values = args.get('receivers',None)

		cls.action_cannot_empty_check(args)

		cls.topic_receiver_check(topicname_values,receivers_values)
		cls.asg_check(asggroup,asgscaletypes)

		sns_operations = cls.create_SNS_operation_arg(topicname_values,receivers_values,trigger_info,alarmvalue_value,triggerid)

		## to do for asg operations
		asg_operations = cls.create_ASG_operation_arg(asggroup,asgscaletypes,triggerid)

		return sns_operations + asg_operations

	@classmethod
	def create_ASG_operation_arg(cls,asggroup,asgscaletypes,triggerid):
		operations = []

		if asggroup is None:
			return operations

		for index in range(len(asggroup)):
			tmp_command = AUTOSCALE_COMMAND_PATH + ' --asgroupname=' + asggroup[index] + ' --asgscaletype=' + asgscaletypes[index]
			operation = {
					"operationtype":1,
					"opcommand_hst":
					[
						{
							"hostid":0
						}
					],
					"opcommand" :
					{
						"type": 0,
						"command": tmp_command,
						"execute_on":1
					}
				}

			operations.append(operation)

		return operations


	@classmethod
	@async
	def send_subscriber(cls,con,topic_arn,emailaddress):
		emails = emailaddress.split(';')
		for e in emails:
			con.subscribe(topic_arn,'email', e)

	@classmethod
	def create_SNS_operation_arg(cls,topicname_values,receivers_values,trigger_info,alarmvalue_value,triggerid):

		operations = []

		more_info = "--hostinfo='" + trigger_info['hostinfo'] + "' --metricname='" + trigger_info['itemname'] + "' --alarmvalue='" + str(alarmvalue_value) + "' --currentvalue='" + '{ITEM.LASTVALUE}' + "'"

		if topicname_values is not None:
			for index in range(len(topicname_values)):
				tmp_topic_name = topicname_values[index].replace(' ','')

				tmp_topic_name += '-monitor_alarm'

				con = boto.sns.connect_to_region(AREA)

				res = con.create_topic(tmp_topic_name)
				topic_arn = ''
				try:
					topic_arn = res['CreateTopicResponse']['CreateTopicResult']['TopicArn']
				except Exception, e:
					raise e

				if topic_arn is not '' and len(receivers_values) == len(topicname_values):
					cls.send_subscriber(con,topic_arn,receivers_values[index])

				topic_arn = '--topicarn=' + topic_arn

				tmp_command = EMAIL_SNS_NEW_PATH + ' ' + topic_arn + ' ' + more_info

				operation = {
						"operationtype":1,
						"opcommand_hst":
						[
							{
								"hostid":0
							}
						],
						"opcommand" :
						{
							"type": 0,
							"command": tmp_command,
							"execute_on":1
						}
					}

				operations.append(operation)


		return operations



	# @classmethod
	# def create_action(cls,):

	# 	actionid = zabbix.action_create(name,eventsource,conditions,operations)

	@classmethod
	def get_trigger_expression(cls,hostname,itemname,func,triggervalue,timeshift,trigger_operator):

		expression = '{'
		expression += hostname
		expression += ':'
		expression += itemname
		expression += '.'
		expression += func
		expression += '('
		expression += str(timeshift)
		expression += ')'
		expression += '}'
		expression += trigger_operator
		expression += str(triggervalue)
		return expression

	@classmethod
	def get_trigger_info_for_one_item(cls,itemid):
		item = Item.query.get(itemid)

		if item == None:
			raise Exception('item do not exist')

		trigger_info = {}
		trigger_info['itemid'] = itemid
		trigger_info['itemname'] = item.itemtype.itemkey

		session = loadSession()
		zi = session.query(Zabbixitems).filter_by(itemid=itemid).first()
		hostid = zi.hostid
		hostname = session.query(Zabbixhosts).filter_by(hostid=hostid).first().name

		trigger_info['hostname'] = hostname
		trigger_info['hostid'] = hostid
		trigger_info['calculateditem'] = None
		hostinfo = cls.get_hostinfo_list_for_item([itemid])
		trigger_info['hostinfo'] =  hostinfo


		return trigger_info

	@classmethod
	def get_formula_for_items(cls,itemids):
		result = ''
		count = 0
		session = loadSession()
		try:
			for itemid in itemids:
				item_formula = ''
				if count == 0:
					count += 1
				else:
					item_formula = '+'

				item_formula += 'last("'
				
				zi = session.query(Zabbixitems).filter_by(itemid=itemid).first()
				hostid = zi.hostid
				hostname = session.query(Zabbixhosts).filter_by(hostid=hostid).first().name
				
				item_formula += hostname
				item_formula += ':'
				item_formula += zi.key_
				item_formula += '")'

				result += item_formula
			session.close()
		except Exception, e:
			raise Exception('get formula for item error, ' + str(e))

		return result

	@classmethod
	def create_calculate_item_on_monitor_server(cls,zabbix,formula,alarmname):
		result = {}
		session = loadSession()
		host = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
		session.close()
		

		day = datetime.today()
		daytime = day.strftime("%Y%m%d")
		itemname = alarmname + '_' + daytime + construct_random_str()
		calcitemid = zabbix.calc_item_create(itemname,host.hostid,formula)
		result['itemid'] = calcitemid
		result['itemname'] = itemname
		result['hostname'] = host.name
		result['hostid'] = host.hostid
		calc = Calculateditem(calcitemid,formula)
		db.session.add(calc)
		result['calculateditem'] = calc

		return result

	@classmethod
	def get_hostinfo_list_for_item(cls,itemids):
		tmp_result = []
		session = loadSession()
		try:
			for itemid in itemids:

				item = Item.query.get(itemid)

				if item is None:
					continue

				host = item.host

				tmp = host.hostname

				zi = session.query(Zabbixitems).filter_by(itemid=itemid).first()
				hostid = zi.hostid
				hostip = session.query(Zabbixhosts).filter_by(hostid=hostid).first().name

				tmp += '(' + hostip + ')'

				tmp_result.append(tmp)
				
			session.close()
		except Exception, e:
			raise Exception('get hostinfo for item error, ' + str(e))

		result = ''
		result = ';'.join(tmp_result)

		return result


	@classmethod
	def create_calculated_item(cls,items,zabbix,alarmname):

		trigger_info = {}

		if items == None:
			raise Exception('item do not exist')
		if zabbix == None:
			raise Exception('initiate zabbix_api instance first')

		calcitem_formula = cls.get_formula_for_items(items)

		hostinfo_list_for_item = cls.get_hostinfo_list_for_item(items)

		trigger_info = cls.create_calculate_item_on_monitor_server(zabbix,calcitem_formula,alarmname)
		trigger_info['hostinfo'] = hostinfo_list_for_item

		return trigger_info
		


