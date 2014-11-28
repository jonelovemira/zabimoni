#! flask/bin/python

from monitor.zabbix_api import zabbix_api
import boto
from boto.ec2 import cloudwatch
from monitor import db
from monitor.auth.models import User

from monitor.item.models import Area,Service,Host,Item,Itemtype,Aws,Itemdatatype,Normalitemtype,Zbxitemtype
import boto.ec2
from constants import *
from monitor.zabbix import Zabbixapplication,Zabbixitemapplication,Zabbixitems,loadSession,Zabbixhosts,Zabbixinterface

from monitor.item.functions import add_update_host

import os,StringIO,ConfigParser,traceback,sys

################################           add aws            ####################################
def init_aws():
	arr = ['By All','By ServiceName','By LinkedAccount','By ServiceName and LinkedAccount']

	for r in arr:
		aws = Aws.query.filter_by(awsname=r).first()
		if aws == None:
			aws = Aws(awsname=r,area=None)
			db.session.add(aws)
	db.session.commit()


def get_zabbix_server_ip():
	config = StringIO.StringIO()
	config.write('[dummysection]\n')
	config.write(open('/etc/zabbix/zabbix_agentd.conf').read())
	config.seek(0, os.SEEK_SET)
	cp = ConfigParser.ConfigParser()
	cp.readfp(config)
	Hostname = cp.get('dummysection', 'Hostname')
	config.close()
	return Hostname

## idt should be exist ##
def init_aws_itemtype(dimension,idt,hostid,additembyapi,area):

	zabbix = zabbix_api()

	if not dimension.has_key('ServiceName') and not dimension.has_key('LinkedAccount'):
		itname = 'All'
		itkey = 'All'
		awsname = 'By All'
	elif dimension.has_key('ServiceName') and dimension.has_key('LinkedAccount'):
		itname = dimension['ServiceName'][0] + ' ' + dimension['LinkedAccount'][0]
		itkey = dimension['ServiceName'][0] + '_' + dimension['LinkedAccount'][0]
		awsname='By ServiceName and LinkedAccount'
	elif dimension.has_key('ServiceName'):
		itname = dimension['ServiceName'][0]
		itkey = itname
		awsname='By ServiceName'
	else:
		itname = dimension['LinkedAccount'][0]
		itkey = itname
		awsname='By LinkedAccount'

	aws = Aws.query.filter_by(awsname=awsname).first()
	if aws == None:
		aws = Aws(awsname=awsname,area=area)
		db.session.add(aws)

	it_tmp = Itemtype.query.filter_by(itemtypename=itname).first()
	if it_tmp == None:
		it_tmp = Itemtype(itemtypename=itname,itemkey=itkey,aws=aws,itemdatatype=idt,itemunit='USD',zabbixvaluetype=NUMERIC_FLOAT)
		db.session.add(it_tmp)
	
	itkey = area.areaname + '_' + itkey
	itemid = None

	session = loadSession()
	chechi = session.query(Zabbixitems).filter_by(hostid=hostid,key_=itkey).first()
	session.close()
	create_results = None
	if chechi == None:
		create_results = zabbix.item_create(itkey,hostid)
	if create_results != None:
		print 'create_results',create_results
		itemid = create_results
		additembyapi.append(itemid) 

	if itemid == None:
		return
	
	
	itmp = Item.query.filter_by(itemname=itkey).first()
	if itmp == None:
		ni = Item(itemid,itkey,None,it_tmp)
		db.session.add(ni)
		t = ni.set_belong_to_area(area)
		if t != None:
			db.session.add(t)

	db.session.commit()



def init_aws_item():
	
	host_name = get_zabbix_server_ip()

	zabbix = zabbix_api()
	
	additembyapi = []
	addhostbyapi = []

	init_aws()

	session = loadSession()
	tmphost = session.query(Zabbixhosts).filter_by(name=host_name).first()
	session.close()
	hostid = None
	if tmphost != None:
		hostid = tmphost.hostid
	if hostid == None:
		host_group_name = ['AWS servers']
		template_name = []
		hostid = zabbix.host_create(host_name,host_name,host_group_name,template_name)
		addhostbyapi.append(hostid)
	try:
		print "hostid",hostid
		rs = boto.ec2.cloudwatch.regions()
		idt = Itemdatatype.query.filter_by(itemdatatypename='AWS fee data').first()
		print "idt",idt
		if idt == None:
			idt = Itemdatatype(itemdatatypename='AWS fee data')
			db.session.add(idt)
		for r in rs:

			a = Area.query.filter_by(areaname=r.name).first()
			print r.name
			if a == None:
				a = Area(areaname=r.name)
				db.session.add(a)
			
			con = boto.ec2.cloudwatch.connect_to_region(r.name)
			lms = con.list_metrics(None,None,metric_name="EstimatedCharges",namespace="AWS/Billing")
			for lm in lms:
				init_aws_itemtype(lm.dimensions,idt,hostid,additembyapi,a)
		db.session.commit()
	except Exception, e:
		print "Exception in user code:"
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
		# zabbix.item_delete(additembyapi)
		# zabbix.host_delete(addhostbyapi)
		# db.session.rollback()

################################           add aws            ####################################


def init_area():
	regions = boto.ec2.regions()

	for r in regions:
		a = Area.query.filter_by(areaname=r.name).first()
		if a == None:
			a = Area(areaname=r.name)
			db.session.add(a)
	db.session.commit()

def init_service():

	names = ['NAT','Web_App','Relay','Control','Database']

	for n in names:
		s = Service.query.filter_by(servicename=n).first()
		if s == None:
			tmp = Service(servicename=n)
			db.session.add(tmp)

	db.session.commit()

def init_itemdatatype():

	names = ["Application data","CPU data","Memory data","Connections","AWS fee data","Counting","Other"]

	for n in names:
		i = Itemdatatype.query.filter_by(itemdatatypename=n).first()
		if i == None:
			tmp = Itemdatatype(itemdatatypename=n)
			db.session.add(tmp)

	db.session.commit()

def init_normalitemtype():
	count = Normalitemtype.query.count()
	if count == 0:
		nit = Normalitemtype()
		db.session.add(nit)
	elif count > 1:
		db.session.query(Normalitemtype).delete()
		nit = Normalitemtype()
		db.session.add(nit)
	db.session.commit()

def init_zbxitemtype():
	count = Zbxitemtype.query.count()
	if count == 0:
		zit = Zbxitemtype()
		db.session.add(zit)
	elif count > 1:
		db.session.query(Zbxitemtype).delete()
		zit = Zbxitemtype()
		db.session.add(zit)
	db.session.commit() 

def init_itemtype():

	idtnames = ["Application data","CPU data","Memory data","Connections","AWS fee data","Counting","Other"]
	idt = []
	for n in idtnames:
		i = Itemdatatype.query.filter_by(itemdatatypename=n).first()
		if i == None:
			tmp = Itemdatatype(itemdatatypename=n)
			db.session.add(tmp)
			idt.append(tmp)
		else:
			idt.append(i)

	servicenames = ['NAT','Web_App','Relay','Control','Database']
	svs = []
	for sn in servicenames:
		stmp = Service.query.filter_by(servicename=sn).first()
		if stmp == None:
			stmp = Service(servicename=sn)
			db.session.add(stmp)
		svs.append(stmp)

	nit = Normalitemtype.query.first()
	if nit == None:
		init_normalitemtype()
		nit = Normalitemtype.query.first()

	zit = Zbxitemtype.query.first()
	if zit == None:
		init_zbxitemtype()
		zit = Zbxitemtype.query.first()


	# for x in xrange(1,35):

	normalitems = {'InstanceType':[idt[5],None,TEXT],'Count':[idt[5],'Counts',NUMERIC_UNSIGNED],'ELB':[idt[6],None,TEXT],'LVS':[idt[6],None,TEXT]}

	serviceitems ={'PV':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[1]],'UV':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[1]], \
				'OnlineDevice':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[3]],'Throughput':[idt[0],'Byte',NUMERIC_FLOAT,svs[2]], \
				'POSTGET':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[2]],'Sum[Success:Failed]':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[0]],\
				'NATTypes':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[0]],'IOPS':[idt[0],'Counts',NUMERIC_UNSIGNED,svs[4]]}

	zabbixitems = { 'system.cpu.intr': ['Interrupts per second' ,idt[1],'Counts'],\
				'system.cpu.load[percpu,avg15]':['Processor load (15 min average per core)',idt[1],'Process Counts'],\
				'system.cpu.load[percpu,avg1]':['Processor load (1 min average per core)',idt[1],'Process Counts'],\
				'system.cpu.load[percpu,avg5]':['Processor load (5 min average per core)',idt[1],'Process Counts'],\
				'system.cpu.switches':['Context switches per second',idt[1],'Counts'],\
				'system.cpu.util[,idle]':['CPU idle time',idt[1],'Percent'],\
				'system.cpu.util[,interrupt]':['CPU interrupt time',idt[1],'Percent'],\
				'system.cpu.util[,iowait]':['CPU iowait time',idt[1],'Percent'],\
				'system.cpu.util[,nice]':['CPU nice time',idt[1],'Percent'],\
				'system.cpu.util[,softirq]':['CPU softirq time',idt[1],'Percent'],\
				'system.cpu.util[,steal]':['CPU steal time',idt[1],'Percent'],\
				'system.cpu.util[,system]':['CPU system time',idt[1],'Percent'],\
				'system.cpu.util[,user]':['CPU user time',idt[1],'Percent'],\
				'system.swap.size[,free]':['Free swap space',idt[2],'Byte'],\
				'system.swap.size[,pfree]':['Free swap space in %',idt[2],'Byte'],\
				'system.swap.size[,total]':['Total swap space',idt[2],'Byte'],\
				'vm.memory.size[available]':['Available memory',idt[2],'Byte'],\
				'vm.memory.size[total]':['Total memory',idt[2],'Byte']}

	for ni in normalitems:
		nitmp = Itemtype.query.filter_by(itemtypename=ni).first()
		if nitmp == None:
			nitmp = Itemtype(ni,ni,None,normalitems[ni][0],normalitems[ni][1],normalitems[ni][2])
			nitmp.nit = nit
		else:
			nitmp.itemtypename = ni
			nitmp.itemkey = ni
			nitmp.aws = None
			nitmp.itemdatatype = normalitems[ni][0]
			nitmp.itemunit = normalitems[ni][1]
			nitmp.zabbixvaluetype = normalitems[ni][2]
			nitmp.nit = nit
		db.session.add(nitmp)

	for si in serviceitems:
		sitmp = Itemtype.query.filter_by(itemtypename=si).first()
		if sitmp == None:
			sitmp = Itemtype(si,si,None,serviceitems[si][0],serviceitems[si][1],serviceitems[si][2])
			db.session.add(sitmp)
		else:
			sitmp.itemtypename = si
			sitmp.itemkey = si
			sitmp.aws = None
			sitmp.itemdatatype = serviceitems[si][0]
			sitmp.itemunit = serviceitems[si][1]
			sitmp.zabbixvaluetype = serviceitems[si][2]
			db.session.add(sitmp)

		addittmp = serviceitems[si][3].add_itemtype(sitmp)
		if addittmp != None:
			db.session.add(addittmp)

	for zi in zabbixitems:
		zitmp = Itemtype.query.filter_by(itemtypename=zabbixitems[zi][0]).first()
		if zitmp == None:
			zitmp = Itemtype(zabbixitems[zi][0],zi,None,zabbixitems[zi][1],zabbixitems[zi][2])
			zitmp.zit = zit
		else:
			zitmp.itemtypename = zabbixitems[zi][0]
			zitmp.itemkey = zi
			zitmp.aws = None
			zitmp.itemdatatype = zabbixitems[zi][1]
			zitmp.itemunit = zabbixitems[zi][2]
			zitmp.zit = zit
		db.session.add(zitmp)

	db.session.commit()

# preconditions : service exists, area exists, zabbixitemtype exists, normal itemtype exists, service itemtype exists 
#       
# def add_host(hostname, servicename,host_ip,areaname):

# 	zabbix = zabbix_api()

# 	print '.'*6 , " Checking for preconditions " , '.'*6
# 	area = Area.query.filter_by(areaname=areaname).first()
# 	if area == None:
# 		print " area ", areaname ," is not exists .."
# 		return None

# 	itemnamelist=['PV','UV','InstanceType',\
# 				'Count','ELB','LVS','OnlineDevice','Throughput','POSTGET','Sum[Success:Failed]',\
# 				'NATTypes','IOPS']

# 	zabbixitems = { 'system.cpu.intr': 'Interrupts per second' ,\
# 				'system.cpu.load[percpu,avg15]':'Processor load (15 min average per core)',\
# 				'system.cpu.load[percpu,avg1]':'Processor load (1 min average per core)',\
# 				'system.cpu.load[percpu,avg5]':'Processor load (5 min average per core)',\
# 				'system.cpu.switches':'Context switches per second',\
# 				'system.cpu.util[,idle]':'CPU idle time',\
# 				'system.cpu.util[,interrupt]':'CPU interrupt time',\
# 				'system.cpu.util[,iowait]':'CPU iowait time',\
# 				'system.cpu.util[,nice]':'CPU nice time',\
# 				'system.cpu.util[,softirq]':'CPU softirq time',\
# 				'system.cpu.util[,steal]':'CPU steal time',\
# 				'system.cpu.util[,system]':'CPU system time',\
# 				'system.cpu.util[,user]':'CPU user time',\
# 				'system.swap.size[,free]':'Free swap space',\
# 				'system.swap.size[,pfree]':'Free swap space in %',\
# 				'system.swap.size[,total]':'Total swap space',\
# 				'vm.memory.size[available]':'Available memory',\
# 				'vm.memory.size[total]':'Total memory'} 

# 	normalitems = itemnamelist[2:6]

# 	service_item_map = {'NAT':['Sum[Success:Failed]','NATTypes'],\
# 						'Web_App':['PV','UV'],\
# 						'Relay':['Throughput','POSTGET'],\
# 						'Control':['OnlineDevice'],\
# 						'Database':['IOPS']}

# 	for t in itemnamelist:
# 		test = Itemtype.query.filter_by(itemtypename=t).first()
# 		if test == None:
# 			print " itemtype is not exist ", t
# 			return None

# 	for t in zabbixitems:
# 		test = Itemtype.query.filter_by(itemtypename=zabbixitems[t]).first()
# 		if test == None:
# 			print " itemtype is not exist ", zabbixitems[t]
# 			return None

# 	service = Service.query.filter_by(servicename=servicename).first()
# 	if service == None:
# 		return None

# 	host_group_name = [HOST_GROUP_NAME]
# 	template_name = [TEMPLATE_NAME] 
				
# 	print "processing host: %s in service: %s ..." %  (hostname,servicename)

# 	#create host via zabbix api
# 	print "creating host via zabbix_api..."
# 	hostid = zabbix.host_create(host_ip,host_ip,host_group_name,template_name)
# 	if hostid == None:
# 		print " add or get host via api error " , host_ip
# 		return None

# 	#create host in monitor database
# 	h1 = Host.query.filter_by(hostid = hostid).first()
# 	if h1 == None:
# 		h1 = Host(hostid,hostname,area,service)
# 		db.session.add(h1)

# 	# update the relationship between area and service
# 	t = h1.area.add_service(h1.service)
# 	if t != None:
# 		db.session.add(t)

# 	# add template item into monitor database
# 	print "add template item into monitor database..."
# 	session = loadSession()
# 	for key in zabbixitems:
# 		zi = session.query(Zabbixitems).filter_by(key_=key,hostid=hostid).first()
# 		it = Itemtype.query.filter_by(itemkey=key).first()
# 		ni = Item.query.filter_by(itemid = zi.itemid).first()
# 		if ni == None:
# 			ni = Item(zi.itemid,it.itemtypename,h1,it)
# 			db.session.add(ni)
# 	session.close()

# 	# add service item into monitor database
# 	print "add service item into monitor database..."
# 	additemtypes = service_item_map.get(servicename,None)
# 	for key in additemtypes:
# 		itemid = zabbix.item_create(key,hostid)
# 		print key
# 		it = Itemtype.query.filter_by(itemkey=key).first()
# 		ni = Item.query.filter_by(itemid = itemid).first()
# 		if ni == None:
# 			ni = Item(itemid,it.itemtypename,h1,it)
# 			db.session.add(ni)

# 	# add normal item into monitor database
# 	print "add normal item into monitor database..."
# 	for key in normalitems:
# 		itemid = zabbix.item_create(key,hostid)
# 		if itemid == None:
# 			print " add or get itemid failed ", host_ip, key
# 		it = Itemtype.query.filter_by(itemkey=key).first()
# 		ni = Item.query.filter_by(itemid = itemid).first()
# 		if ni == None:
# 			ni = Item(itemid,it.itemtypename,h1,it)
# 			db.session.add(ni)

# 	db.session.commit()

# 	print "host: %s in service: %s add items complete!" %  (hostname,servicename)

# 	return hostid


def mass_add_host_item_for_area(areaname):

	con = boto.ec2.connect_to_region(areaname)
	reservations = con.get_all_instances()
	for res in reservations:
		for inst in res.instances:
			if 'ServiceType' in inst.tags: #zabbix server does not have servicetype 

				hostname = inst.tags['Name']
				servicename = inst.tags['ServiceType']
				host_ip = inst.private_ip_address
				if host_ip == None:
					continue
				
				hostid = add_update_host(hostname, servicename,host_ip,areaname)
				if hostid == None:
					print " add host item failed ", host_ip
				else:
					print " add host item Success ", host_ip


if __name__ == '__main__':

	u = User.query.filter_by(username='root').first()
	if u == None:
		u = User('root','root',0,1,'root@localhost')
		db.session.add(u)
		db.session.commit()

	print 'process aws'
	init_aws_item()
	print 'process area'
	init_area()
	print 'process service'
	init_service()
	print 'process itemdatatype'
	init_itemdatatype()
	print 'process normalitemtype'
	init_normalitemtype()
	print 'process zbxitemtype'
	init_zbxitemtype()
	print 'process itemtype'
	init_itemtype()
	print 'process host item'
	mass_add_host_item_for_area('ap-southeast-1')




