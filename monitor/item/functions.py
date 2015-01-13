#! flask/bin/python

from monitor.zabbix.zabbix_api import zabbix_api,get_zabbix_server_ip
from monitor import db
from monitor.item.models import Area,Service,Host,Item,Itemtype,Normalitemtype,Zbxitemtype,Itemdatatype,Calculateditem,Trigger,Action
from monitor.chart.models import Series
import boto.ec2
import boto.ec2.elb
from constants import *
from monitor.zabbix.models import Zabbixitems,Zabbixinterface,Zabbixhosts,loadSession
from monitor.chart.functions import construct_random_str
from monitor.MonitorException import *
from datetime import datetime
import sys,traceback

#################################################################
#################################################################
############ public function
def arg_2_array(arg=''):
	result = []

	if len(arg) > 0:
		if '@' in arg:
			result = arg.split('@')
		else:
				result.append(arg)
	return result

def get_elb_for_area(areaname):
	result = []
	try:
		con = boto.ec2.elb.connect_to_region(areaname)
		# for i in range(4):
		# 	result.append(areaname+str(i))
		elbs = con.get_all_load_balancers()
		for e in elbs:
			result.append(e.name)
		# result = ['1','2','3']
	except Exception, e:
		pass
	
	return result

def get_all_area_elb():
	result = {}

	try:
		regions = boto.ec2.regions()
		for r in regions:
			result[r.name] = get_elb_for_area(r.name)
	except Exception, e:
		pass
	
	return result

def add_host_register_in_elb(elbname,areaid):
	areaname = areaname = Area.query.filter_by(areaid=areaid).first().areaname
	con = boto.ec2.elb.connect_to_region(areaname)
	elbs = con.get_all_load_balancers([elbname])
	res = elbs[0].get_instance_health()
	instance_ids = [e.instance_id for e in res]
	con_r = boto.ec2.connect_to_region(areaname)
	resvs = con_r.get_all_instances(instance_ids)
	for r in resvs:
		for inst in r.instances:
			hostname = inst.tags['Name']
			host_ip = inst.private_ip_address
			print hostname,host_ip
			if host_ip == None:
				continue
			hostid = add_update_host(hostname, elbname,host_ip,areaname)
	# return instances



def nit_ait_sit_zit(area,service):
	allitemtypes = []
	ait = area.itemtypes.all()
	nit = Normalitemtype.query.first().itemtypes.all()
	sit = service.itemtypes.all()
	zit = Zbxitemtype.query.first().itemtypes.all()
	allitemtypes = list( set(ait) | set(nit) | set(sit) | set(zit))
	return allitemtypes

def get_old_allitemtype(host):
	items = host.items.all()
	oit = []
	for i in items:
		oit.append(i.itemtype)
	return oit

def get_host_interfaceid(hostid):
	session = loadSession()
	i = session.query(Zabbixinterface).filter_by(hostid=hostid).first()
	session.close()
	if i == None:
		raise IpAddressNotExist('ip address do not exists')
	interface_id = i.interfaceid
	return interface_id
#################################################################
#################################################################
#################################################################




#################################################################
#################################################################
#### host operations  #######
# preconditions : service exists, area exists, zabbixitemtype exists, normal itemtype exists, service itemtype exists       
def add_update_host(hostname, servicename,host_ip,areaname):

	zabbix = zabbix_api()

	try:
		# check preconditions
		print '.'*6 , " Checking for preconditions " , '.'*6
		area = Area.query.filter_by(areaname=areaname).first()
		if area == None:
			raise AreaNotExist('input area do not exists')

		service = Service.query.filter_by(servicename=servicename).first()
		if service == None:
			raise ServiceNotExist('input service do not exists')

		host_group_name = [HOST_GROUP_NAME]
		template_name = [TEMPLATE_NAME] 
					
		print "processing host: %s in service: %s ..." %  (hostname,servicename)

		#create host via zabbix api
		print "creating host if not exists via zabbix_api..."
		session = loadSession()
		checkh = session.query(Zabbixhosts).filter_by(name=host_ip).first()
		session.close()
		hostid = None
		if checkh == None:
			print host_ip,host_ip,host_group_name,template_name
			hostid = zabbix.host_create(host_ip,host_ip,host_group_name,template_name)
		else:
			hostid = checkh.hostid
			# dangerous to update as it will clear history data in zabbix database
			# host_update(hostid,hostname=None,host_ip=None)

		#create host in monitor database
		h1 = Host.query.filter_by(hostid = hostid).first()
		if h1 == None:
			h1 = Host(hostid,hostname,area,service)
			db.session.add(h1)

		# update the relationship between area and service
		t = h1.area.add_service(h1.service)
		if t != None:
			db.session.add(t)


		# delete in monitor database
		delete_itemids = []
		for i in h1.items:
			if i.itemtype == None:
				delete_itemids.append(i.itemid)
				db.session.delete(i)


		# delete in zabbix database
		try:
			zabbix.item_delete(delete_itemids)
		except Exception, e:
			pass
		

		# create items which is added later
		allitemtype = nit_ait_sit_zit(area,service)
		session = loadSession()
		for it in allitemtype:
			
			addbytem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
			
			itemid = None
			if addbytem == None and it.zabbixvaluetype == None:
				continue

			# do not exist in zabbix database will create now
			if addbytem == None:
				
				interface_id = get_host_interfaceid(hostid)
				itemid = zabbix.item_create(it.itemkey,hostid,host_ip,interface_id,2,it.zabbixvaluetype)
			else:
				itemid = addbytem.itemid
				print "update",itemid
				if it.zabbixvaluetype != None:
					try:
						zabbix.item_update(itemid,it.itemkey,2,it.zabbixvaluetype)
					except Exception as e:
						print e

			# add in monitor database if it do not exist
			addi = Item.query.filter_by(itemid = itemid).first()
			if addi == None:
				addi = Item(itemid,it.itemtypename,h1,it)
				db.session.add(addi)
		session.close()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		zabbix.rollback()
		raise MonitorException('can not add or update host',str(e))

	print "host: %s in service: %s add items complete!" %  (hostname,servicename)
	return hostid

def delete_host(hostid):
	host = Host.query.filter_by(hostid=hostid).first()
	if host == None:
		raise MonitorException('host to be delete does not exists')
	hostid = host.hostid
	items = host.items
	for i in items:
		db.session.delete(i)
	db.session.delete(host)
	zabbix = zabbix_api()
	zabbix.host_delete([hostid])


def add_host(hostname, servicename,host_ip,areaname):

	''' preconditions '''
	area = Area.query.filter_by(areaname=areaname).first()
	if area == None:
		raise AreaNotExist('input area do not exists')


	service = Service.query.filter_by(servicename=servicename).first()
	if service == None:
		raise ServiceNotExist('input service do not exists')


	host_group_name = [HOST_GROUP_NAME]
	template_name = [TEMPLATE_NAME] 
	hostid = None

	zabbix = zabbix_api()

	try:
		# add host record in zabbix database, template items will create now
		hostid = zabbix.host_create(host_ip,host_ip,host_group_name,template_name)

		# add host record in monitor database
		h1 = Host(hostid,hostname,area,service)
		db.session.add(h1)

		# all itemtype need to add
		allitemtype = nit_ait_sit_zit(area,service)
		session = loadSession()
		for it in allitemtype:
			
			addbytem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
			itemid = None

			if addbytem == None and it.zabbixvaluetype == None:
				continue

			# not template items
			if addbytem == None:
				interface_id = get_host_interfaceid(hostid)
				itemid = zabbix.item_create(it.itemkey,hostid,host_ip,interface_id,2,it.zabbixvaluetype)
			else:
				itemid = addbytem.itemid

			# add record in monitor database
			addi = Item(itemid,it.itemtypename,h1,it)
			db.session.add(addi)

			# update related chart series
			# s = Series.query.filter_by(host_id='').filter_by(aws_id='').filter_by(itemtype_id=it.itemtypeid).first()
			# if s != None:
			# 	if str(area.areaid) in s.area_id or str(service.serviceid) in s.service_id:
			# 		s.add_item(addi)
			# 		db.session.add(s)
		session.close()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		zabbix.rollback()
		raise Exception(' cannot create host',str(e))
	

	return hostid


def update_host(hostid,hostname,areaid,serviceid,host_ip=None):

	# checkout preconditions
	area = Area.query.filter_by(areaid=areaid).first()
	if area == None:
		raise AreaNotExist('area do not exists')

	service = Service.query.filter_by(serviceid=serviceid).first()
	if service == None:
		raise ServiceNotExist('service do not exists')

	host = Host.query.filter_by(hostid=hostid).first()
	if host == None:
		raise HostNotExist('host do not exists')

	zabbix = zabbix_api()
	try:
		# zabbix.update_host(hostid,host_ip)
		host.hostname = hostname
		host.area = area
		host.service = service

		# delete items in monitor database
		delete_itemids = []
		for i in host.items:
			if i.itemtype == None:
				delete_itemids.append(i.itemid)
				db.session.delete(i)

		# delete items in zabbix database
		try:
			zabbix.item_delete(delete_itemids)
		except Exception, e:
			pass

		envitemtype = nit_ait_sit_zit(area,service)
		hostitemtype = host.itemtypes.all()
		allitemtype = list( set(envitemtype) | set(hostitemtype) )

		# add items which added later
		session = loadSession()
		for it in allitemtype:
			item = it.items.filter_by(host_id=hostid).first()
			
			zitem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
			
			if item == None:
				# create item in zabbix database if it not exists
				if zitem != None:
					itemid = zitem.itemid
				else:
					itemid = zabbix.item_create(it.itemkey,hostid,None,None,2,it.zabbixvaluetype)

				# create item record in monitor database
				item = Item(itemid,it.itemtypename,host,it)
			else:
				# update in both zabbix database or monitor database
				if zitem.type != 0 and it.zabbixvaluetype != None:
					zabbix.item_update(item.itemid,it.itemkey,2,it.zabbixvaluetype)
				item.area = area
				item.itemtype = it
				item.service = service
				item.aws = it.aws

			db.session.add(item)
		session.close()
		db.session.add(host)
	except Exception, e:
		zabbix.rollback()
		raise Exception('can not update',str(e))
#################################################################
#################################################################
#################################################################



#################################################################
#################################################################
## add key ##
# will test on monitor server 
def it_test(key):
	session = loadSession()
	th = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
	session.close()
	if th == None:
		raise MonitorException('cannot check if the key can be added due to host is not available')

	hostid = th.hostid
	zabbix = zabbix_api()
	itemid = zabbix.item_create(key,hostid)

	try:
		if itemid != None:
			zabbix.item_delete([itemid])
	except Exception, e:
		pass


def add_itkey_to_host(hostid,it,zabbix):
	host = Host.query.filter_by(hostid=hostid).first()
	if host == None:
		raise HostNotExist('host do not exists')

	if it == None:
		raise MonitorException('it to be add do not exists')

	item = host.items.filter_by(itemname=it.itemtypename).first()
	if item != None:
		raise MonitorException(' item to be add in current host is already exist')

	session = loadSession()
	zitem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
	session.close()
	
	if zitem != None:
		itemid = zitem.itemid
	else:
		itemid = zabbix.item_create(it.itemkey,hostid,None,None,2,it.zabbixvaluetype)

	newitem = Item(itemid,it.itemtypename,host,it)

	db.session.add(newitem)


def add_it(o,key,itemdatatypeid,unitname,zabbixvaluetype):
	idt = Itemdatatype.query.filter_by(itemdatatypeid=itemdatatypeid).first()
	if idt == None:
		raise MonitorException('data type do not exists')
	#it_test(key)
	it = Itemtype.query.filter_by(itemtypename=key).first()
	if it == None:
		it = Itemtype(key,key,None,idt,unitname,zabbixvaluetype)
		db.session.add(it)

	htmp = o.add_itemtype(it)
	if htmp != None:
		db.session.add(htmp)

	return it

def find_hosts_and_add_key(kinds,o,it,zabbix):
	hosts = None
	if kinds == 1:
		hosts = Host.query.all()
	elif kinds == 4:
		hosts = [o]
	else:
		hosts = o.hosts.all()

	for h in hosts:
		add_itkey_to_host(h.hostid,it,zabbix)
		# update_host(h.hostid,h.hostname,h.area.areaid,h.service.serviceid)

def find_object_2_action(kinds,indexid):
	if kinds > 4 :
		raise MonitorException('kind of adding itemtype out of range')
	kind_o_map = {BY_ALL:[Normalitemtype,'normalitemtypeid'],BY_AREA:[Area,'areaid'],BY_SERVICE:[Service,'serviceid'],BY_HOST:[Host,'hostid']}
	arr = kind_o_map.get(kinds,[Service,'serviceid'])
	# print "arr",arr
	o = arr[0].query.filter(arr[1] + '=' + str(indexid)).first()
	return o

def add_key(kinds,indexid,key,itemdatatypeid,unitname,zabbixvaluetype,zabbix):
	kinds = int(kinds)
	if indexid == None:
		indexid = 1
	o = find_object_2_action(kinds,indexid)
	# print o
	it = add_it(o,key,itemdatatypeid,unitname,zabbixvaluetype)

	find_hosts_and_add_key(kinds,o,it,zabbix)

## add key ##
#################################################################
#################################################################



#################################################################
#################################################################
#################################################################
#################  calculate items,trigger and actions  #########
def get_formula_for_items(itemids):
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
	finally:
		pass

	return result

def create_calculated_items_formula(scale,scale_operator,first_itemids,fs_operator,second_itemids,brackets_position = 1):
	final_formula = ''
	# final_formula += str(scale)
	# final_formula += scale_operator
	
	first_itemids_formula = get_formula_for_items(first_itemids)

	if len(first_itemids_formula) != 0:
		first_itemids_formula = '(' + first_itemids_formula + ')'
	else:
		scale_operator = ''
	# final_formula += first_itemids_formula

	# final_formula += fs_operator

	second_itemids_formula = get_formula_for_items(second_itemids)

	if len(second_itemids_formula) != 0:
		second_itemids_formula = '(' + second_itemids_formula +')'
	else:
		fs_operator = ''

	if len(first_itemids_formula) == 0 and len(second_itemids_formula) == 0:
		return str(scale)
	
	# final_formula += second_itemids_formula

	if brackets_position == 1:
		final_formula += '('
		final_formula += str(scale)
		final_formula += scale_operator
		final_formula += first_itemids_formula
		final_formula += ')'
		final_formula += fs_operator
		final_formula += second_itemids_formula
	else:
		final_formula += str(scale)
		final_formula += scale_operator
		final_formula += '('
		final_formula += first_itemids_formula
		final_formula += fs_operator
		final_formula += second_itemids_formula
		final_formula += ')'

	return final_formula

def get_valid_hostid(first,second):
	total = list( set(first) | set(second) )
	result = None
	session = loadSession()
	for itemid in total:
		
		item = session.query(Zabbixitems).filter_by(itemid=itemid).first()
		if item != None:
			result = session.query(Zabbixhosts).filter_by(hostid=item.hostid).first()
			break
	session.close()
	return result

def create_calculate_item(zabbix,hostid,formula):
	result = {}
	day = datetime.today()
	daytime = day.strftime("%Y%m%d")
	itemname = daytime + construct_random_str()
	calcitemid = zabbix.calc_item_create(itemname,hostid,formula)
	result['itemid'] = calcitemid
	result['itemname'] = itemname
	return result

def get_trigger_expression(hostname,itemname,func,triggervalue,timeshift,equality):
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
	expression += equality
	expression += str(triggervalue)
	return expression

def get_action_name(command_path):
	if len(command_path) == 0 :
		return ''
	split_result1 = command_path.split('/')
	split_result2 = split_result1[len(split_result1) - 1].split(' ')
	result = split_result2[0].split('.')[0]
	if len(result) >= 80:
		result = result[0:80]

	return result

def create_calcitem_trigger_action(zabbix,formula,functiontype,triggervalue,timeshift,trigger_operator,\
									command):

	session = loadSession()
	host = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
	session.close()
	iteminfo = create_calculate_item(zabbix,host.hostid,formula)

	# save in monitor database
	calcitem = Calculateditem(iteminfo['itemid'],formula)
	db.session.add(calcitem)

	# add trigger and action both in zabbix and monitor
	hostname = host.name
	expression = get_trigger_expression(hostname,iteminfo['itemname'],functiontype,triggervalue,timeshift,trigger_operator)
	name = iteminfo['itemname']

	result = {}
	# in zabbix
	triggerid = zabbix.trigger_create(expression,name)

	
	content = "'" + functiontype + ' of ' + formula + ' ' + trigger_operator + ' ' + triggervalue + ' for ' + timeshift + 's' +"'"

	# in monitor 
	# trigger = Trigger(triggerid,name,triggervalue,timeshift,calcitem)
	# db.session.add(trigger)

	# add action in zabbix
	eventsource = 0
	conditions = [{"conditiontype": 1,
					"operator": 0,
					"value": host.hostid
					},
					{
						"conditiontype": 2,
						"operator": 0,
						"value": triggerid
					}
				]
	operations = [
				{
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
						"command":command + ' ' + content,
						"execute_on":1
					}
				}
				]

	actionid = zabbix.action_create(name,eventsource,conditions,operations)

	result['trigger_name'] = name
	result['trigger_id'] = triggerid
	result['calcitem'] = calcitem
	result['actionid'] = actionid

	return result

	# add action in monitor
	# actionname = get_action_name(command_path)
	# action =  Action(actionid,autoscalegroupname,autoscaletype,areaid,command_path,actionname)
	# db.session.add(action)

	# # add relationship between trigger and action
	# ttmp = trigger.add_action(action)
	# if ttmp != None:
	# 	db.session.add(ttmp)



# use current host
def create_calcitem_trigger_action2(zabbix,formula,functiontype,triggervalue,timeshift,trigger_operator,\
									command_path,autoscalegroupname,autoscaletype,areaid):

	#generate calculate item in zabbix
	session = loadSession()
	host = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
	session.close()
	iteminfo = create_calculate_item(zabbix,host.hostid,formula)
	

	# save in monitor database
	calcitem = Calculateditem(iteminfo['itemid'],formula)
	db.session.add(calcitem)

	# add trigger and action both in zabbix and monitor
	hostname = host.name
	expression = get_trigger_expression(hostname,iteminfo['itemname'],functiontype,triggervalue,timeshift,trigger_operator)
	name = iteminfo['itemname']
	
	# in zabbix
	triggerid = zabbix.trigger_create(expression,name)

	# in monitor 
	trigger = Trigger(triggerid,name,triggervalue,timeshift,calcitem)
	db.session.add(trigger)

	# add action in zabbix
	eventsource = 0
	conditions = [{"conditiontype": 1,
					"operator": 0,
					"value": host.hostid
					},
					{
						"conditiontype": 2,
						"operator": 0,
						"value": triggerid
					}
				]
	operations = [
				{
					"operationtype":1,
					"opcommand_hst":
					[
						{
							"hostid":host.hostid
						}
					],
					"opcommand" :
					{
						"type": 0,
						"command":command_path,
						"execute_on":1
					}
				}
				]

	actionid = zabbix.action_create(name,eventsource,conditions,operations)

	# add action in monitor
	actionname = get_action_name(command_path)
	action =  Action(actionid,autoscalegroupname,autoscaletype,areaid,command_path,actionname)
	db.session.add(action)

	# add relationship between trigger and action
	ttmp = trigger.add_action(action)
	if ttmp != None:
		db.session.add(ttmp)

# def test_create_calcitem_trigger_action():
# 	zabbix = zabbix_api()
# 	scale = '1'
# 	scale_operator = '*'
# 	first_itemids = [37677,37628]
# 	fs_operator = ''
# 	second_itemids = []

# 	triggervalue = 100
# 	timeshift = 60
# 	functiontype = 'min'
# 	trigger_operator = '>'

# 	command_path = '/home/jone/flask_project/monitor-0.3.7/command/test_remote_command.py'
# 	autoscalegroupname = 'test autoscale group'
# 	autoscaletype = '1'
# 	areaid = '1'

# 	try:
# 		create_calcitem_trigger_action(zabbix,scale,scale_operator,first_itemids,fs_operator,second_itemids,\
# 									functiontype,triggervalue,timeshift,trigger_operator,\
# 									command_path,autoscalegroupname,autoscaletype,areaid)
# 		db.session.commit()
# 	except Exception, e:
# 		db.session.rollback()
# 		zabbix.rollback()
# 		raise e
# 	finally:
# 		db.session.remove()

#################################################################
#################################################################
#################################################################






