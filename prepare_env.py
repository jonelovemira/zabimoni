#! flask/bin/python

from monitor.zabbix.zabbix_api import zabbix_api
import boto
from boto.ec2 import cloudwatch
from monitor import db
from monitor.auth.models import User

from monitor.item.models import Area,Service,Host,Item,Itemtype,Aws,Itemdatatype,Normalitemtype,Zbxitemtype
import boto.ec2

from monitor.zabbix.models import Zabbixitems,Zabbixhosts,loadSession

from monitor.item.functions import add_update_host

import os,StringIO,ConfigParser,traceback,sys

from config import AREA,SERVICE
from boto.exception import BotoServerError

from crontab import CronTab

from boto.s3.connection import S3Connection
from tempfile import NamedTemporaryFile
from config import S3_BUCKET_NAME,XML_EXPORT_PATH,NUMERIC_FLOAT ,CHARACTER ,LOG,NUMERIC_UNSIGNED ,TEXT,LOCAL_XML_EXPORT_PATH
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def init_aws_update_crontab(command,crontab_time):
	try:
		cron = CronTab()
		iter_cron = cron.find_command(command)
		res = next(iter_cron,None)
		if res is None:
			job = cron.new(command)
			job.setall(crontab_time)
			cron.write()
	except Exception, e:
		raise e
	


################################           add aws            ####################################
def init_aws():
	arr = ['By All','By ServiceName','By LinkedAccount','By ServiceName and LinkedAccount']

	try:
		for r in arr:
			aws = Aws.query.filter_by(awsname=r).first()
			if aws == None:
				aws = Aws(awsname=r,area=None)
				db.session.add(aws)
	except Exception, e:
		db.session.rollback()
		Exception('cannot init aws', str(e))
	else:
		db.session.commit()
	finally:
		db.session.remove()


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
def init_aws_itemtype(dimension,idt,hostid,area,zabbix):

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
		else:
			create_results = chechi.itemid

		if create_results != None:
			print 'create_results',create_results
			itemid = create_results

		if itemid == None:
			return
		
		host = Host.query.filter_by(hostid=hostid).first()
		
		itmp = Item.query.filter_by(itemname=itkey).first()
		if itmp == None:
			ni = Item(itemid,itkey,host,it_tmp)
			db.session.add(ni)
			t = ni.set_belong_to_area(area)
			if t != None:
				db.session.add(t)


def init_aws_item():
	
	# add aws item in current host
	host_name = get_zabbix_server_ip()

	zabbix = zabbix_api()

	init_aws()

	# checkout if current host exists in zabbix database
	session = loadSession()
	tmphost = session.query(Zabbixhosts).filter_by(name=host_name).first()
	session.close()
	hostid = None
	
	try:
		# will create in zabbix if do not exist
		if tmphost != None:
			hostid = tmphost.hostid
		if hostid == None:
			pass
			#host_group_name = ['AWS servers']
			#template_name = ['Template OS Linux']
			#zabbix.host_create(host_name,host_name,host_group_name,template_name)
		print "hostid",hostid

		# get all regions for aws
		rs = boto.ec2.cloudwatch.regions()

		# get data type category and will create if do not exist
		idt = Itemdatatype.query.filter_by(itemdatatypename='AWS fee data').first()
		print "idt",idt
		if idt == None:
			idt = Itemdatatype(itemdatatypename='AWS fee data')
			db.session.add(idt)

		# get aws data for every area
		for r in rs:
			a = Area.query.filter_by(areaname=r.name).first()
			print r.name
			if a == None:
				a = Area(areaname=r.name)
				db.session.add(a)
			con = boto.ec2.cloudwatch.connect_to_region(r.name)
			lms = con.list_metrics(None,None,metric_name="EstimatedCharges",namespace="AWS/Billing")
			for lm in lms:
				init_aws_itemtype(lm.dimensions,idt,hostid,a,zabbix)
		db.session.commit()
	except BotoServerError, e:
		db.session.commit()
		pass
	except Exception, e:
		print "Exception in user code:"
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
		db.session.rollback()
		zabbix.rollback()		
	finally:
		db.session.remove()

################################           add aws            ####################################


def init_area():
	regions = boto.ec2.regions()

	for r in regions:
		a = Area.query.filter_by(areaname=r.name).first()
		if a == None:
			a = Area(areaname=r.name)
			db.session.add(a)
	db.session.commit()

def init_service(names=[]):

	if len(names) == 0:
		names = ['nat','web','relay','control','database','monitor']

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

def init_itemtype(it_keys=[]):

	if len(it_keys) == 0:
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

		servicenames = ['nat','web','relay','control','database']
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
	else:
		zit = Zbxitemtype.query.first()
		nit = Normalitemtype.query.first()
		for it in it_keys:
			ittmp = Itemtype.query.filter_by(itemtypename=it['itemtypename']).first()
			itemunit = None
			if it.has_key('itemunit'):
				itemunit = it['itemunit']
			zabbixvaluetype = None
			if it.has_key('zabbixvaluetype'):
				zabbixvaluetype = it['zabbixvaluetype']
			itemdatatype = Itemdatatype.query.filter_by(itemdatatypename=it['itemdatatypename']).first()
			function_type = 0
			if it['function_type'] != "None":
				function_type = int(it['function_type'])
			if ittmp == None:
				ittmp = Itemtype(it['itemtypename'],it['itemkey'],None,itemdatatype,itemunit,zabbixvaluetype,it['time_frequency'],function_type)
			else:
				ittmp.itemtypename = it['itemtypename']
				ittmp.itemkey = it['itemkey']
				ittmp.itemdatatype = itemdatatype
				ittmp.itemunit = itemunit
				ittmp.zabbixvaluetype =zabbixvaluetype
				ittmp.time_frequency = it['time_frequency']
				ittmp.function_type = function_type

			if len(it['services']) == 0:
				if zabbixvaluetype != None:
					ittmp.nit = nit
			else:
				for servicename in it['services']:
					s = Service.query.filter_by(servicename=servicename).first()
					stmp = s.add_itemtype(ittmp)
					if stmp != None:
						db.session.add(stmp)

			if zabbixvaluetype == None:
				ittmp.zit = zit

			db.session.add(ittmp)

		db.session.commit()

if __name__ == '__main__':

	# u = User.query.filter_by(username='root').first()
	# if u == None:
	# 	u = User('root','root',0,1,'root@localhost')
	# 	db.session.add(u)
	# 	db.session.commit()
	

	
	key = None
	try:
		con = S3Connection()
		bucket = con.get_bucket(S3_BUCKET_NAME)
		key = bucket.get_key(XML_EXPORT_PATH)
	except Exception, e:
		key = None

	tree = None
	if key == None:
		tree = ET.ElementTree(file=LOCAL_XML_EXPORT_PATH)
	else:
		print "get contents from s3"
		f = NamedTemporaryFile(delete=False)
		key.get_contents_to_filename(f.name)
		print f.name
		tree = ET.ElementTree(file=f.name)

	if tree == None:
		raise Exception('Cannot open xml config file')

	root = tree.getroot()
	services = root.findall('service')
	names = []
	for s in services:
		names.append(s.attrib['servicename'])

	itemtypes = root.findall('itemtype')
	it_keys = []
	for it in itemtypes:
		it_services = it.findall('itservice')
		it_s = []
		for i_s in it_services:
			it_s.append(i_s.attrib['servicename'])

		it.attrib['services'] = it_s
		it_keys.append(it.attrib)
	
	if key != None:
		os.unlink(f.name)
		
	print 'process area'
	init_area()
	print 'process service'
	init_service(names)

	print 'process host'
	zabbix = zabbix_api()
	try:
		session = loadSession()
		h = session.query(Zabbixhosts).filter_by(name=get_zabbix_server_ip()).first()
		session.close()
		if h == None:
			result = zabbix.host_create(get_zabbix_server_ip() , '127.0.0.1' , ['AWS servers'], [])
		else:
			result = h.hostid
	
		area = Area.query.filter_by(areaname=AREA).first()
		service = Service.query.filter_by(servicename=SERVICE).first()
		h = Host(result,get_zabbix_server_ip(),area,service)
		print "hostid",result
		db.session.add(h)
		db.session.commit()
	except Exception, e:
		db.session.rollback()
		zabbix.rollback()

	if os.environ.get('aws_cron_command') is None:
		aws_cron_command = os.path.abspath(os.path.dirname(__file__)) + '/aws_update.py'
	else:
		aws_cron_command = os.environ['aws_cron_command']

	if os.environ.get('aws_cron_time') is None:
		aws_cron_time = '0 */4 * * *'
	else:
		aws_cron_time = os.environ['aws_cron_time']

	init_aws_update_crontab(aws_cron_command,aws_cron_time)

	print 'process aws'
	init_aws_item()
	print 'process itemdatatype'
	init_itemdatatype()
	print 'process normalitemtype'
	init_normalitemtype()
	print 'process zbxitemtype'
	init_zbxitemtype()
	print 'process itemtype'
	init_itemtype(it_keys)



