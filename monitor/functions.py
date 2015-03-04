
import os,StringIO,ConfigParser,string,random

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

def construct_random_str(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))