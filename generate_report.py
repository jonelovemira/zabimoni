#! /usr/bin/python


import urllib,sys

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


if __name__ == '__main__':
	esid = sys.argv[1]
	port = 5000
	protocol = 'http://'
	route = '/chart/report/generate'
	url = protocol +  get_zabbix_server_ip() + ':' + str(port) + route + '/' + esid
	print url
	data = urllib.urlopen(url).read()
	#print os.getcwd()
