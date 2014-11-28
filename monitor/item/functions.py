#! flask/bin/python

from monitor.zabbix_api import zabbix_api,get_zabbix_server_ip
from monitor import db
from monitor.item.models import Area,Service,Host,Item,Itemtype,Normalitemtype,Zbxitemtype,Itemdatatype
from monitor.chart.models import Series
import boto.ec2
import boto.ec2.elb
from constants import *
from monitor.zabbix import Zabbixitems,Zabbixapplication,Zabbixitemapplication,loadSession,Zabbixinterface,Zabbixhosts
from monitor.chart.functions import get_all_itemtypes
from monitor.MonitorException import *

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
	if i == None:
		raise IpAddressNotExist('ip address do not exists')
	interface_id = i.interfaceid
	return interface_id

# preconditions : service exists, area exists, zabbixitemtype exists, normal itemtype exists, service itemtype exists 
#       
def add_update_host(hostname, servicename,host_ip,areaname):

	zabbix = zabbix_api()

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
	print "creating host via zabbix_api..."
	session = loadSession()
	checkh = session.query(Zabbixhosts).filter_by(name=host_ip).first()
	session.close()
	hostid = None
	if checkh == None:
		print host_ip,host_ip,host_group_name,template_name
		hostid = zabbix.host_create(host_ip,host_ip,host_group_name,template_name)
	else:
		hostid = checkh.hostid

	#create host in monitor database
	h1 = Host.query.filter_by(hostid = hostid).first()
	if h1 == None:
		h1 = Host(hostid,hostname,area,service)
		db.session.add(h1)

	# update the relationship between area and service
	t = h1.area.add_service(h1.service)
	if t != None:
		db.session.add(t)

	for i in h1.items:
		if i.itemtype == None:
			try:
				zabbix.item_delete(i.itemid)
			except Exception, e:
				pass
			session = loadSession()
			c = session.query(Zabbixitems).filter_by(itemid=i.itemid).count()
			session.close()
			if c > 0:
				raise MonitorException('can not delete by zabbix api')
			db.session.delete(i)

	
	allitemtype = nit_ait_sit_zit(area,service)

	
	for it in allitemtype:
		session = loadSession()
		addbytem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
		session.close()
		itemid = None
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

		if itemid == None:
			db.session.rollback()
			raise ItemCannotCreate('Item cannot create by zabbix api')

		addi = Item.query.filter_by(itemid = itemid).first()
		if addi == None:
			addi = Item(itemid,it.itemtypename,h1,it)
			db.session.add(addi)

	db.session.commit()

	print "host: %s in service: %s add items complete!" %  (hostname,servicename)
	return hostid

def delete_host(hostid):
	zabbix = zabbix_api()
	host = Host.query.filter_by(hostid=hostid).first()
	if host == None:
		raise MonitorException('host to be delete does not exists')
	hostid = host.hostid
	items = host.items
	for i in items:
		db.session.delete(i)
	db.session.delete(host)
	zabbix.host_delete([hostid])


def add_host(hostname, servicename,host_ip,areaname):

	zabbix = zabbix_api()

	''' preconditions '''
	area = Area.query.filter_by(areaname=areaname).first()
	if area == None:
		raise AreaNotExist('input area do not exists')


	service = Service.query.filter_by(servicename=servicename).first()
	if service == None:
		raise ServiceNotExist('input service do not exists')


	host_group_name = [HOST_GROUP_NAME]
	template_name = [TEMPLATE_NAME] 
				
	hostid = zabbix.host_create(host_ip,host_ip,host_group_name,template_name)

	h1 = Host(hostid,hostname,area,service)
	db.session.add(h1)

	allitemtype = nit_ait_sit_zit(area,service)


	for it in allitemtype:
		session = loadSession()
		addbytem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
		session.close()
		itemid = None
		if addbytem == None:
			interface_id = get_host_interfaceid(hostid)
			itemid = zabbix.item_create(it.itemkey,hostid,host_ip,interface_id,2,it.zabbixvaluetype)
		else:
			itemid = addbytem.itemid

		addi = Item(itemid,it.itemtypename,h1,it)
		db.session.add(addi)

		# update related chart series
		s = Series.query.filter_by(host_id='').filter_by(aws_id='').filter_by(itemtype_id=it.itemtypeid).first()
		if s != None:
			if str(area.areaid) in s.area_id or str(service.serviceid) in s.service_id:
				s.add_item(addi)
				db.session.add(s)	


	return hostid

# def is_zabbix_item_changed(item,it):
# 	if item.itemname != it.itemtypename:
# 		return True
# 	if 


def update_host(hostid,hostname,areaid,serviceid,host_ip=None):

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
	# zabbix.update_host(hostid,host_ip)

	host.hostname = hostname
	host.area = area
	host.service = service

	envitemtype = nit_ait_sit_zit(area,service)
	hostitemtype = host.itemtypes.all()

	allitemtype = list( set(envitemtype) | set(hostitemtype) )

	# olditemtype = get_old_allitemtype(host)

	for i in host.items:
		if i.itemtype == None:
			try:
				zabbix.item_delete(i.itemid)
			except Exception, e:
				pass
			session = loadSession()
			c = session.query(Zabbixitems).filter_by(itemid=i.itemid).count()
			session.close()
			if c > 0:
				raise MonitorException('can not delete by zabbix api')
			db.session.delete(i)

	for it in allitemtype:
		item = it.items.filter_by(host_id=hostid).first()
		if item == None:
			# create
			interface_id = get_host_interfaceid(hostid)
			session = loadSession()
			zitem = session.query(Zabbixitems).filter_by(hostid=hostid,key_=it.itemkey).first()
			session.close()
			if zitem != None:
				itemid = zitem.itemid
			else:
				itemid = zabbix.item_create(it.itemkey,hostid,None,None,2,it.zabbixvaluetype)
			item = Item(itemid,it.itemtypename,host,it)
		else:
			# update
			zabbix.item_update(item.itemid,it.itemkey,2,it.zabbixvaluetype)
			item.area = area
			item.itemtype = it
			item.service = service
			item.aws = it.aws
			
		db.session.add(item)

	db.session.add(host)

def it_test(key):
	session = loadSession()
	th = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
	session.close()
	if th == None:
		raise MonitorException('cannot check the if the key can be added due to host is not available')

	hostid = th.hostid
	zabbix = zabbix_api()
	itemid = zabbix.item_create(key,hostid)

	if itemid != None:
		zabbix.item_delete(itemid)

def add_it(o,key,itemdatatypeid,unitname,zabbixvaluetype):
	idt = Itemdatatype.query.filter_by(itemdatatypeid=itemdatatypeid).first()
	if idt == None:
		raise MonitorException('data type do not exists')
	it_test(key)
	it = Itemtype.query.filter_by(itemtypename=key).first()
	if it == None:
		it = Itemtype(key,key,None,idt,unitname,zabbixvaluetype)
		db.session.add(it)

	htmp = o.add_itemtype(it)
	if htmp != None:
		db.session.add(htmp)

def update_key_to_host(kinds,o):
	print "kinds",kinds
	hosts = None
	if kinds == 1:
		hosts = Host.query.all()
	elif kinds == 4:
		hosts = [o]
	else:
		hosts = o.hosts.all()

	for h in hosts:
		print h
		update_host(h.hostid,h.hostname,h.area.areaid,h.service.serviceid)


def find_object_2_action(kinds,indexid):
	if kinds > 4 :
		raise MonitorException('kind of adding itemtype out of range')
	kind_o_map = {BY_ALL:[Normalitemtype,'normalitemtypeid'],BY_AREA:[Area,'areaid'],BY_SERVICE:[Service,'serviceid'],BY_HOST:[Host,'hostid']}
	arr = kind_o_map.get(kinds,[Service,'serviceid'])
	# print "arr",arr
	o = arr[0].query.filter(arr[1] + '=' + str(indexid)).first()
	return o

def add_key(kinds,indexid,key,itemdatatypename,unitname,zabbixvaluetype):
	kinds = int(kinds)
	if indexid == None:
		indexid = 1
	o = find_object_2_action(kinds,indexid)
	# print o
	add_it(o,key,itemdatatypename,unitname,zabbixvaluetype)

	update_key_to_host(kinds,o)

# def test_add():
# 	zit = Zbxitemtype()
# 	db.session.add(zit)
# 	raise MonitorException('test')
	












