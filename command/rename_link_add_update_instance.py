#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config


from monitor.item.models import Host,Service
from monitor.zabbix.zabbix_api import zabbix_api
from monitor.functions import get_zabbix_server_ip,log_for_callback_command
from monitor.zabbix.models import Zabbixinterface,loadSession,Zabbixhosts
from monitor import db
import sys,traceback,time
from datetime import datetime
import boto.ec2
from monitor.item.functions import add_update_host
from config import REMOTE_COMMAND_LOG,AREA,AREA_PROXY_SPLITER,ZABBIX_TEMPLATE_PREFIX,TEMPLATE_GROUP_SPLITER,NORMAL_TEMPLATE_NAME

import getopt

def rename_link_add_update(zabbix,host_ip):

	session = loadSession()
	server_ip = get_zabbix_server_ip()

	if host_ip == server_ip or host_ip == '127.0.0.1':
		exit(0)

	areaname = AREA

	zis = session.query(Zabbixinterface).filter_by(ip=host_ip).all()

	if len(zis) <= 0:
		exit(0)

	host_to_be_add = {}
	for i in zis:
		hostid = i.hostid
		if Host.query.get(hostid) is None:
			zh = session.query(Zabbixhosts).get(hostid)
			if zh != None:
				host_to_be_add[hostid] = {}
				host_to_be_add[hostid]['area'] = areaname
				host_to_be_add[hostid]['ip'] = i.ip
				proxy_hostid = zh.proxy_hostid
				if proxy_hostid != None:
					zph = session.query(Zabbixhosts).get(proxy_hostid)
					if zph != None:
						proxy_name = zph.name
						host_to_be_add[hostid]['area'] = proxy_name.split(AREA_PROXY_SPLITER)[0]

	nametag = None
	servicename = None

	for hid in host_to_be_add:
		try:
			con = boto.ec2.connect_to_region(host_to_be_add[hid]['area'])
			res = con.get_all_instances(filters={'private_ip_address':host_to_be_add[hid]['ip']})
			nametag = res[0].instances[0].tags['Name']
			servicename = nametag.split('-')[0]
			if session.query(Zabbixhosts).filter_by(host=ZABBIX_TEMPLATE_PREFIX + TEMPLATE_GROUP_SPLITER + servicename).count() <= 0:
				servicename = 'unknown'
		except Exception, e:
			nametag = host_to_be_add[hid]['ip']
			servicename = 'unknown'

		tmps = Service.query.filter_by(servicename=servicename).first()
		if tmps == None:
			tmps = Service(servicename=servicename)
			db.session.add(tmps)
			db.session.commit()

		host_to_be_add[hid]['nametag'] = nametag
		host_to_be_add[hid]['servicename'] = servicename

		added_template_name = [ZABBIX_TEMPLATE_PREFIX + TEMPLATE_GROUP_SPLITER + servicename, NORMAL_TEMPLATE_NAME]

		tmp_hostid = zabbix.host_update(hid,hostname=host_to_be_add[hid]['ip'],host_ip=host_to_be_add[hid]['ip'],added_template_name=added_template_name)

		add_update_host(host_to_be_add[hid]['nametag'], host_to_be_add[hid]['servicename'],host_to_be_add[hid]['ip'],host_to_be_add[hostid]['area'])

	
	session.close()

def usage():
	print("Usage:%s [-h|-i] [--help|--instanceip] args ...." % sys.argv[0])


if __name__ == '__main__':

	# WRITE LOG 
	log_for_callback_command(sys.argv)

	# get args
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


	zabbix = zabbix_api()
	try:
		rename_link_add_update(zabbix,instanceip)
		db.session.commit()

		# areaname = Host.query.filter_by(hostname=server_ip).first().area.areaname

		# i = session.query(Zabbixinterface).filter_by(ip=host_ip).first()

		# if i == None:
		# 	exit(0)
		# hostid = i.hostid
		
		# hostid = zabbix.host_update(hostid,hostname=host_ip,host_ip=host_ip)
		# # add host in monitor database
		# nametag = None
		# servicename = None


		# try:
		# 	con = boto.ec2.connect_to_region(areaname)
		# 	res = con.get_all_instances(filters={'private_ip_address':host_ip})
		# 	nametag = res[0].instances[0].tags['Name']
		# 	servicename = nametag.split('-')[0]
		# except Exception, e:
		# 	nametag = host_ip
		# 	servicename = "nat"

		# tmps = Service.query.filter_by(servicename=servicename).first()
		# if tmps == None:
		# 	tmps = Service(servicename=servicename)
		# 	db.session.add(tmps)
		# 	db.session.commit()

		
		# print "add update host"
		# add_update_host(nametag, servicename,host_ip,areaname)
		# session.close()
	except Exception, e:
		traceback.print_exc(file=sys.stdout)
		zabbix.rollback()
		db.session.rollback()
		raise Exception('error',str(e))
	finally:
		db.session.remove()

	
	# rename
