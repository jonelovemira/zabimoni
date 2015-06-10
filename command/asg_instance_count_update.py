#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0, parentdir) 
import monitor, config, zabbix_send

import boto.ec2.autoscale
from config import AREA
from zabbix_send import ZabbixSender
from monitor.functions import get_zabbix_server_ip


group_metric_map = {
	'monitor': 'INTERNAL_ASG_MONITOR',
	'dbs': 'INTERNAL_ASG_DBS',
	'gdbs': 'INTERNAL_ASG_GDBS',
	'relay': 'INTERNAL_ASG_RELAY',
	'stun': 'INTERNAL_ASG_STUN',
	'control': 'INTERNAL_ASG_CONTROL',
	'web': 'INTERNAL_ASG_WEB',
	'cas': 'INTERNAL_ASG_CAS',
}

def send_update_data():

	try:
		server_ip = get_zabbix_server_ip()
		host_name = get_zabbix_server_ip()

		con = boto.ec2.autoscale.connect_to_region(AREA)
		autoscalegroups = con.get_all_groups()

		zs = ZabbixSender(server_ip)
		for asg in autoscalegroups:
			for key in group_metric_map:
				if key in asg.name:
					zs.AddData(host_name, unicode(group_metric_map[key]), str(asg.desired_capacity))
					break
		
		res = zs.Send()
		zs.ClearData()
	except Exception, e:
		import sys, traceback
		traceback.print_exc(file=sys.stdout)
				

if __name__ == '__main__':
	send_update_data()