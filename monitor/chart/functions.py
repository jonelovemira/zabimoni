from monitor.item.models import Area,Service,Host,Aws,Itemtype,Item,Itemtype
from monitor.chart.models import *
from sqlalchemy.sql import func,union
from monitor.zabbix.models import Zabbixhistory,Zabbixhistoryuint,Zabbixhosts
import time,json,os
from monitor import db
from subprocess import call
from datetime import datetime
# from send_email import monitor_status_notification
from monitor.MonitorException import *
import string
from flask import current_app
from boto.s3.connection import S3Connection
from crontab import CronTab
from monitor.decorators import async
from monitor.functions import construct_random_str

from config import PHANTOMJS,HIGHCHART_CONVERT,REPORT_OUTPUT_DIR,REPORT_OUTPUT_WIDTH,\
				REPORT_OUTPUT_TYPE,REPORT_OUTPUT_SCALE,GENERATE_REPORT_PATH,\
				S3_BUCKET_NAME,S3_BUCKET_FOLDER,CHART_INIT_TIME,CHART_HISTORY_TIME,\
				DESIRED_DISPLAY_POINTS,RESOLUTION,SECOND_TO_MILLI,SCHEDULE_ALL_FILENAME,\
				S3_SCHEDULE_FOLDER,S3_MONITOR_BUCKET_NAME,S3_MONITOR_REPORT_FOLDER,\
				S3_MONITOR_SCHEDULE_FOLDER,S3_MONITOR_SHEDULE_ALL_FILENAME

########################################################################################
###222222222222222222222222222222222222222222222222222222222222222222222222222222#######
########################################################################################
###########     return itemtypes based on selection of area,service,host,aws   #########
def get_area_host(area):
	result = []
	if len(area) == 0:
		result = Host.query.all()
	else:
		for a in area:
			atmp = Area.query.filter_by(areaid=a).first()
			result = list( set(result) | set(atmp.hosts))

	return result

def get_service_host(service):
	result = []
	if len(service) == 0:
		result = Host.query.all()
	else:
		for s in service:
			stmp = Service.query.filter_by(serviceid=s).first()
			result = list( set(result) | set(stmp.hosts))

	return result

def get_hosts(host):
	result = []
	if len(host) == 0:
		result = Host.query.all()
	else:
		for h in host:
			htmp = Host.query.filter_by(hostid=h).first()
			result.append(htmp)
	return result

def get_area_aws(area):
	result = []
	if len(area) == 0:
		result = Aws.query.all()
	else:
		for a in area:
			atmp = Area.query.filter_by(areaid=a).first()
			result = list( set(result) | set(atmp.awses))

	return result

def get_aws(aws):
	result = []
	if len(aws) == 0:
		result = Aws.query.all()
	else:
		for a in aws:
			atmp = Aws.query.filter_by(awsid=a).first()
			result.append(atmp)

	return result

def get_all_itemtypes(area=[],service=[],host=[],aws=[]):
	result = {}
	# all index are empty
	if len(area) == 0 and len(service) == 0 and len(host) == 0 and len(aws) == 0:
		return result

	# choosed service or host will comfilct with aws
	if (len(service) != 0 or len(host) != 0) and len(aws) != 0:
		return result

	finalhost = []

	# may have some hosts
	if not (len(area) == 0 and len(service) == 0 and len(host) == 0):
	 	ahosts = get_area_host(area)
	 	shosts = get_service_host(service)
	 	hhosts = get_hosts(host)
	 	# get intersect of hosts
		finalhost = list(set(ahosts) & set(shosts) & set(hhosts))

	# have no items to monitor
	if len(finalhost) == 0 and len(aws) == 0:
		return result

	#collect normal monitor items
	hostids = []
	for h in finalhost:
		hostids.append(h.hostid);
		for item in h.items.all():
			if item.itemtype.aws != None:
				continue
			if result.has_key(item.itemtype_id):
				result[item.itemtype_id]['items'].append(item.itemid)
			else :
				itemtype = item.itemtype
				result[item.itemtype_id] = {}
				result[item.itemtype_id]['name'] = itemtype.itemtypename
				result[item.itemtype_id]['itemdatatypename'] = itemtype.itemdatatype.itemdatatypename
				result[item.itemtype_id]['items'] = [item.itemid]
				result[item.itemtype_id]['time_frequency'] = itemtype.time_frequency
	if len(result) != 0:
		return {'itemtype':result,'hostids':hostids}

	# have no aws items
	if len(area) == 0 and len(aws) == 0:
		return result

	
	checkedaws = get_aws(aws)
	areaaws = get_area_aws(area)
	finalaws = list( set(checkedaws) & set(areaaws))

	# collect items in intersect itemtypes
	for fa in finalaws:
		for it in fa.itemtypes:
			if it.items.count() == 0:
				continue
			result[it.itemtypeid] = {}
			result[it.itemtypeid]['name'] = it.itemtypename
			result[it.itemtypeid]['itemdatatypename'] = it.itemdatatype.itemdatatypename
			result[it.itemtypeid]['items'] = []
			for i in it.items.all():
				result[it.itemtypeid]['items'].append(i.itemid)
			result[it.itemtypeid]['time_frequency'] = it.time_frequency

	return {'itemtype':result}

########################################################################################
###222222222222222222222222222222222222222222222222222222222222222222222222222222#######
########################################################################################



#########################################################################################
###11111111111111111111111111111111111111111111111111111111111111111111111111111111######
#########################################################################################
#############   generate report at server side via export.js ############################

def generate_png_chart(chartname,infile_path,callback_path):
	# call(["monitor/static/js/export/generate/phantomjs",\
	# 	"monitor/static/js/export/highcharts-convert.js",\
	# 	"-infile","monitor/static/js/export/generate/infile.json",\
	# 	"-callback","monitor/static/js/export/generate/callback.js",\
	# 	"-outfile","monitor/static/report/" + chartname,"-width",\
	# 	"2400","-constr","StockChart","-scale","1"])
	call([PHANTOMJS,HIGHCHART_CONVERT,"-infile",infile_path,"-callback",callback_path,\
		"-outfile",REPORT_OUTPUT_DIR + chartname, "-width",REPORT_OUTPUT_WIDTH,\
		"-constr",REPORT_OUTPUT_TYPE,"-scale",REPORT_OUTPUT_SCALE])



def generate_infile(save_json,imgname):
	infile_path = '/tmp/' + imgname + '.json'
	f = open(infile_path,'w')
	f.write(save_json)
	f.close()
	return infile_path

def generate_callback_js(imgname):
	callback_str = '''function(chart) {}'''
	callback_path = '/tmp/' + imgname + '.js'
	f = open(callback_path,'w')
	f.write(callback_str)
	f.close()
	return callback_path



def create_chart_json(series_data,reportname,y_title):
	tmp = '''{
				legend: {
                    enabled: true,
                    align: 'center',
                    backgroundColor: '#FCFFC5',
                    borderColor: 'black',
                    borderWidth: 2,
                    layout: 'vertical',
                    verticalAlign: 'bottom',
                    y: 0,
                    shadow: true,
                    labelFormatter : function()
                    {
                        return this.name;
                    }
                },
                rangeSelector : {
                        // selected : 1,
                        inputEnabled: true
                },
                title : {
                    text : ''' + "'" + reportname + "'" + '''
                },
                navigator:
                {
                	enabled:false
                },
                scrollbar:
                {
                	enabled:false
                },
                plotOptions:{
                    line:{
                        turboThreshold:1000000
                    }
                },
                yAxis: {
                        min: 0,
                        startOnTick: false,
                        title: {
                        	text: ''' + "'" + y_title + "'" + '''
                        }
                },
                credits:{
                    enabled:false
                },
                series:''' + series_data + ''' 
	}'''
	return tmp 

	

def generate_report_series_data(report,time_since,time_till):
	r = report
	# print r
	series = r.report_series
	all_series_info = []
	for s in series.all():
		series_info = {}
		itemlist = []
		# for i in s.items:
		# 	itemlist.append(i.itemid)

		itid = s.itemtype.itemtypeid

		indexes = index_arg_2_array(s.area_id,s.service_id,s.host_id,s.aws_id)
		all_itemtypes = get_all_itemtypes(indexes['area'],indexes['service'],indexes['host'],indexes['aws'])
		if all_itemtypes['itemtype'].has_key(s.itemtype.itemtypeid):
			itemlist = all_itemtypes['itemtype'][s.itemtype.itemtypeid]['items']

		series_info['series_item_list'] = itemlist
		series_info['series_name'] = s.seriesname
		all_series_info.append(series_info)

	time_frequency = int(r.scaletype)
	functiontype = r.functiontype
	sr = report_series_result(all_series_info,time_frequency,time_since,time_till,functiontype)
	return sr

## itemtype' unitname cannot be null
def generate_report_y_title(report):
	r = report
	series = r.report_series
	y_title = []
	for s in series.all():
		grsd_it = s.itemtype
		tmp_title = grsd_it.itemunit
		if not tmp_title in y_title:
			y_title.append(tmp_title)
	return ','.join(y_title)

def generate_report(report,postfix,time_since,time_till):
	r = report
	imgfilename = r.owner.username + '_' + r.reportname + '_' + postfix + '.png'
	series_data = generate_report_series_data(r,time_since,time_till)
	tmp = str(series_data)
	tmp = tmp.replace('None','null')
	y_title = generate_report_y_title(r)
	chart_json = create_chart_json(tmp,r.reportname,y_title)
	infile_path = generate_infile(chart_json,imgfilename)
	callback_path = generate_callback_js(imgfilename)
	generate_png_chart(imgfilename,infile_path,callback_path)
	os.unlink(infile_path)
	os.unlink(callback_path)
	# generate_async_chart(current_app,imgfilename)
	return imgfilename
#########################################################################################
####1111111111111111111111111111111111111111111111111111111111111111111111111############
#########################################################################################





def str_2_seconds(strtime):
	format = '%m/%d/%Y %I:%M:%S %p'
	return int(time.mktime(time.strptime(strtime,format)))


#######################################################################################
#####3333333333333333333333333333333333333333333333333333333333333333333333############
#######################################################################################
# series config #
# w and r should at least one exist #
def mass_save_series(series,w,r):
	if ( w == None and r == None) or (w != None and r != None):
		raise MonitorException('save series failed for args error in w and r')
	for sindex in range(len(series)):
		seriesname = series[sindex]['series_name']
		seriesindex = sindex
		area = series[sindex]['area_list']
		service = series[sindex]['service_list']
		host = series[sindex]['host_list']
		aws = series[sindex]['aws_list']
		it = Itemtype.query.filter_by(itemtypeid = series[sindex]['series_type']).first()
		s = Series(seriesname,seriesindex,area,service,host,aws,it,w,r)
		db.session.add(s)
		item_arr = series[sindex]['series_item_list']
		# for itemid in item_arr:
		# 	i = Item.query.filter_by(itemid=itemid).first()
		# 	tmp = s.add_item(i)
		# 	if tmp != None:
		# 		db.session.add(tmp)


def mass_update_series(series,w,r):
	if ( w == None and r == None) or (w != None and r != None):
		raise MonitorException('update series failed for args error in w and r')
	if w != None:
		for s in w.window_series:
			db.session.delete(s)
		db.session.add(w)

	if r != None:
		for s in r.report_series:
			db.session.delete(s)
		db.session.add(r)

	mass_save_series(series,w,r)

# series config #
#######################################################################################
###3333333333333333333333333333333333333333333333333333333333333333333333333333########
#######################################################################################

##############################################################################################
###44444444444444444444444444444444444444444444444444444444444444444444444444444##############
##############################################################################################
### report save and delete ##########

def	save_report(reportname,seriesinfo,scaletype,functiontype,owner,title,discription):
	# s_s = str_2_seconds(timesince)
	# t_s = str_2_seconds(timetill)

	if owner.reports.filter_by(reportname=reportname).count() > 0:
		raise MonitorException('reportname for this user is already exist')

	scaletype = int(scaletype)
	functiontype = int(functiontype)

	# if s_s + scaletype > t_s:
	# 	return 0
	# print seriesinfo
	series_info = json.loads(seriesinfo)
	series = series_info['current_series_info']

	r = Report(scaletype,functiontype,reportname,owner,title,discription)

	db.session.add(r)

	index = 0
	# print "series",series
	for si in series:
		area_list = si['area_list']
		service_list = si['service_list']
		host_list = si['host_list']
		aws_list = si['aws_list']
		series_type = si['series_type']
		series_name = si['series_name']
		# print "itemtypename",series_type
		itemtype = Itemtype.query.filter_by(itemtypeid = series_type).first()
		# print itemtype
		s = Series(series_name,index,area_list,service_list,host_list,aws_list,itemtype,None,r)

		item_arr = si['series_item_list']

		db.session.add(s)

		# for i in item_arr:
		# 	item = Item.query.filter_by(itemid = i).first()
		# 	tmp = s.add_item(item)
		# 	if tmp != None:
		# 		db.session.add(tmp)

		index += 1

	# db.session.commit()

### report save and delete ##########
##############################################################################################
####44444444444444444444444444444444444444444444444444444444444444444444444444444#############
##############################################################################################


#################################################################################################
#################################################################################################
#################################################################################################
##### emailschedule save and delete ##############

# def gen_es_cron(frequency,start_time,esid,timezone):
# 	days = int(frequency)/(3600*24)
# 	h_m = start_time.split(':')
# 	command = os.getcwd() + '/generate_report.py ' + str(esid)
# 	new_crontab_time = str(h_m[1]) + ' ' + str(( int(h_m[0]) + 24 - int(timezone) ) % 24) + ' */' + str(days) + ' * * ' + command + '\n'
# 	return new_crontab_time


def gen_new_cron_time(frequency,start_time,timezone):

	# print frequency,start_time
	days = int(frequency)/(3600*24)
	h_m = start_time.split(':')
	new_crontab_time = str(h_m[1]) + ' ' + str(( int(h_m[0]) + 24 - int(timezone) ) % 24) + ' */' + str(days) + ' * *'
	return new_crontab_time

# def update_cron_job(eses):
# 	try:
# 		output = open('new.cron','w')
# 		# print "output"
# 		for es in eses:
# 			new_crontab = gen_new_cron(es.frequency,es.starttime,es.emailscheduleid,es.timezone)
# 			output.write(new_crontab)
# 		if len(eses) == 0:
# 			output.write('')

# 	except Exception, e:
# 		raise MonitorException('write crontab job file failed')
# 	finally:
# 		output.close()

# 	try:
# 		call(['crontab','new.cron'])
# 	except Exception, e:
# 		raise MonitorException(' call crontab command failed ')

def add_specific_cron(es):
	try:
		command = GENERATE_REPORT_PATH + str(es.emailscheduleid)
		new_crontab_time = gen_new_cron_time(es.frequency,es.starttime,es.timezone)
		cron = CronTab()
		job = cron.new(command)
		job.setall(new_crontab_time)
		cron.write()
	except Exception, e:
		raise Exception('install new crontab failed ' + str(e))

def delete_specific_cron(es):
	try:
		command = GENERATE_REPORT_PATH + str(es.emailscheduleid)
		cron = CronTab()
		iter_cron = cron.find_command(command)
		cron.remove(iter_cron.next())
		cron.write()
	except Exception, e:
		raise Exception('install new crontab failed ' + str(e))

@async
def update_schedule_data_2_s3():
	try:
		con = S3Connection()
		bucket = con.get_bucket(S3_MONITOR_BUCKET_NAME)
		schedule_data_file = bucket.get_key(S3_MONITOR_SCHEDULE_FOLDER + S3_MONITOR_SHEDULE_ALL_FILENAME)
		if schedule_data_file == None:
			schedule_data_file = bucket.new_key(S3_MONITOR_SCHEDULE_FOLDER + S3_MONITOR_SHEDULE_ALL_FILENAME)
		all_es = Emailschedule.query.all()
		result = []
		for es in all_es:
			report_info = []
			result.append({'starttime':es.starttime,'frequency':es.frequency,'esid':es.emailscheduleid,'timezone':es.timezone})

		result_str = json.dumps(result)
		
		schedule_data_file.set_contents_from_string(result_str)
		schedule_data_file.make_public()
	except Exception, e:
		con = S3Connection()
		bucket = con.get_bucket(S3_BUCKET_NAME)
		schedule_data_file = bucket.get_key(S3_SCHEDULE_FOLDER+SCHEDULE_ALL_FILENAME)
		all_es = Emailschedule.query.all()
		result = []
		for es in all_es:
			report_info = []
			result.append({'starttime':es.starttime,'frequency':es.frequency,'esid':es.emailscheduleid,'timezone':es.timezone})

		result_str = json.dumps(result)
		schedule_data_file.set_contents_from_string(result_str)
		schedule_data_file.make_public()


def save_emailschedule(subject,reportids,email,frequency,start_time,owner,timezone):


	es = Emailschedule(subject,frequency,start_time,owner,timezone)
	db.session.add(es)
	for rid in reportids['report_id_list']:
		r = Report.query.filter_by(reportid=rid).first()
		tr = es.add_report(r)
		if tr != None:
			db.session.add(tr)

	for e in email:
		rv = Receiver.query.filter_by(mailaddress=e).first()
		if rv == None:
			rv = Receiver(e)
			db.session.add(rv)
		trv = es.add_receiver(rv)
		if trv != None:
			db.session.add(trv)

	return es
	

def delete_schedule(esid):
	es = Emailschedule.query.filter_by(emailscheduleid=esid).first()
	if es == None:
		raise MonitorException('schedule do not exist')
	db.session.delete(es)
	delete_specific_cron(es)

##### emailschedule save and delete ##############
#################################################################################################
#################################################################################################
#################################################################################################

###########################################################################################
###########################################################################################
###########################################################################################
# window chart save, delete, update #
def save_window_chart(wc_name,series,owner,wc_type=0,window_index=0,page=None):
	w = Window(wc_name,wc_type,window_index,owner,page)
	db.session.add(w)

	mass_save_series(series,w,None)
	return w

## window chart for this user is already exist ##
def update_window_chart(wc_name,current_series,user):
	w = user.windows.filter_by(type=0,windowname=wc_name).first()
	mass_update_series(current_series,w,None)
	return None

def delete_window(windowid):
	window = Window.query.filter_by(windowid=windowid).first()
	if window == None:
		raise Exception('window to be delete do not exist')

	ws = window.window_series.all()

	for s in ws:
		db.session.delete(s)

	db.session.delete(window)

###########################################################################################
###########################################################################################
###########################################################################################


####################################################################################
####################################################################################
####################################################################################
# page config
def save_page_chart(pagename,series_info,user):

	page = Page(pagename,user)
	db.session.add(page)

	for i in range(len(series_info)):
		if len(series_info[i]) > 0 :
			wc_name = pagename + str(i)
			series = series_info[i]
			wc_type = 1
			window_index = i
			save_window_chart(wc_name,series,user,wc_type,window_index,page)
	return page

def update_page_chart(pagename,series_info,user):

	page = user.pages.filter_by(pagename=pagename).first()

	for w in page.windows:
		for s in w.window_series:
			db.session.delete(s)
		db.session.delete(w)
	
	for i in range(len(series_info)):
		if len(series_info[i]) > 0 :
			wc_name = pagename + str(i)
			series = series_info[i]
			wc_type = 1
			window_index = i
			save_window_chart(wc_name,series,user,wc_type,window_index,page)
	return page

def delete_page(pageid):
	page = Page.query.filter_by(pageid=pageid).first()

	if page == None:
		raise Exception('page to be deleted do not exist')

	windows = page.windows.all()

	for w in windows:
		delete_window(w.windowid)

	db.session.delete(page)
# page config
####################################################################################
####################################################################################
####################################################################################


##############################################################################################
##############################################################################################
##############################################################################################
# history data process
def init_series_data(init_data,data,s_s,t_s,time_frequency,functiontype):
		from_t = s_s/time_frequency*time_frequency
		to_t = t_s/time_frequency*time_frequency
		data_index = 0;

		origin = from_t

		last_value = None

		while from_t < to_t:
			if data_index < len(data) and from_t > data[data_index][4]:
				last_value = data[data_index][functiontype]
				data_index += 1
				continue

			if data_index < len(data) and from_t == data[data_index][4]:
				tmp = from_t
				arr = []
				arr.append(int(tmp*1000))
				arr.append(data[data_index][functiontype])
				init_data.append(arr)
				last_value = data[data_index][functiontype]
				data_index += 1
			else:
				tmp = from_t
				arr = []
				arr.append(int(tmp*1000))
				arr.append(last_value)
				init_data.append(arr)

			from_t += time_frequency


		# while from_t < to_t:

		# 	if data_index < len(data) and from_t > data[data_index][4]:
		# 		data_index += 1
		# 		continue

		# 	if data_index < len(data) and from_t == data[data_index][4]:
		# 		tmp = from_t
		# 		arr = []
		# 		arr.append(int(tmp*1000))
		# 		arr.append(data[data_index][functiontype])
		# 		init_data.append(arr)
		# 		data_index += 1
		# 	else:
		# 		tmp = from_t
		# 		arr = []
		# 		arr.append(int(tmp*1000))
		# 		arr.append(None)
		# 		init_data.append(arr)

		# 	from_t += time_frequency

def update_series_data(update_data,data,s_s,functiontype):

	data_index = 0;

	update_data.append(s_s*1000)
	if len(data) > 0 :
		update_data.append(data[0][functiontype])
	else:
		update_data.append(None)

def report_series_result(current_series_info,time_frequency,time_since,time_till,functiontype):
	s_s = time_since
	t_s = time_till
	
	result = []
	if s_s + int(time_frequency) > t_s:
		return result

	ground = int(time_frequency)

	for series in current_series_info:
		item_list = series['series_item_list']
		# print "item_list",item_list
		
		data_result = update_history_data(item_list,t_s,s_s,ground)
		# print data_result
		name = str(series['series_name'])
		init_data = []
		init_series_data(init_data,data_result,s_s,t_s,ground,functiontype)
		tmp = {'data':init_data,'name':name}
		result.append(tmp)

	return result

def get_init_y_title(current_series_info):
	y_title = []
	for series in current_series_info:
		ittypeid = series['series_type']
		giyt_it = Itemtype.query.filter_by(itemtypeid = ittypeid).first()
		unitname = giyt_it.itemunit
		if not unitname in y_title:
			y_title.append(unitname)

	return ','.join(y_title)


def init_result(current_series_info,time_frequency):

	result = []
	t_s = int(time.time())
	s_s = t_s - CHART_INIT_TIME
	ground = int(time_frequency)

	for series in current_series_info:
		item_list = series['series_item_list']	
		itemtypeid = series['series_type']
		# it = Itemtype.query.filter_by(itemtypeid=itemtypeid).first()
		# ground = int(it.time_frequency)
		data_result = init_history_data(item_list,ground,s_s,t_s)
		name = str(series['series_name'])
		init_data = []
		init_series_data(init_data,data_result,s_s,t_s,ground,1)
		tmp = {'data':init_data,'name':name}
		result.append(tmp)
	return result

def series_interval_result(item_list,s_s,t_s,ground):

	steps = (t_s - s_s)/(ground*DESIRED_DISPLAY_POINTS)

	if steps < 1:
		steps = 1

	ground = ground * steps

	history_result = Zabbixhistory.get_interval_history(item_list,ground,s_s,t_s)
	historyuint_result =Zabbixhistoryuint.get_interval_history(item_list,ground,s_s,t_s)
	query_result = []
	if history_result == None:
		query_result = historyuint_result
	else:
		query_result = history_result

	if query_result == None:
		query_result = []

	g_s = s_s / ground
	g_t = t_s / ground

	index = g_s

	result = []

	for row in query_result:
		while index < int(row[4]) or index == int(query_result[len(query_result)-1][4]):
			time = index * ground * SECOND_TO_MILLI
			arr = [time,None]
			result.append(arr)
			index += 1

		if index == int(row[4]):
			time = int(row[4]) * ground * SECOND_TO_MILLI
			count = int(row[0])
			avg = float(row[1])
			maxv = float(row[2])
			minv = float(row[3])
			arr = [time,avg]
			result.append(arr)
			index += 1

	while index <= (g_t + 1) :
		time = index * ground * SECOND_TO_MILLI
		arr = [time,None]
		result.append(arr)
		index += 1

	return result

def interval_result(current_series_info,t_s,s_s,time_frequency):
	result = []

	for series in current_series_info:
		item_list = series['series_item_list']
		# ground = Itemtype.query.filter_by(itemtypeid=series['series_type']).first().time_frequency
		ground = time_frequency
		data_result = series_interval_result(item_list,s_s,t_s,int(ground))
		name = str(series['series_name'])
		tmp = {'data':data_result,'name':name}
		result.append(tmp)
	return result

def history_result(current_series_info,time_frequency):
	result = []
	t_s = int(time.time())
	s_s = t_s - CHART_HISTORY_TIME

	# print "t_s,s_s",t_s,s_s

	return interval_result(current_series_info,t_s,s_s,time_frequency)


def update_result(series_info,time_frequency,time_till):

	result = []
	ground = int(time_frequency)
	t_s = int(time.time())/ground*ground

	s_s = t_s - ground

	for c in series_info:
		cdata = []
		for series in c:
			if not series.has_key('series_item_list'):
				continue
			item_list = series['series_item_list']
			data_result = update_history_data(item_list,t_s,s_s,ground)
			update_data = []
			update_series_data(update_data,data_result,s_s,1)
			cdata.append(update_data)

		result.append(cdata)

	return result


def arg_2_array(arg=''):
	result = []

	if len(arg) > 0:
		if '@' in arg:
			result = arg.split('@')
		else:
				result.append(arg)
	return result


def index_arg_2_array(area='',service='',host='',aws=''):
	area_arr = []
	service_arr = []
	host_arr = []
	aws_arr = []
	result = {'area':area_arr,'service':service_arr,'host':host_arr,'aws':aws_arr}

	arg_id_map = {0:area,1:service,2:host,3:aws}
	arr_id_map = {0:area_arr,1:service_arr,2:host_arr,3:aws_arr}
	name_id_map = {0:'area',1:'service',2:'host',3:'aws'}

	for i in arg_id_map:
		result[name_id_map[i]] = arg_2_array(arg_id_map[i])

	return result

def init_history_data(item_arr=[],ground = 60,time_since=0,time_till=60):

	engine = ''

	history_result = Zabbixhistory.get_interval_history(item_arr,ground,time_since,time_till)
	historyuint_result =Zabbixhistoryuint.get_interval_history(item_arr,ground,time_since,time_till)
	query_result = []
	if history_result == None:
		query_result = historyuint_result
	else:
		query_result = history_result

	if query_result == None:
		query_result = []

	result = []

	for row in query_result:
		count = int(row[0])
		avg = float(row[1])
		maxv = float(row[2])
		minv = float(row[3])
		index = row[4] * ground
		arr = [count,avg,maxv,minv,index]
		result.append(arr)
	return result

def update_history_data(item_arr=[],time_till=60,time_since=0,ground=60):

	engine = ''

	history_result = Zabbixhistory.get_interval_history(item_arr,ground,time_since,time_till)
	historyuint_result =Zabbixhistoryuint.get_interval_history(item_arr,ground,time_since,time_till)
	query_result = []
	if history_result == None:
		query_result = historyuint_result
	else:
		query_result = history_result

	if query_result == None:
		query_result = []

	result = []

	for row in query_result:
		count = int(row[0])
		avg = float(row[1])
		maxv = float(row[2])
		minv = float(row[3])
		index = row[4] * ground
		arr = [count,avg,maxv,minv,index]
		result.append(arr)
	return result

def get_series_info(series):

	result = {}
	for s in series:
		tmp = {}
		tmp['area_list'] = s.area_id
		tmp['service_list'] = s.service_id
		tmp['aws_list'] = s.aws_id
		tmp['series_type'] = s.itemtype.itemtypeid
		tmp['series_name'] = s.seriesname
		tmp['host_list'] = s.host_id

		tmp['time_frequency'] = s.itemtype.time_frequency

		indexes = index_arg_2_array(s.area_id,s.service_id,s.host_id,s.aws_id)
		all_itemtypes = get_all_itemtypes(indexes['area'],indexes['service'],indexes['host'],indexes['aws'])
		print "all_itemtypes",all_itemtypes
		if all_itemtypes['itemtype'].has_key(s.itemtype.itemtypeid):
			tmp['series_item_list'] = all_itemtypes['itemtype'][s.itemtype.itemtypeid]['items']
		# items = s.items
		# item_arr = []
		# for i in items:
		# 	item_arr.append(str(i.itemid))
		# tmp['series_item_list'] = item_arr
		result[s.index] = tmp

	return result
# history data process
##############################################################################################
##############################################################################################
##############################################################################################









def upload_img_to_s3(filename):
	try:
		imgfile = file(REPORT_OUTPUT_DIR + filename,'r')
		con = S3Connection()
		bucket = con.get_bucket(S3_MONITOR_BUCKET_NAME)
		key = bucket.new_key(S3_MONITOR_REPORT_FOLDER + filename)
		key.set_contents_from_file(imgfile)
		imgfile.close()
		key.make_public()
	except Exception, e:
		try:
			imgfile = file(REPORT_OUTPUT_DIR + filename,'r')
			con = S3Connection()
			bucket = con.get_bucket(S3_BUCKET_NAME)
			key = bucket.new_key(S3_BUCKET_FOLDER+filename)
			key.set_contents_from_file(imgfile)
			imgfile.close()
			key.make_public()
		except Exception, e:
			pass
		
	


def update_specific_schedule_data_2_s3(esid):
	try:
		con = S3Connection()
		bucket = con.get_bucket(S3_MONITOR_BUCKET_NAME)
		schedule_data_file = bucket.get_key(S3_MONITOR_SCHEDULE_FOLDER+str(esid))
		if schedule_data_file == None:
			schedule_data_file = bucket.new_key(S3_MONITOR_SCHEDULE_FOLDER+str(esid))

		es = Emailschedule.query.filter_by(emailscheduleid=esid).first()
		result = {}
		report_info = []
		day = datetime.today()
		daytime = day.strftime("%Y%m%d")
		for r in es.reports:
			img = r.imgs.filter_by(es=es,daytime=daytime).first()
			if img == None:
				raise MonitorException('img did not generate')
			imgname = img.reportimgname
			tmp = {'imgname':imgname,'title':r.title,'discription':r.discription}
			report_info.append(tmp)

		rvs = es.receivers
		rvaddress = []
		for rv in rvs:
			rvaddress.append(rv.mailaddress)
		subject = es.subject

		result = {'reports':report_info,'rvaddress':rvaddress,'subject':subject,'starttime':es.starttime,'frequency':es.frequency}
		result_str = json.dumps(result)
		schedule_data_file.set_contents_from_string(result_str)
		schedule_data_file.make_public()
	except Exception, e:
		try:
			con = S3Connection()
			bucket = con.get_bucket(S3_BUCKET_NAME)
			schedule_data_file = bucket.get_key(S3_SCHEDULE_FOLDER+str(esid))
			if schedule_data_file == None:
				schedule_data_file = bucket.new_key(S3_SCHEDULE_FOLDER+str(esid))

			es = Emailschedule.query.filter_by(emailscheduleid=esid).first()
			result = {}
			report_info = []
			day = datetime.today()
			daytime = day.strftime("%Y%m%d")
			for r in es.reports:
				img = r.imgs.filter_by(es=es,daytime=daytime).first()
				if img == None:
					raise MonitorException('img did not generate')
				imgname = img.reportimgname
				tmp = {'imgname':imgname,'title':r.title,'discription':r.discription}
				report_info.append(tmp)

			rvs = es.receivers
			rvaddress = []
			for rv in rvs:
				rvaddress.append(rv.mailaddress)
			subject = es.subject

			result = {'reports':report_info,'rvaddress':rvaddress,'subject':subject,'starttime':es.starttime,'frequency':es.frequency}
			result_str = json.dumps(result)
			schedule_data_file.set_contents_from_string(result_str)
			schedule_data_file.make_public()
		except Exception, e:
			pass
		


@async
def async_gen_report_img(emailscheduleid):
	es = Emailschedule.query.filter_by(emailscheduleid=emailscheduleid).first()
	day = datetime.today()
	daytime = day.strftime("%Y%m%d")
	
	try:
		print '''... Generate report at server ing....'''
		for r in es.reports:
			time_till = int(time.mktime(day.timetuple()))
			time_since = time_till - es.frequency
			postfix = daytime + construct_random_str()
			img = generate_report(r,postfix,time_since,time_till)
			ri = Reportimg(img,daytime,r,es)
			db.session.add(ri)
			upload_img_to_s3(img)
			# async_upload_img_to_s3(current_app,img)
		db.session.commit()
		update_specific_schedule_data_2_s3(emailscheduleid)
	except Exception, e:
		db.session.rollback()
		raise MonitorException('generate img or save img info failed'+str(e))
	finally:
		db.session.remove()

def gen_upload_report_img(emailscheduleid):
	async_gen_report_img(emailscheduleid)

def send_schedule_data():
	all_es = Emailschedule.query.all()
	result = []
	for es in all_es:
		report_info = []
		result.append({'starttime':es.starttime,'frequency':es.frequency,'esid':es.emailscheduleid,'timezone':es.timezone})

	return json.dumps(result)


## es is already exist ##
## img for es's reports has already generated ##
def send_specific_schedule(esid):
	es = Emailschedule.query.filter_by(emailscheduleid=esid).first()
	result = {}
	report_info = []
	day = datetime.today()
	daytime = day.strftime("%Y%m%d")
	for r in es.reports:
		img = r.imgs.filter_by(es=es,daytime=daytime).first()
		if img == None:
			raise MonitorException('img did not generate')
		imgname = img.reportimgname
		tmp = {'imgname':imgname,'title':r.title,'discription':r.discription}
		report_info.append(tmp)

	rvs = es.receivers
	rvaddress = []
	for rv in rvs:
		rvaddress.append(rv.mailaddress)
	subject = es.subject

	result = {'reports':report_info,'rvaddress':rvaddress,'subject':subject,'starttime':es.starttime,'frequency':es.frequency}
	return json.dumps(result)


def result_for_index():
	area = Area.query.all()
	service = Service.query.all()
	service_result = []
	for s in service:
		tmp = {}
		tmp['service'] = s
		host_arr = []
		for h in s.hosts.all():
			h_info = {}
			h_info['hostname'] = h.hostname
			h_info['hostid'] = h.hostid
			zh = Zabbixhosts.query.get(h.hostid)
			if zh == None:
				h_info['available'] = None
			else:
				h_info['available'] = zh.available
			host_arr.append(h_info)
		tmp['host'] = host_arr
		service_result.append(tmp)
	host = Host.query.all()
	aws = Aws.query.all()
	return {'area':area,'service':service_result,'host':host,'aws':aws}












