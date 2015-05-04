from monitor.chart.search import ItemSearch
from monitor.item.models import Service,Item,Host
from monitor.zabbix.models import Zabbixinterface,loadSession,Zabbixhosts,Zabbixhistory,Zabbixhistoryuint
import json

class Overall():
	"""docstring for Overall"""
	def __init__(self, arg):
		self.arg = arg
		self.info = []


	def overall_data(self,input_json):
		pass

		'''input_dict = 
			input_dict = {'services': ['monitor'], 'metrics': [{'metricname':'us-east-1_AmazonEC2'}], 'time_to': 1428628814, 'time_from': 1428542432}
		'''
	def mechine_health(self,input_dict):
		services = input_dict['services']

		time_from = input_dict['time_from']
		time_to = input_dict['time_to']

		metrics = input_dict['metrics']
		session = loadSession()
		result = {}
		for s in services:
			group = Service.query.filter_by(servicename=s).first()
			if group != None:
				result[s] = {}
				for h in group.hosts.all():
					zinterface = session.query(Zabbixinterface).filter_by(hostid=h.hostid).first()
					zh = session.query(Zabbixhosts).get(h.hostid)
					if zinterface is None or zh is None:
						continue
					result[s][zinterface.ip] = {}
					result[s][zinterface.ip]['available'] = zh.available

					for m in metrics:
						itemids = ItemSearch.find_item_list_for_table_row_instance([None,None,zinterface.ip,m['metricname']])

						if len(itemids) > 0:
							v = Zabbixhistory.get_interval_history_no_ground(itemids,time_from,time_to)
							vuint = Zabbixhistoryuint.get_interval_history_no_ground(itemids,time_from,time_to)
							if vuint is  None and v is None:
								continue
							result[s][zinterface.ip][m['metricname']] = v if v is not None else vuint

		session.close()
		return result


	'''input_dict = 
	{'service_metrics':{'monitor':[{'metricname':'us-east-1_All','condition':'>100'}]},'time_from':1428451200,'time_to':1428624000}'''
	def business_health(self,input_dict):
		services_metrics = input_dict['service_metrics']

		time_from = input_dict['time_from']
		time_to = input_dict['time_to']

		session = loadSession()
		result = {}

		for sm in services_metrics:
			group = Service.query.filter_by(servicename=sm).first()
			if group != None:
				result[sm] = []
				for metric_condition in services_metrics[sm]:
					metricname = metric_condition['metricname']
					condition = metric_condition['condition']
					itemids = ItemSearch.find_item_list_for_table_row_group([sm,metricname])

					if len(itemids) > 0:
						recordsuint = Zabbixhistoryuint.get_interval_condition_record(itemids,time_from,time_to,condition)
						records = Zabbixhistory.get_interval_condition_record(itemids,time_from,time_to,condition)
						if records is None and recordsuint is None:
							continue
						tmp_records = recordsuint if recordsuint is not None else records
						for r in tmp_records:
							itemid = r[0]
							clock = r[1]
							value = r[2]
							item = Item.query.get(itemid)
							if item != None:
								host = item.host
								zinterface = session.query(Zabbixinterface).filter_by(hostid=host.hostid).first()
								if zinterface != None:
									result[sm].append([host.hostname,zinterface.ip,item.itemname,clock,value])


		session.close()
		return result


		'''
		input: {'monitor':{'us-east-1_All':{'time_from':1428451200,'time_to':1428624000,'frequency':60}}}
		output: {'monitor': {'us-east-1_All': {'statics': [[6, 2462.3200000000002, 2799.8899999999999, 2129.0999999999999, 14773.92]], 'last': 2799.8899999999999}}}
		'''
	def core_data(self,input_dict):
		services_metrics = input_dict
		session = loadSession()
		result = {}
		for sm in services_metrics:
			group = Service.query.filter_by(servicename=sm).first()
			if group != None:
				result[sm] = {}
				for metric in services_metrics[sm]:
					time_from = services_metrics[sm][metric]['time_from']
					time_to = services_metrics[sm][metric]['time_to']
					ground = int(services_metrics[sm][metric]['frequency'])

					result[sm][metric] = {}

					itemids = ItemSearch.find_item_list_for_table_row_group([sm,metric])

					if len(itemids) > 0 :
						v = Zabbixhistory.get_interval_history_no_ground(itemids,time_from,time_to)
						vuint = Zabbixhistoryuint.get_interval_history_no_ground(itemids,time_from,time_to)
						if vuint is  None and v is None:
							continue

						result[sm][metric]['statics'] = v if v is not None else vuint

						last_value = Zabbixhistory.get_interval_last_few_records(itemids,time_from,time_to)
						last_valueuint = Zabbixhistoryuint.get_interval_last_few_records(itemids,time_from,time_to)

						if last_value is None and last_valueuint is None:
							continue

						tmp_last_value = last_value if last_value is not None else last_valueuint

						tmp_dict = {}
						for x in tmp_last_value:
							# tmp_dict[x[1]/ground]
							index = x[1]//ground
							if index not in tmp_dict:
								tmp_dict[index] = {} 
								tmp_dict[index]['value'] = x[2]
								tmp_dict[index]['count'] = 1
							else:
								tmp_dict[index]['value'] += x[2]
								tmp_dict[index]['count'] += 1

						last_sum_key = max(key for key in tmp_dict if tmp_dict[key]['count'] == len(itemids))
						last_sum = tmp_dict[last_sum_key]['value']
						
						result[sm][metric]['last'] = last_sum

		session.close()
		return result

					




		