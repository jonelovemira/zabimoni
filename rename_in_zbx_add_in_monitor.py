#! /home/jone/flask_project/monitor-0.3.7/flask/bin/python

from monitor.item.models import Host,Service
from monitor.zabbix_api import zabbix_api,get_zabbix_server_ip
from monitor.zabbix import loadSession,Zabbixinterface
from monitor import db
import sys,traceback
from datetime import datetime
import boto.ec2
from monitor.item.functions import add_update_host

if __name__ == '__main__':
	zabbix = zabbix_api()
	try:
		content = 'new content'
		if len(sys.argv) > 1:
			content = 	sys.argv[1]
		today = datetime.today()
		output = open('/home/jone/flask_project/monitor-0.3.7/remote_command','a')
		output.write('\n')
		output.write(str(today))
		output.write(' ' + 'auto registration' + ' ')
		output.write(' ' + content)
		output.close()

		# update name in zabbix
		host_ip = sys.argv[1]
		# dnsname = sys.argv[2]
		# areaname = dnsname.split('.')[1]
		server_ip = get_zabbix_server_ip()
		areaname = Host.query.filter_by(hostname=server_ip).first().area.areaname

		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(ip=host_ip).first()
		session.close()

		if i == None:
			exit(0)
		hostid = i.hostid
		
		hostid = zabbix.host_update(hostid,hostname=host_ip,host_ip=host_ip)
		# add host in monitor database
		nametag = None
		servicename = None


		try:
			con = boto.ec2.connect_to_region(areaname)
			res = con.get_all_instances(filters={'private_ip_address':host_ip})
			nametag = res[0].instances[0].tags['Name']
			servicename = nametag
		except Exception, e:
			nametag = host_ip
			servicename = "nat"

		tmps = Service.query.filter_by(servicename=servicename).first()
		if tmps == None:
			tmps = Service(servicename=servicename)
			db.session.add(tmps)

		if Host.query.filter_by(hostname=nametag).count() > 0:
			exit(0)
		
		print "add update host"
		add_update_host(nametag, servicename,host_ip,areaname)

		db.session.commit()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		zabbix.rollback()
		db.session.rollback()
		raise Exception('error',str(e))
	finally:
		db.session.remove()

	
	# rename
