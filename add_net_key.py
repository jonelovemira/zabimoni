#! /home/monitor/project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Host,Item,Itemtype,Itemdatatype
from monitor.item.functions import update_host
from monitor.zabbix.zabbix_api import zabbix_api
from monitor.zabbix.models import Zabbixinterface,Zabbixitems,Zabbixfunctions, Zabbixtriggers,Zabbixhosts,loadSession
from monitor import db
import sys,traceback
import boto.ec2
from monitor.item.functions import add_update_host
from monitor.MonitorException import *
from datetime import datetime
from monitor.item.functions import add_key
from config import REMOTE_COMMAND_LOG
import time

if __name__ == '__main__':
	zabbix = zabbix_api()
	session = loadSession()
	try:

		time_format = '%Y-%m-%d %H:%M:%S %Z'
		current_time = time.strftime(time_format,time.gmtime(time.time()))

		output = open(REMOTE_COMMAND_LOG,'a')
		output.write( '\n' + current_time + ' ')

		for a in sys.argv:
			output.write(a + ' ')

		output.close()


		

		hostname = sys.argv[1]
		in_key = sys.argv[2]

		h1 = session.query(Zabbixhosts).filter_by(name=hostname).first()
		kinds = 4
		indexid = h1.hostid

		#disable the trigger
		ini = session.query(Zabbixitems).filter_by(hostid=indexid,key_=in_key).first()
		fres = session.query(Zabbixfunctions).filter_by(itemid=ini.itemid).all()

		for f in fres:
			t = session.query(Zabbixtriggers).filter_by(triggerid=f.triggerid).first()
			if t.expression == '{' + str(f.functionid) + '}>-1':
				# print t.triggerid
				zabbix.trigger_update(f.triggerid,1)

		#update key in monitor database
		itemdatatypename = 'Connections'
		it = Itemdatatype.query.filter_by(itemdatatypename=itemdatatypename).first()
		unitname = 'Bps'
		zabbixvaluetype = None
		# add_key(kinds,indexid,in_key,it.itemdatatypeid,unitname,zabbixvaluetype)
		add_key(kinds,indexid,in_key,it.itemdatatypeid,unitname,zabbixvaluetype,zabbix)

		out_key = in_key.replace('in','out')
		# add_key(kinds,indexid,out_key,it.itemdatatypeid,unitname,zabbixvaluetype)
		add_key(kinds,indexid,out_key,it.itemdatatypeid,unitname,zabbixvaluetype,zabbix)
		
		db.session.commit()
		session.close()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		db.session.rollback()
		zabbix.rollback()
		raise Exception('error',str(e))
	finally:
		db.session.remove()

	
	# rename
