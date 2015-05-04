#! /home/monitor/project/monitor-0.3.7/flask/bin/python

import inspect,os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import monitor,config


from monitor.zabbix.zabbix_api import zabbix_api
from monitor.zabbix.models import Zabbixhostgroup,Zabbixtriggers,Zabbixactions,Zabbixfunctions
import sys,traceback
from config import HOST_GROUP_NAME,PROTOTYPE_COMMAND_PATH,AR_COMMAND_PATH,UNREACHABLE_ACTION_PATH,\
					UNREACHABLE_ACTION_PATH_2,AUTO_REGISTRATION_NAME,ADD_NET_TRIGGER_NAME,\
					UNREACHABLE_ACTION_NAME,TRIGGER_PROTOTYPE_EXPRESSION,OS_LINUX_TEMPLATEID,\
					ZBX_TEMPLATE_CONF_FILE


def create_aws_group(zbx_groupname,zabbix):
	groupname = zbx_groupname
	groupid = None
	groupid = zabbix.hostgroup_create(groupname)
	return groupid

def update_aws_group(groupid,zbx_groupname,zabbix):
	groupname = zbx_groupname
	groupid = groupid
	result_gid = zabbix.hostgroup_update(groupid,groupname)
	return result_gid

def create_discovery_rule(dname,zabbix):
	iprange = '10.9.0.0/16'
	dcheck = [{"type":"9","key_":"system.uname","ports":"10050","uniq":"0"}]
	zabbix.drule_create(dname,iprange,dcheck)



def create_trigger_prototype(name,zabbix):
	expression = TRIGGER_PROTOTYPE_EXPRESSION
	templateid = OS_LINUX_TEMPLATEID
	zabbix.triggerprototype_create(name,expression)

def update_trigger_prototype(triggerid,trigger_name,zabbix):
	zabbix.triggerprototype_update(triggerid,trigger_name)

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
	
def update_prototype_action(actionid,name,trigger_key,command,zabbix):
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

	zabbix.action_update_condition_operation(actionid,name,eventsource,conditions,operations)



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

def update_auto_registration_action(actionid,name,groupid,command,zabbix):
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
					"templateid":OS_LINUX_TEMPLATEID
				}
			]
		},
	]
	zabbix.action_update_condition_operation(actionid,name,eventsource,conditions,operations)

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

	# ar_command_path = sys.argv[1]
	# prototype_command_path = sys.argv[2]

	# zbx_groupname = sys.argv[3]
	# unreachable_action_command = sys.argv[4]
	# unreachable_action_command_2 = sys.argv[5]


	zbx_groupname = HOST_GROUP_NAME
	ar_command_path = AR_COMMAND_PATH
	prototype_command_path = PROTOTYPE_COMMAND_PATH
	unreachable_action_command = UNREACHABLE_ACTION_PATH
	unreachable_action_command_2 = UNREACHABLE_ACTION_PATH_2

	# print discovery_command_path,prototype_command_path,zbx_groupname

	auto_registration_name = AUTO_REGISTRATION_NAME
	trigger_name = ADD_NET_TRIGGER_NAME
	unreachable_action_name = UNREACHABLE_ACTION_NAME

	zbx_template_conf = ZBX_TEMPLATE_CONF_FILE

	zabbix = zabbix_api()

	try:
		zg = Zabbixhostgroup.query.filter_by(name=zbx_groupname).first()
		groupid = None
		if zg == None:
			groupid = create_aws_group(zbx_groupname,zabbix)
		else:
			tmp_groupid = zg.groupid
			# print 'tmp_groupid',tmp_groupid
			groupid = update_aws_group(tmp_groupid,zbx_groupname,zabbix)
			# groupid = zg.groupid

		print 'group conf done'

		# tp = Zabbixtriggers.query.filter_by()
		zf = Zabbixfunctions.query.filter_by(itemid=22446).first()
		if zf == None:
			create_trigger_prototype(trigger_name,zabbix)
		else:
			tmp_triggerid = zf.triggerid
			update_trigger_prototype(tmp_triggerid,trigger_name,zabbix)

		print 'trigger prototype done'

		za = Zabbixactions.query.filter_by(name=trigger_name).first()
		if za == None:
			create_prototype_action(trigger_name,trigger_name,prototype_command_path,zabbix)
		else:
			tmp_actionid = za.actionid
			update_prototype_action(tmp_actionid,trigger_name,trigger_name,prototype_command_path,zabbix)

		print 'prototype action done'

		zara = Zabbixactions.query.filter_by(name=auto_registration_name).first()
		if zara == None:
			create_auto_registration_action(auto_registration_name,groupid,ar_command_path,zabbix)
		else:
			tmp_actionid = zara.actionid
			update_auto_registration_action(tmp_actionid,auto_registration_name,groupid,ar_command_path,zabbix)

		print 'auto registration action done'
		
		update_itemprototype(zabbix)

		ua = Zabbixactions.query.filter_by(name=unreachable_action_name).first()
		if ua != None:
			zabbix.action_delete([ua.actionid])
		create_unreachable_action(zabbix,unreachable_action_command,unreachable_action_command_2,unreachable_action_name)

		print 'unreachable host action done'

		zabbix.import_template_file(zbx_template_conf)

		print 'import template file done'

		# print 1/0
	except Exception, e:
		zabbix.rollback()
		traceback.print_exc(file=sys.stdout)
