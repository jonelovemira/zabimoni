#! flask/bin/python

from monitor.zabbix.zabbix_api import zabbix_api
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
	


def update_itemprototype(zabbix):

	params = {"itemid": 22446,"history": 30}
	zabbix.itemprototype_update(params)
	params = {"itemid":22448,"history": 30}
	zabbix.itemprototype_update(params)


if __name__ == '__main__':

	ar_command_path = sys.argv[1]
	prototype_command_path = sys.argv[2]

	zbx_groupname = sys.argv[3]

	# print discovery_command_path,prototype_command_path,zbx_groupname

	auto_registration_name = 'AWS auto registration'
	trigger_name = 'add_net_key'

	zabbix = zabbix_api()

	try:
		groupid = create_aws_group(zbx_groupname,zabbix)
		create_trigger_prototype(trigger_name,zabbix)
		# create_discovery_rule(dname,zabbix)
		create_prototype_action(trigger_name,trigger_name,prototype_command_path,zabbix)
		create_auto_registration_action(auto_registration_name,groupid,ar_command_path,zabbix)
		update_itemprototype(zabbix)

		# print 1/0
	except Exception, e:
		zabbix.rollback()
		traceback.print_exc(file=sys.stdout)
