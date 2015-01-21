import json
import urllib2
from urllib2 import URLError
import sys,traceback
from monitor.zabbix.models import Zabbixhosts,Zabbixitems,Zabbixhostgroup,Zabbixinterface,Zabbixtriggers,Zabbixactions,Zabbixdrules,loadSession
from monitor.MonitorException import *

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
	
	created_hosts = []
	created_items = []
	created_triggers = []
	created_actions = []

	created_hostgroups = []
	created_discovery_rules = []
	created_trigger_prototypes = []

	#### server_ip shuould be valid for zabbix_api ###
	def __init__(self): 
		server_ip = get_zabbix_server_ip()
		port = '5000'
		self.url = 'http://' + server_ip + ':' + port +  '/zabbix/api_jsonrpc.php' 
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
	    return self.request_api(data)

	
	#### generate create host json        ####
	def gen_host_create_json(self,host_name , host_ip , hostgroup_name, template_name):
 		if len(hostgroup_name) == 0:
 			raise MonitorException('host group cannot be null')

		group_list=[]
		template_list=[]
		session = loadSession()

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
				t = Zabbixhosts.query.filter_by(name = template).first()
				var['templateid'] = t.hostid
				template_list.append(var)
			else:
				raise MonitorException('Template not found ' + template)
		
		session.close()
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
				"templates": template_list
			},
			"auth": self.user_login(),
			"id":1
		})

		return data 

	####   create a host via zabbix api                 #####
	####   attention: hostgroup_name cannot be empty    #####
	def host_create(self, host_name , host_ip , hostgroup_name, template_name): 
		data = self.gen_host_create_json(host_name , host_ip , hostgroup_name, template_name)
		api_result = self.request_api(data)['hostids'][0]
		self.created_hosts.append(api_result)
		return api_result
			

	def host_update(self,hostid,hostname=None,host_ip=None):
		template_list=[]
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(hostid=hostid).first()
		h = session.query(Zabbixhosts).filter_by(hostid=hostid).first()
		tmp_hostname = h.name
		tmp_host_ip = i.ip
		template_name = ['Template OS Linux']
		for template in template_name:
			if session.query(Zabbixhosts).filter_by(name = template).count() > 0:
				var = {}
				t = session.query(Zabbixhosts).filter_by(name = template).first()
				var['templateid'] = t.hostid
				template_list.append(var)
			else:
				raise MonitorException('Template not found ' + template)
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
				"name":hostname,
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
			raise MonitorException('cannot update host')
		else:
			response = json.loads(result.read())
			result.close()
			if response.has_key('result'):
				return response['result']['hostids'][0]
			else:
				raise MonitorException('cannot update host due to ' + str(response))

	def gen_normal_item_json(self,item_name,host_id,host_ip=None,interface_id=None,item_type=2,value_type=0):
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(hostid=host_id).first()
		interface_id = i.interfaceid
		h = session.query(Zabbixhosts).filter_by(hostid=host_id).first()
		hostname = h.name
		session.close()
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
				"trapper_hosts":hostname
			},
			"auth":self.user_login(),
			"id":1
		})

		return data

	def gen_calc_item_json(self,item_name,host_id,formula,host_ip=None,interface_id=None,item_type=15,value_type=0):
		session = loadSession()
		i = session.query(Zabbixinterface).filter_by(hostid=host_id).first()
		interface_id = i.interfaceid
		host_ip = i.ip
		session.close()
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
				"trapper_hosts":host_ip,
				"params": formula,
				"delay":60
			},
			"auth":self.user_login(),
			"id":1
		})

		return data

	def request_api(self,data):

		# print data

		request = urllib2.Request(self.url, data)

		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			raise MonitorException('can not generate request')
		else: 
			response = json.loads(result.read()) 
			result.close()

			if response.has_key('result'):
				return response['result']
			else:
				raise MonitorException('request api fail,' + str(response))


	def item_create(self,item_name,host_id,host_ip=None,interface_id=None,item_type=2,value_type=0):
		data = self.gen_normal_item_json(item_name,host_id,host_ip,interface_id,item_type,value_type)
		api_result = self.request_api(data)['itemids'][0]
		self.created_items.append(api_result)
		return api_result

	def calc_item_create(self,item_name,host_id,formula,host_ip=None,interface_id=None,item_type=15,value_type=0):
		data = self.gen_calc_item_json(item_name,host_id,formula,host_ip,interface_id,item_type,value_type)
		api_result = self.request_api(data)['itemids'][0]
		self.created_items.append(api_result)
		return api_result

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

		api_result = self.request_api(data)['itemids'][0]

		return api_result

	def item_delete(self,itemids):
		# precheck if the item exist in zabbix
		session = loadSession()
		delete_itemids = []
		for itemid in itemids:
			if session.query(Zabbixitems).filter_by(itemid=itemid).count() > 0:
				delete_itemids.append(itemid)

		session.close()
		if len(delete_itemids) == 0:
			return None
		# di = [itemid]
		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"item.delete",
					"params":delete_itemids,
					"auth":self.user_login(),
					"id":1
		})
		api_result = self.request_api(data)
		return api_result

	def host_delete(self,hostids):
		delete_hostids = []
		session = loadSession()
		for i in hostids:
			host = session.query(Zabbixhosts).filter_by(hostid=i).first()
			if host != None:
				delete_hostids.append(i)
		session.close()
		if len(delete_hostids) == 0:
			return None
		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"host.delete",
					"params":delete_hostids,
					"auth":self.user_login(),
					"id":1
		})

		api_result = self.request_api(data)
		return api_result

	def trigger_create(self,expression,description):
		data = json.dumps({
				"jsonrpc":"2.0",
				"method":"trigger.create",
				"params": {
					"description": description,
					"expression": expression
				},
				"auth":self.user_login(),
				"id":1
		})
		api_result = self.request_api(data)['triggerids'][0]

		self.created_triggers.append(api_result)
		return api_result



	def trigger_update(self,triggerid,status):
		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"trigger.update",
					"params":{
						"triggerid":triggerid,
						"status":status
					},
					"auth":self.user_login(),
					"id":1
		})
		api_result = self.request_api(data)
		return api_result

	def trigger_delete(self,triggerids):
		delete_triggerids = []
		session = loadSession()
		for t in triggerids:
			if session.query(Zabbixtriggers).filter_by(triggerid=t).count() > 0:
				delete_triggerids.append(t)

		session.close()
		if len(delete_triggerids) == 0:
			return None

		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"trigger.delete",
					"params":delete_triggerids,
					"auth":self.user_login(),
					"id":1
		})

		api_result = self.request_api(data)
		return api_result

	def action_create(self,name,eventsource,conditions,operations,def_shortdata="{TRIGGER.NAME}: {TRIGGER.STATUS}",def_longdata="{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}"):
		data = json.dumps({
				"jsonrpc":"2.0",
				"method":"action.create",
				"params": {
					"name": name,
					"eventsource": eventsource,
					"evaltype":0,
					"esc_period":1800,
					"def_shortdata": def_shortdata,
					"def_longdata": def_longdata,
					"conditions":conditions,
					"operations":operations
				},
				"auth":self.user_login(),
				"id":1
		})

		api_result = self.request_api(data)['actionids'][0]

		self.created_actions.append(api_result)

		return api_result

	def action_update(self,actionid,status):

		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"action.update",
					"params":{
						"actionid":actionid,
						"status":status
					},
					"auth":self.user_login(),
					"id":1
		})

		api_result = self.request_api(data)['actionids'][0]

		return api_result

	def action_delete(self,actionids):
		delete_actionids = []
		session = loadSession()
		for a in actionids:
			if session.query(Zabbixactions).filter_by(actionid=a).count() > 0:
				delete_actionids.append(a)

		session.close()
		if len(delete_actionids) == 0:
			return None

		data = json.dumps({
					"jsonrpc":"2.0",
					"method":"action.delete",
					"params":delete_actionids,
					"auth":self.user_login(),
					"id":1
		})

		api_result = self.request_api(data)
		return api_result


	def hostgroup_create(self,groupname):
		data = json.dumps({
			"jsonrpc":"2.0",
			"method":"hostgroup.create",
			"params": {
					"name": groupname,
				},
			"auth":self.user_login(),
			"id":1
		})

		api_result = self.request_api(data)['groupids'][0]

		self.created_hostgroups.append(api_result)

		return api_result

	def hostgroup_delete(self,groupids):
		delete_hgs = []
		session = loadSession()
		for g in groupids:
			if session.query(Zabbixhostgroup).filter_by(groupid=g).count() > 0:
				delete_hgs.append(g)

		session.close()

		if len(delete_hgs) == 0:
			return None

		data = json.dumps({
			"jsonrpc":"2.0",
			"method":"hostgroup.delete",
			"params":delete_hgs,
			"auth":self.user_login(),
			"id":1
		})
		api_result = self.request_api(data)
		return api_result

	def drule_create(self,dname,iprange,dcheck):
		data = json.dumps({
			"jsonrpc": "2.0",
    		"method": "drule.create",
    		"params": {
    		    "name": dname,
        		"iprange": iprange,
        		"dchecks": dcheck
    		},
    		"auth": self.user_login(),
    		"id": 1
		})

		api_result = self.request_api(data)['druleids'][0]

		self.created_discovery_rules.append(api_result)

		return api_result

	def drule_delete(self,druleids):
		session = loadSession()
		delete_drules = []
		for d in druleids:
			if session.query(Zabbixdrules).filter_by(druleid=d).count() > 0:
				delete_drules.append(d)
		session.close()
		if len(delete_drules) == 0:
			return None

		data = json.dumps(
		{
			"jsonrpc": "2.0",
    		"method": "drule.delete",
    		"params": delete_drules,
    		"auth": self.user_login(),
    		"id": 1
		})

		api_result = self.request_api(data)

		return api_result

	def triggerprototype_create(self,name,expression):
		data = json.dumps(
		{
			"jsonrpc": "2.0",
    		"method": "triggerprototype.create",
    		"params": {
        		"description": name,
        		"expression": expression
    		},
    		"auth": self.user_login(),
    		"id": 1
		})

		api_result = self.request_api(data)['triggerids'][0]

		self.created_trigger_prototypes.append(api_result)
		
		return api_result

	def triggerprototype_delete(self,tpids):

		delete_tpids = []

		session = loadSession()
		for t in tpids:
			if session.query(Zabbixtriggers).filter_by(triggerid=t).count():
				delete_tpids.append(t)

		session.close()

		if len(delete_tpids) == 0:
			return None

		data = json.dumps({
			"jsonrpc": "2.0",
    		"method": "triggerprototype.delete",
    		"params": delete_tpids,
    		"auth": self.user_login(),
    		"id": 1
		})

		api_result = self.request_api(data)
		return api_result

	def itemprototype_update(self,params):
		data = json.dumps(
		{
			"jsonrpc": "2.0",
			"method": "itemprototype.update",
			"params": params,
			"auth": self.user_login(),
			"id": 1
		})

		api_result = self.request_api(data)

		return api_result

	def rollback(self):

		try:
			self.item_delete(self.created_items)
		except Exception, e:
			pass

		try:
			self.host_delete(self.created_hosts)
		except Exception, e:
			pass

		try:
			self.trigger_delete(self.created_triggers)
		except Exception, e:
			pass

		try:
			self.action_delete(self.created_actions)
		except Exception, e:
			print str(e)

		try:
			self.hostgroup_delete(self.created_hostgroups)
		except Exception, e:
			print str(e)

		try:
			self.drule_delete(self.created_discovery_rules)
		except Exception, e:
			print str(e)

		try:
			self.triggerprototype_delete(self.created_trigger_prototypes)
		except Exception, e:
			print str(e)



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
	# zabbix = zabbix_api()
	# zabbix.item_update(36631,'Count',item_type=2,value_type=4)

	# # test for zabbix_api rollback
	# zabbix = zabbix_api()
	# try:
	# 	host_name = '192.168.221.134'
	# 	host_ip = host_name
	# 	hostgroup_name = ['AWS servers']
	# 	template_name = ['Template OS Linux']
	# 	hostid = zabbix.host_create(host_name , host_ip , hostgroup_name ,template_name)
	# 	print hostid
	# 	itemid = zabbix.item_create('item_name',hostid)
	# 	print itemid
	# 	itemid2 = zabbix.item_create('item_name2',hostid)
	# 	print itemid2
	# 	print 1/0
	# except Exception, e:
	# 	print str(e)
	# 	zabbix.rollback()

	# test for calc_item_create
	# zabbix = zabbix_api()
	# try:
	# 	host_id = 10451
	# 	formula = 'last("10.0.150.191:Count")+last("10.0.20.107:Count")+last("192.168.221.132:Count")+last("192.168.221.130:Count")'
	# 	zabbix.calc_item_create('itemname',host_id,formula)
	# except Exception, e:
	# 	raise e

	zabbix = zabbix_api()
	try:
		# zabbix.hostgroup_delete([12])
		
		# groupname = 'new group test'
		# zabbix.hostgroup_create(groupname)

		# # zabbix.drule_delete([5])
		# dname = 'new drule'
		# iprange = '10.9.0.0/16'
		# dcheck = [{"type":"9","key_":"system.uname","ports":"10050","uniq":"0"}]
		# zabbix.drule_create(dname,iprange,dcheck)


		# name = 'new__new_add_net_key'
		# expression = '{Template OS Linux:net.if.in[{#IFNAME}].last()}>-1'
		# templateid = "10001"
		# zabbix.triggerprototype_create(name,expression)


		# params = {"itemid": 22446,"history": 30}
		# zabbix.itemprototype_update(params)
		# params = {"itemid":22448,"history": 30}
		# zabbix.itemprototype_update(params)
		name = 'AWS auto registration'
		eventsource = 2
		conditions = []
		operations = [
			{
				"operationtype":1,
				"opcommand_hst":
				[
					{
						"hostid":0
					}
				],
				"opcommand" :
				{
					"type": 0,
					"command":'/home/monitor/project/monitor-0.3.7/rename_in_zbx_add_in_monitor.py {HOST.IP}',
					"execute_on":1
				}
			},
			{
				"operationtype":2
			},
			{
				"operationtype":4,
				"opgroup":
				[
					{
						"groupid":32
					}
				]
			},
			{
				"operationtype":6,
				"optemplate":
				[
					{
						"templateid":10001
					}
				]
			},
		]

		def_shortdata = 'Auto registration: {HOST.HOST}'
		def_longdata = 'Host name: {HOST.HOST}\r\nHost IP: {HOST.IP}\r\nAgent port: {HOST.PORT}'
		zabbix.action_create(name,eventsource,conditions,operations,def_shortdata,def_longdata)

	#	print 1/0
	except Exception, e:
		zabbix.rollback()
		traceback.print_exc(file=sys.stdout)





