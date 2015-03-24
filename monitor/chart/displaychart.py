
from monitor.chart.search import ItemSearch
from config import BY_GROUP_RESULT,PER_INSTANCE_RESULT,BY_GROUP_TABLE_HEAD,PER_INSTANCE_TABLE_HEAD,\
					FUNC_TYPE_COUNT,FUNC_TYPE_AVG,FUNC_TYPE_MAX,FUNC_TYPE_MIN,FUNC_TYPE_SUM,WINDOW_CHART,\
					AWS_FEE_TABEL_HEAD,PAGE_CHART,DESIRED_DISPLAY_POINTS,TABLE_HEAD_AVAILABILITY
from monitor.zabbix.models import Zabbixhistory,Zabbixhistoryuint
import time

from monitor import db
from monitor.chart.models import Window,Selectedmetrics,Option,Displaytable,Displaytablerow,Attr,Chartconfig,Page
from monitor.item.models import Aws

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
		if selected_metrics == None:
			return result
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

		# while from_t <= to_t + ground:
		while from_t < to_t :
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
	def interval_init_result(cls,time_since,time_till,ground,function_type,row_result,shared_yaxis=False):
		result = []

		steps = (time_till - time_since) / ( ground * DESIRED_DISPLAY_POINTS )

		if steps < 1:
			steps = 1

		ground = ground * steps

		series_index = 0

		no_history_count = 0
		for row in row_result:
			item_list = ItemSearch.row_2_item_list(row['row_type'],row['row'])
			history_data = cls.item_list_2_history_data(item_list,ground,time_since,time_till)
			if len(history_data) == 0:
				no_history_count += 1
			series_data = cls.item_history_data_2_chart_init_series_data(history_data,time_since,time_till,ground,function_type)
			series_name = ItemSearch.row_type_2_name(row['row_type'],row['row'])
			item_unit = 'unknown'

			item_unit = ItemSearch.item_list_2_unitname(item_list)
			
			tmp = {'data':series_data,'name':str(series_name),'unit_name':str(item_unit)}

			if not shared_yaxis:
				tmp['yAxis'] = series_index

			series_index += 1

			result.append(tmp)

		return result


	@classmethod
	def init_with_now(cls,row_result,chart_config):

		result = []

		time_till = int(time.time())
		time_since = time_till - int(chart_config['init_time_length'])
		# time_since = time_till - int(chart_config['frequency'])
		ground = int(chart_config['frequency'])
		# console.log("ground",ground)
		# print "ground",ground
		time_since = time_since / ground * ground
		# ground = int(chart_config['frequency'])
		function_type = function_type_map.get(chart_config['function_type'],FUNC_TYPE_AVG)
		shared_yaxis = chart_config.get('shared_yaxis',True)
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
		result = cls.interval_init_result(time_since,time_till,ground,function_type,row_result,shared_yaxis)

		return result


	@classmethod
	def init_with_interval(cls,row_result,chart_config):
		result = []

		time_till = int(chart_config['to_clock'])
		time_since = int(chart_config['from_clock'])
		ground = int(chart_config['frequency'])
		shared_yaxis = chart_config.get('shared_yaxis',True)
		function_type = function_type_map.get(chart_config['function_type'],FUNC_TYPE_AVG)

		result = cls.interval_init_result(time_since,time_till,ground,function_type,row_result,shared_yaxis)
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

	@classmethod
	def save_chart(cls,selected_metrics,chart_config,windowname,user,index,window_type,page):

		for aws in Aws.query.all():
			head_grouptype_map[aws.awsname] = AWS_FEE_TABEL_HEAD

		print windowname

		if window_type == WINDOW_CHART:
			tmp_window = user.windows.filter_by(windowname=windowname).filter_by(type=window_type).first()
			if tmp_window != None:
				raise Exception('same name for saving is already exists')

		

		window = Window(windowname,window_type,index,user,page)

		db.session.add(window)

		sm = Selectedmetrics(window)

		db.session.add(sm)

		for option_iter in selected_metrics:

			option = Option(option_iter,sm)
			db.session.add(option)

			for table_title_iter in selected_metrics[option_iter]:

				dt = Displaytable(table_title_iter,option)
				db.session.add(dt)

				table_head = head_grouptype_map.get(table_title_iter,None)
				if table_head == None:
					raise Exception('unknown table head')

				for td_content in selected_metrics[option_iter][table_title_iter]['metric_result']:

					dtr = Displaytablerow(dt)
					db.session.add(dtr)

					assert len(table_head) == len(td_content)

					for i in range(len(td_content)):
						attr = Attr(table_head[i],td_content[i],dtr,None)
						db.session.add(attr)

		cc = Chartconfig(window)
		db.session.add(cc)

		for key in chart_config:
			tmp_attr = Attr(key,chart_config[key],None,cc)
			db.session.add(tmp_attr)

		return window

	@classmethod
	def save_window_chart(cls,selected_metrics,chart_config,windowname,user):

		index = 0
		window_type = WINDOW_CHART

		return cls.save_chart(selected_metrics,chart_config,windowname,user,index,window_type,None)

	@classmethod
	def save_page(cls,nine_charts,pagename,user):

		tmp_page = user.pages.filter_by(pagename=pagename).first()

		if tmp_page != None:
			raise Exception('same name for saving already exists')

		page = Page(pagename,user)
		db.session.add(page)

		for index in nine_charts:
			selected_metrics = nine_charts[index]['selected_metric_result']
			chart_config = nine_charts[index]['chart_config']

			## chart title can be saved in nine_charts
			
			# windowname = pagename + ' in ' + str(index)
			windowname = nine_charts[index]['chart_name']
			window_type = PAGE_CHART
			cls.save_chart(selected_metrics,chart_config,windowname,user,index,window_type,page)

		return page

	@classmethod
	def delete_page(cls,pageid):
		page = Page.query.get(pageid)

		if page == None:
			raise Exception( 'page to be delete do not exist' )

		for w in page.windows.all():
			cls.delete_window_chart(w.windowid)

		db.session.delete(page)

	@classmethod
	def load_page(cls,pageid):
		page = Page.query.get(pageid)

		if page == None:
			raise Exception( 'page to be load do not exist' )

		result = {}

		for w in page.windows.all():
			window_result = cls.load_window_chart(w.windowid)
			index = w.index
			result[index] = window_result

		return result




	@classmethod
	def delete_window_chart(cls,windowid):
		window = Window.query.get(windowid)
		if window == None:
			raise Exception('window do not exist')

		selectedmetrics = window.selectedmetrics.first()
		chartconfig = window.chartconfig.first()

		if selectedmetrics != None:
			for option in selectedmetrics.options.all():


				for dt in option.displaytables.all():

					for dtr in dt.rows.all():
						for attr in dtr.attrs.all():
							db.session.delete(attr)
						db.session.delete(dtr)

					db.session.delete(dt)

				db.session.delete(option)

			db.session.delete(selectedmetrics)

		if chartconfig != None:
			for attr in chartconfig.attrs.all():
				db.session.delete(attr)
			db.session.delete(chartconfig)

		db.session.delete(window)






	@classmethod
	def load_window_chart(cls,windowid):

		for aws in Aws.query.all():
			head_grouptype_map[aws.awsname] = AWS_FEE_TABEL_HEAD


		result = {}

		window = Window.query.get(windowid)
		if window == None:
			raise Exception('window do not exist')

		selected_metrics = {}
		selectedmetrics = window.selectedmetrics.first()
		chartconfig = window.chartconfig.first()
		chart_config = {}

		if selectedmetrics != None:
			for option in selectedmetrics.options.all():
				selected_metrics[option.optionname] = {}

				for dt in option.displaytables.all():
					selected_metrics[option.optionname][dt.displaytablename] = {}

					table_head = head_grouptype_map.get(dt.displaytablename,None)
					if table_head == None:
						raise Exception('unknown table head')

					selected_metrics[option.optionname][dt.displaytablename]['metric_count'] = 0
					selected_metrics[option.optionname][dt.displaytablename]['metric_result'] = []
					selected_metrics[option.optionname][dt.displaytablename]['table_head'] = table_head

					for dtr in dt.rows.all():
						selected_metrics[option.optionname][dt.displaytablename]['metric_count'] += 1
						tmp_arr = list(table_head)
						for attr in dtr.attrs.all():
							tmp_arr[table_head.index(attr.attrname)] = attr.attrvalue

						if table_head.index(TABLE_HEAD_AVAILABILITY) > 0:
							tmp_hostid = ItemSearch.find_hostid_for_table_row_instance(tmp_arr)
							if tmp_hostid != None:
								tmp_arr[table_head.index(TABLE_HEAD_AVAILABILITY)] = ItemSearch.hostid_2_availability(tmp_hostid)

						selected_metrics[option.optionname][dt.displaytablename]['metric_result'].append(tmp_arr)

		if chartconfig != None:
			for attr in chartconfig.attrs.all():
				chart_config[attr.attrname] = attr.attrvalue

		if chart_config['use_utc'] == '0':
			chart_config['use_utc'] = False
		elif chart_config['use_utc'] == '1':
			chart_config['use_utc'] = True

		result['selected_metrics'] = selected_metrics
		result['chart_config'] = chart_config
		result['chart_name'] = window.windowname

		return result

	@classmethod
	def smr_2_itemlist(cls,selected_metrics):
		row_result = cls.selected_metrics_2_metric_content(selected_metrics)
		convert_result = []
		for row in row_result:
			item_list = ItemSearch.row_2_item_list(row['row_type'],row['row'])
			convert_result = list( set(convert_result) | set(item_list) )

		return convert_result