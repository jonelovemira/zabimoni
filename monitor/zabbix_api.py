#! flask/bin/python

import json
import urllib2
from urllib2 import URLError
import sys
from zabbix import Zabbixhosts,Zabbixitems,Zabbixhostgroup,loadSession,Zabbixinterface
from MonitorException import *

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

class zabbix_api:
	
	#### server_ip shuould be valid for zabbix_api ###
	def __init__(self): 
		server_ip = get_zabbix_server_ip()
		self.url = 'http://' + server_ip + '/zabbix/api_jsonrpc.php' 
		self.header = {"Content-Type":"application/json"}         
	     
	#### get user login the zabbix api id ####
	#### important for every call of      ####
	#### method in this class             ####   
	def user_login(self): 
	    data = json.dumps({ 
	                       "jsonrpc": "2.0", 
	                       "method": "user.login", 
	                       "params": { 
	                                  "user": "admin",
	                                  "password": "zabbix" 
	                                  }, 
	                       "id": 0 
	                       }) 
	     
	    request = urllib2.Request(self.url, data) 
	    for key in self.header: 
	        request.add_header(key, self.header[key]) 
	    try: 
	        result = urllib2.urlopen(request) 
	    except URLError as e:
	    	# return 
	        raise  MonitorException('can not login the zabbix api due to urlerror')
	    else: 
	        response = json.loads(result.read()) 
	        result.close()
	        if response.has_key('result'):
	         	self.authID = response['result']
	         	return self.authID 
	        else:
	        	# return
	        	raise  MonitorException('can not login the zabbix api: ' + str(response))
	

	####   create a host via zabbix api                 #####
	####   attention: hostgroup_name cannot be empty    #####
	def host_create(self, host_name , host_ip , hostgroup_name, template_name): 
		session = loadSession()
 		if len(hostgroup_name) == 0:
 			raise MonitorException('host group cannot be null')

		group_list=[]
		template_list=[]

		for hostgroup in hostgroup_name:
			if session.query(Zabbixhostgroup).filter_by(name = hostgroup).count() > 0:
				var = {}
				var['groupid'] = session.query(Zabbixhostgroup).filter_by(name = hostgroup).first().groupid
				group_list.append(var)
				# print "yes"
			else:
				raise MonitorException('Group not found ' + hostgroup)

		for template in template_name:
			if session.query(Zabbixhosts).filter_by(name = template).count() > 0:
				var = {}
				t = session.query(Zabbixhosts).filter_by(name = template).first()
				var['templateid'] = t.hostid
				template_list.append(var)
			else:
				raise MonitorException('Template not found ' + template)

		data = json.dumps({ 
	                       "jsonrpc":"2.0", 
	                       "method":"host.create", 
	                       "params":{ 
	                                 "host": host_name, 
	                                 "interfaces": [ 
	                                 { 
	                                 "type": 1, 
	                                 "main": 1, 
	                                 "useip": 1, 
	                                 "ip": host_ip, 
	                                 "dns": "", 
	                                 "port": "10050" 
	                                  } 
	                                 ], 
	                               "groups": group_list,
	                               "templates": template_list,
	                                 }, 
	                       "auth": self.user_login(), 
	                       "id":1                   
	    }) 
		
		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key]) 
		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			raise MonitorException('can not create host due to urlerror')
		else:
			response = json.loads(result.read())
			result.close()
			if response.has_key('result'):
				return response['result']['hostids'][0]
			else:
				raise MonitorException('can not create host ,response ' + str(response))
		finally:
			session.close()

	def host_update(self,hostid,hostname=None,host_ip=None):
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(hostid=hostid).first()
		h = session.query(Zabbixhosts).filter_by(hostid=hostid).first()
		tmp_hostname = h.name
		tmp_host_ip = i.ip
		session.close()

		if hostname == None:
			hostname = tmp_hostname

		if host_ip == None:
			host_ip = tmp_host_ip

		


		data = json.dumps({ 
			"jsonrpc":"2.0", \
			"method":"host.update", 
			"params":{
				"hostid": hostid ,
				"host": hostname,
				"name":hostname
			}, 
			"auth": self.user_login(), 
			"id":1
		})
		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key]) 
		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			raise MonitorException('cannot update host')
		else:
			response = json.loads(result.read())
			result.close()
			if response.has_key('result'):
				return response['result']['hostids'][0]
			else:
				raise MonitorException('cannot update host due to ' + str(response))



	# def host_delete(self,hostid):
	# 	session = loadSession()
	# 	h = session.query(Zabbixhosts).filter_by(hostid=hostid).first()
	# 	if h == None:
	# 		return False

	# ####   We can read host info via sqlalchemy class mapper ####
	# def get_hostid_by_name(self,host_name):
	# 	session = loadSession()
	# 	h = session.query(Zabbixhosts).filter_by(name=host_name).first()
	# 	session.close()
	# 	if h == None:
	# 		return None
	# 	return h.hostid


	def item_create(self,item_name,host_id,host_ip=None,interface_id=None,item_type=2,value_type=0):
		session = loadSession()
		# if session.query(Zabbixhosts).filter_by(hostid = host_id).count()>0:
		# 	itmp = session.query(Zabbixitems).filter_by(key_=item_name,hostid=host_id).first()
		# 	if itmp != None:
		# 		return itmp.itemid
		i = session.query(Zabbixinterface).filter_by(hostid=host_id).first()
		interface_id = i.interfaceid
		host_ip = i.ip
		session.close()
		# 	# print interface_id
		# else:
		# 	raise ZabbixAPICreateItemError('host can not found' + str(host_id))

		data = json.dumps({
			"jsonrpc":"2.0",
			"method":"item.create",
			"params":{
				"name":item_name,
				"key_":item_name,
				"hostid": str(host_id),
				"type":item_type,
				"value_type":value_type,
				"interfaceid":interface_id,
				"trapper_hosts":host_ip
			},
			"auth":self.user_login(),
			"id":1
		})

		request = urllib2.Request(self.url, data)

		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			raise MonitorException('cannot create item ')
		else: 
			response = json.loads(result.read()) 
			result.close()
			if response.has_key('result'):
				return response['result']['itemids'][0]
			else:
				# print response
				raise MonitorException('item can not create ,' + str(response))
		# finally:
		# 	session.close()
			#return response['result']

	def item_update(self,itemid,item_name,item_type=2,value_type=0):
		data = json.dumps({
			"jsonrpc":"2.0",
			"method":"item.update",
			"params":{
				"itemid":str(itemid),
				"name":item_name,
				"key_":item_name,
				"type":item_type,
				"value_type":value_type
			},
			"auth":self.user_login(),
			"id":1
		})
		request = urllib2.Request(self.url, data)

		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			raise MonitorException('cannot update item')
		else: 
			response = json.loads(result.read()) 
			result.close()
			if response.has_key('result'):
				return response['result']['itemids'][0]
			else:
				raise MonitorException('item can not update ,' + str(response))

	def item_delete(self,itemid):
		di = [itemid]
		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"item.delete",
					"params":di,
					"auth":self.user_login(),
					"id":1
		})

		request = urllib2.Request(self.url, data)

		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			raise MonitorException('can not delete item')
		else: 
			response = json.loads(result.read()) 
			result.close()
			if response.has_key('result'):
				return response['result']
			else:
				raise MonitorException('item can not delete ,' + str(response))

	def host_delete(self,hosts):
		session = loadSession()
		dh = []
		for i in hosts:
			host = session.query(Zabbixhosts).filter_by(hostid=i).first()
			if host != None:
				dh.append(i)
		if len(dh) == 0:
			return None
		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"host.delete",
					"params":dh,
					"auth":self.user_login(),
					"id":1
		})

		request = urllib2.Request(self.url, data)

		for key in self.header: 
			request.add_header(key, self.header[key]) 
	          
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			raise MonitorException('host can not delete due to url error')
		else: 
			response = json.loads(result.read()) 
			result.close()
			if response.has_key('result'):
				return response['result']
			else:
				raise MonitorException('host can not delete ,' + str(response))
		finally:
			session.close()


if __name__ == '__main__':
	# zabbix = zabbix_api('192.168.221.130')
	# host_name = '192.168.221.130'
	# host_ip = host_name
	# # hostgroup_name = ['test']
	# # template_name = ['Template OS Linux']
	# print zabbix.host_create(host_name , host_ip , ['AWS servers'], [])['hostids'][0]
	# # print zabbix.item_delete([35572])
	# # print zabbix.host_delete([10415])
	# # print zabbix.get_host_interface('10260')[0]['interfaceid']
	zabbix = zabbix_api()
	zabbix.item_update(36631,'Count',item_type=2,value_type=4)




