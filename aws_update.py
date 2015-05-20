#! /usr/bin/python
import boto
from boto.ec2 import cloudwatch
from datetime import datetime
import time
from zabbix_send import ZabbixSender
from datetime import timedelta

import os,StringIO,ConfigParser


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

def get_key(dimension):
	if not dimension.has_key('ServiceName') and not dimension.has_key('LinkedAccount'):
		itkey = 'All'
	elif dimension.has_key('ServiceName') and dimension.has_key('LinkedAccount'):
		itkey = dimension['ServiceName'][0] + '_' + dimension['LinkedAccount'][0]
	elif dimension.has_key('ServiceName'):
		itkey = dimension['ServiceName'][0]
	else:
		itkey = dimension['LinkedAccount'][0]
	return itkey

def send_update_data():

	server_ip = get_zabbix_server_ip()
	host = get_zabbix_server_ip()

	rs = boto.ec2.cloudwatch.regions()
	tmp = timedelta(hours=-4)
	end_time = datetime.utcnow()
	start_time = end_time + tmp
	for r in rs:
		try:
			print "--------------- " , r.name , " ---------------------"
			con = boto.ec2.cloudwatch.connect_to_region(region_name=r.name)
			lm = con.list_metrics(None,None,metric_name="EstimatedCharges",namespace="AWS/Billing")

			for l in lm:
				ms = con.get_metric_statistics(period = 14400,start_time=start_time,\
				end_time=end_time,metric_name="EstimatedCharges",namespace="AWS/Billing",\
				statistics="Maximum",dimensions=l.dimensions)

				key = r.name + '_' + get_key(l.dimensions)
				zs = ZabbixSender(server_ip)
				for ms_it in ms:
					t = ms_it['Timestamp']
					t_clock = time.mktime(t.timetuple())
					value = ms_it['Maximum']
					zs.AddData(host ,unicode(key), str(value),str(t_clock))
				res = zs.Send()
				print zs.send_data
				print res
				zs.ClearData()
				

		except Exception ,e:
			print e
			continue

if __name__ == '__main__':
	send_update_data()