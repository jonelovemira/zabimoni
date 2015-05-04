#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config

from monitor.item.models import Host
from monitor.item.functions import delete_host
from monitor.zabbix.zabbix_api import zabbix_api

from monitor.zabbix.models import Zabbixinterface,loadSession
from monitor import db
import sys,traceback,time
from datetime import datetime
from monitor.functions import get_zabbix_server_ip,log_for_callback_command
# import boto.ec2
# from monitor.item.functions import add_update_host
from config import REMOTE_COMMAND_LOG
import getopt

def unreach_action(host_ip):
	print host_ip
	return 

def usage():
	print("Usage:%s [-i|-h] [--help|--instanceip] args ...." % sys.argv[0])

if __name__ == '__main__':
# 	zabbix = zabbix_api()
	session = loadSession()

	log_for_callback_command(sys.argv)

	try:
		opts,args = getopt.getopt(sys.argv[1:], "i:", ["help","instanceip="])
		for opt,arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit(1)
			elif opt in ("-i", "--instanceip"):
				instanceip = arg
			else:
				usage()
				sys.exit(1)
		for arg in args:
			print "non-option ARGV-elements: %s" % arg
	except getopt.GetoptError, exc:
		print "%s" % exc.msg
		usage()
		sys.exit(1)

	unreach_action(instanceip)
	# try:
		
	# 	time_format = '%Y-%m-%d %H:%M:%S %Z'
	# 	current_time = time.strftime(time_format,time.gmtime(time.time()))

	# 	output = open(REMOTE_COMMAND_LOG,'a')
	# 	output.write( '\n' + current_time + ' ')

	# 	for a in sys.argv:
	# 		output.write(a + ' ')

	# 	output.close()


	# 	# host_ip = sys.argv[1]

	# 	# server_ip = get_zabbix_server_ip()

	# 	# if host_ip == server_ip:
	# 	# 	exit(0)

	# 	# i = session.query(Zabbixinterface).filter_by(ip=host_ip).first()

	# 	# if i == None:
	# 	# 	exit(0)
	# 	# hostid = i.hostid
		
	# 	# host = Host.query.filter_by(hostid=hostid).first()
	# 	# if host == None:
	# 	# 	raise MonitorException('host to be delete does not exists')
	# 	# hostid = host.hostid
	# 	# items = host.items
	# 	# for i in items:
	# 	# 	db.session.delete(i)
	# 	# db.session.delete(host)
	# 	# zabbix = zabbix_api()
	# 	# # zabbix.host_delete([hostid]) 

	# 	# db.session.commit()
	# except Exception, e:
	# 	# zabbix.rollback()
	# 	db.session.rollback()
	# 	raise Exception('error',str(e))
	# finally:
	# 	session.close()
	# 	db.session.remove()

