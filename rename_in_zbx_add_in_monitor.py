#! flask/bin/python

from monitor.item.models import Host
from monitor.zabbix_api import zabbix_api
from monitor.zabbix import loadSession,Zabbixinterface
from monitor import db
import sys

if __name__ == '__main__':
	try:
		host_ip = sys.argv[1]
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(ip=host_ip).first()
		session.close()
		hostid = i.hostid
		zabbix = zabbix_api()
		hostid = zabbix_api.host_update(hostid,hostname=host_ip,host_ip=host_ip)
	except Exception, e:
		raise Exception('error',str(e))

	
	# rename
