
from monitor.chart.search import ItemSearch
from config import BY_GROUP_RESULT,PER_INSTANCE_RESULT,BY_GROUP_TABLE_HEAD,PER_INSTANCE_TABLE_HEAD,\
					FUNC_TYPE_COUNT,FUNC_TYPE_AVG,FUNC_TYPE_MAX,FUNC_TYPE_MIN,FUNC_TYPE_SUM
from monitor.zabbix.models import Zabbixhistory,Zabbixhistoryuint
import time

head_grouptype_map = {
	BY_GROUP_RESULT:BY_GROUP_TABLE_HEAD,
	PER_INSTANCE_RESULT:PER_INSTANCE_TABLE_HEAD
}

function_type_map = {
	'Sum' : FUNC_TYPE_SUM,
	'Average' : FUNC_TYPE_AVG,
	'Minimum' : FUNC_TYPE_MIN,
	'Maximum' : FUNC_TYPE_MAX,
	'Count' : FUNC_TYPE_COUNT
}

class Chart():

	@classmethod 
	def metric_content_2_item_list(cls,metric_content):
		return 0

	@classmethod
	def selected_metrics_2_metric_content(cls,selected_metrics):
		result = []
		for option in selected_metrics:
			for table_title in selected_metrics[option]:
				for td_content in selected_metrics[option][table_title]['metric_result']:
					tmp = {'row_type':table_title,'row':td_content}
					result.append(tmp)
		return result

	@classmethod
	def item_list_2_history_data(cls,item_arr,ground,time_since,time_till):
		history_result = Zabbixhistory.get_interval_history(item_arr,ground,time_since,time_till)
		historyuint_result =Zabbixhistoryuint.get_interval_history(item_arr,ground,time_since,time_till)
		query_result = []
		if history_result == None:
			query_result = historyuint_result
		else:
			query_result = history_result

		if query_result == None:
			query_result = []
		return query_result

	@classmethod
	def item_history_data_2_chart_init_series_data(cls,data,time_since,time_till,ground,functiontype):

		init_data = []

		from_t = time_since/ground*ground
		to_t = time_till/ground*ground

		data_index = 0;

		origin = from_t
		# last_value = None

		while from_t < to_t:
			if data_index < len(data) and from_t > data[data_index][4]*ground:
				# last_value = data[data_index][functiontype]
				data_index += 1
				continue

			if data_index < len(data) and from_t == data[data_index][4]*ground:
				tmp = from_t
				arr = []
				arr.append(int(tmp*1000))
				arr.append(data[data_index][functiontype])
				init_data.append(arr)
				# last_value = data[data_index][functiontype]
				data_index += 1
			else:
				tmp = from_t
				arr = []
				arr.append(int(tmp*1000))
				arr.append(None)
				# arr.append(last_value)
				init_data.append(arr)

			from_t += ground
		# history_data = 
		return init_data

	@classmethod
	def item_history_data_2_chart_update_series_data(cls,data,time_since,functiontype):
		update_data = []

		update_data.append(time_since*1000)
		if len(data) > 0:
			update_data.append(data[0][functiontype])
		else:
			update_data.append(None)

		return update_data

	@classmethod
	def interval_init_result(cls,time_since,time_till,ground,function_type,row_result):
		result = []

		no_history_count = 0
		for row in row_result:
			item_list = ItemSearch.row_2_item_list(row['row_type'],row['row'])
			history_data = cls.item_list_2_history_data(item_list,ground,time_since,time_till)
			if len(history_data) == 0:
				no_history_count += 1
			series_data = cls.item_history_data_2_chart_init_series_data(history_data,time_since,time_till,ground,function_type)
			series_name = ItemSearch.row_type_2_name(row['row_type'],row['row'])
			tmp = {'data':series_data,'name':series_name}
			result.append(tmp)

		return result


	@classmethod
	def init_with_now(cls,row_result,chart_config):

		result = []

		time_till = int(time.time())
		time_since = time_till - int(chart_config['init_time_length'])
		ground = int(chart_config['frequency'])
		function_type = function_type_map.get(chart_config['function_type'],FUNC_TYPE_AVG)
		# no_history_count = 0
		# for row in row_result:
		# 	item_list = ItemSearch.row_2_item_list(row['row_type'],row['row'])
		# 	history_data = cls.item_list_2_history_data(item_list,ground,time_since,time_till)
		# 	if len(history_data) == 0:
		# 		no_history_count += 1
		# 	series_data = cls.item_history_data_2_chart_init_series_data(history_data,time_since,time_till,ground,function_type)
		# 	series_name = ItemSearch.row_type_2_name(row['row_type'],row['row'])
		# 	tmp = {'data':series_data,'name':series_name}
		# 	result.append(tmp)
		result = cls.interval_init_result(time_since,time_till,ground,function_type,row_result)

		return result


	@classmethod
	def init_with_interval(cls,row_result,chart_config):
		result = []

		time_till = int(chart_config['to_clock'])
		time_since = int(chart_config['from_clock'])
		ground = int(chart_config['frequency'])
		function_type = function_type_map.get(chart_config['function_type'],FUNC_TYPE_AVG)

		result = cls.interval_init_result(time_since,time_till,ground,function_type,row_result)
		return result


	@classmethod
	def init(cls,selected_metrics,chart_config):
		# print selected_metrics,chart_config
		row_result = cls.selected_metrics_2_metric_content(selected_metrics)
		# print "result",result
		# item_list_arr = []

		result = []

		if chart_config['update_flag']:
			result = cls.init_with_now(row_result,chart_config)
		else:
			result = cls.init_with_interval(row_result,chart_config)

		

		# if no_history_count == len(row_result):
		# 	raise Exception('No history data')
		return result


	@classmethod
	def update(cls,selected_metrics,chart_config):
		row_result = cls.selected_metrics_2_metric_content(selected_metrics)
		result = []
		time_till = int(time.time())
		time_since = time_till - int(chart_config['frequency'])
		ground = int(chart_config['frequency'])
		time_since = time_since / ground * ground 
		function_type = function_type_map.get(chart_config['function_type'],FUNC_TYPE_AVG)
		no_history_count = 0
		for row in row_result:
			item_list = ItemSearch.row_2_item_list(row['row_type'],row['row'])
			history_data = cls.item_list_2_history_data(item_list,ground,time_since,time_till)
			if len(history_data) == 0:
				no_history_count += 1

			series_data = cls.item_history_data_2_chart_update_series_data(history_data,time_since,function_type)
			result.append(series_data)

		return result





		
