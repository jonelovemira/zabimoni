#! /home/monitor/project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Host,Service
from monitor.zabbix_api import zabbix_api
from monitor.zabbix import loadSession,Zabbixinterface
from monitor import db
import sys
import boto.ec2
from monitor.item.functions import add_update_host

if __name__ == '__main__':
	try:
		# test if can execute
		#content = 'new content'
		#if len(sys.argv) > 1:
		#	content = 	sys.argv[1]
		#output = open('/home/monitor/project/monitor-0.3.7/new.cron','w')
		#output.write(content)
		#output.close()

		# update name in zabbix
		host_ip = sys.argv[1]
		dnsname = sys.argv[2]
		areaname = dnsname.split('.')[1]
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(ip=host_ip).first()
		session.close()
		hostid = i.hostid
		zabbix = zabbix_api()
		hostid = zabbix.host_update(hostid,hostname=host_ip,host_ip=host_ip)
		
		# add host in monitor database
		con = boto.ec2.connect_to_region(areaname)
		res = con.get_all_instances(filters={'private_ip_address':host_ip})
		nametag = res[0].instances[0].tags['Name']
		servicename = nametag.split('-')[0]
		tmps = Service.query.filter_by(servicename=servicename).first()
		if tmps == None:
			tmps = Service(servicename=servicename)
			db.session.add(tmps)
		add_update_host(nametag, servicename,host_ip,areaname)

	except Exception, e:
		db.session.rollback()
		raise Exception('error',str(e))
	else:
		db.session.commit()
	finally:
		db.session.remove()

	
	# rename
