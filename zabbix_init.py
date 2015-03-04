#! flask/bin/python

from monitor.zabbix.zabbix_api import zabbix_api
from monitor.zabbix.models import Zabbixhostgroup,Zabbixtriggers,Zabbixactions,Zabbixfunctions
import sys,traceback


def create_aws_group(zbx_groupname,zabbix):
	groupname = zbx_groupname
	groupid = None
	groupid = zabbix.hostgroup_create(groupname)
	return groupid

def create_discovery_rule(dname,zabbix):
	iprange = '10.9.0.0/16'
	dcheck = [{"type":"9","key_":"system.uname","ports":"10050","uniq":"0"}]
	zabbix.drule_create(dname,iprange,dcheck)



def create_trigger_prototype(name,zabbix):
	expression = '{Template OS Linux:net.if.in[{#IFNAME}].last()}>-1'
	templateid = "10001"
	zabbix.triggerprototype_create(name,expression)


def create_prototype_action(name,trigger_key,command,zabbix):
	name = name
	eventsource = 0
	conditions = [
		{
			"conditiontype": 16,
			"operator": 7
		},
		{
			"conditiontype": 5,
			"operator": 0,
			"value": 1
		},
		{
			"conditiontype": 3,
			"operator": 2,
			"value": trigger_key
		}
	]
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
				"command":command,
				"execute_on":1
			}
		}
	]

	zabbix.action_create(name,eventsource,conditions,operations)
	

def create_auto_registration_action(name,groupid,command,zabbix):
	name = name
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
				"command":command,
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
					"groupid":groupid
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

def create_unreachable_action(zabbix,command,command_2,action_name='agent is unreachable',trigger_name='is unreachable for 5 minutes'):
	name = action_name
	eventsource = 0
	conditions = [
		{
			"conditiontype": 16,
			"operator": 7
		},
		{
			"conditiontype": 5,
			"operator": 0,
			"value": 1
		},
		{
			"conditiontype": 3,
			"operator": 2,
			"value": trigger_name
		}
	]
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
				"command":command,
				"execute_on":1
			}
		},
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
				"command":command_2,
				"execute_on":1
			}
		}
	]

	zabbix.action_create(name,eventsource,conditions,operations)
	


def update_itemprototype(zabbix):

	params = {"itemid": 22446,"history": 30}
	zabbix.itemprototype_update(params)
	params = {"itemid":22448,"history": 30}
	zabbix.itemprototype_update(params)


if __name__ == '__main__':

	ar_command_path = sys.argv[1]
	prototype_command_path = sys.argv[2]

	zbx_groupname = sys.argv[3]
	unreachable_action_command = sys.argv[4]
	unreachable_action_command_2 = sys.argv[5]

	# print discovery_command_path,prototype_command_path,zbx_groupname

	auto_registration_name = 'AWS auto registration'
	trigger_name = 'add_net_key'
	unreachable_action_name = 'agent is unreachable'

	zabbix = zabbix_api()

	try:
		zg = Zabbixhostgroup.query.filter_by(name=zbx_groupname).first()
		groupid = None
		if zg == None:
			groupid = create_aws_group(zbx_groupname,zabbix)
		else:
			groupid = zg.groupid

		# tp = Zabbixtriggers.query.filter_by()
		zf = Zabbixfunctions.query.filter_by(itemid=22446).first()
		if zf == None:
			create_trigger_prototype(trigger_name,zabbix)

		za = Zabbixactions.query.filter_by(name=trigger_name).first()
		if za == None:
			create_prototype_action(trigger_name,trigger_name,prototype_command_path,zabbix)

		zara = Zabbixactions.query.filter_by(name=auto_registration_name).first()
		if zara == None:
			create_auto_registration_action(auto_registration_name,groupid,ar_command_path,zabbix)
		
		update_itemprototype(zabbix)

		ua = Zabbixactions.query.filter_by(name=unreachable_action_name).first()
		if ua != None:
			zabbix.action_delete([ua.actionid])
		create_unreachable_action(zabbix,unreachable_action_command,unreachable_action_command_2,unreachable_action_name)

		# print 1/0
	except Exception, e:
		zabbix.rollback()
		traceback.print_exc(file=sys.stdout)
