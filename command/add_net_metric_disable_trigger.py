#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

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
# from config import REMOTE_COMMAND_LOG
from monitor.functions import log_for_callback_command
import time

import getopt


def add_net_metric(zabbix,hostname,in_key):
	session = loadSession()

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
	session.close()

def usage():
	print("Usage:%s [-i|-m|-h] [--help|--instanceip|--metricname] args ...." % sys.argv[0])


if __name__ == '__main__':

	# WRITE LOG 
	log_for_callback_command(sys.argv)

	# get args
	try:
		opts,args = getopt.getopt(sys.argv[1:], "i:m:", ["help","instanceip=","metricname="])
		for opt,arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit(1)
			elif opt in ("-i", "--instanceip"):
				instanceip = arg
			elif opt in ("-m","--metricname"):
				metricname = arg
			else:
				usage()
				sys.exit(1)
		for arg in args:
			print "non-option ARGV-elements: %s" % arg
	except getopt.GetoptError, exc:
		print "%s" % exc.msg
		usage()
		sys.exit(1)

	zabbix = zabbix_api()
	try:
		add_net_metric(zabbix,instanceip,metricname)
		db.session.commit()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		db.session.rollback()
		zabbix.rollback()
		raise Exception('error',str(e))
	finally:
		db.session.remove()

	
	# rename
