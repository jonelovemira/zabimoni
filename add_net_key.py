#! /home/monitor/project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Host,Item,Itemtype,Itemdatatype
from monitor.item.functions import update_host
from monitor.zabbix_api import zabbix_api
from monitor.zabbix import loadSession,Zabbixinterface,Zabbixitems,Zabbixfunctions, Zabbixtriggers,Zabbixhosts
from monitor import db
import sys
import boto.ec2
from monitor.item.functions import add_update_host
from monitor.MonitorException import *

def add_it(o,key,itemdatatypeid,unitname,zabbixvaluetype):
	idt = Itemdatatype.query.filter_by(itemdatatypeid=itemdatatypeid).first()
	if idt == None:
		raise MonitorException('data type do not exists')
	it = Itemtype.query.filter_by(itemtypename=key).first()
	if it == None:
		it = Itemtype(key,key,None,idt,unitname,zabbixvaluetype)
		db.session.add(it)

	htmp = o.add_itemtype(it)
	if htmp != None:
		db.session.add(htmp)

def update_key_to_host(kinds,o):
	hosts = None
	if kinds == 1:
		hosts = Host.query.all()
	elif kinds == 4:
		hosts = [o]
	else:
		hosts = o.hosts.all()

	for h in hosts:
		update_host(h.hostid,h.hostname,h.area.areaid,h.service.serviceid)

def add_key(kinds,indexid,key,itemdatatypeid,unitname,zabbixvaluetype):
	kinds = int(kinds)
	if indexid == None:
		indexid = 1
	o = Host.query.filter_by(hostid=indexid).first()
	# print o
	add_it(o,key,itemdatatypeid,unitname,zabbixvaluetype)

	update_key_to_host(kinds,o)

if __name__ == '__main__':
	session = None
	zabbix = zabbix_api()
	try:
		# test if can execute
		# content = 'new content'
		# if len(sys.argv) > 1:
		# 	content = 	sys.argv[1]
		# output = open('/home/monitor/project/monitor-0.3.7/new.cron','w')
		# output.write(content)
		# output.close()
		hostname = sys.argv[1]
		session = loadSession()

		# interface1 = session.query(Zabbixinterface).filter_by(ip=hostip).first()
		h1 = session.query(Zabbixhosts).filter_by(name=hostname).first()
		kinds = 4
		indexid = h1.hostid

		#disable the trigger
		ini = session.query(Zabbixitems).filter_by(hostid=indexid,key_='net.if.in[eth0]').first()
		fres = session.query(Zabbixfunctions).filter_by(itemid=ini.itemid).all()

		for f in fres:
			t = session.query(Zabbixtriggers).filter_by(triggerid=f.triggerid).first()
			if t.expression == '{' + str(f.functionid) + '}>-1':
				# print t.triggerid
				zabbix.trigger_update(f.triggerid,1)

		#update key in monitor database
		key = 'net.if.in[eth0]'
		itemdatatypename = 'Connections'
		it = Itemdatatype.query.filter_by(itemdatatypename=itemdatatypename).first()
		unitname = 'Bps'
		zabbixvaluetype = None
		add_key(kinds,indexid,key,it.itemdatatypeid,unitname,zabbixvaluetype)

		key = 'net.if.out[eth0]'
		add_key(kinds,indexid,key,it.itemdatatypeid,unitname,zabbixvaluetype)
		

	except Exception, e:
		db.session.rollback()
		zabbix.rollback()
		raise Exception('error',str(e))
	else:
		db.session.commit()
	finally:
		session.close()
		db.session.remove()

	
	# rename
