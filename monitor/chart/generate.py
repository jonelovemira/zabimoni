from monitor.chart.models import Report,Selectedmetrics,Option,Displaytable,Displaytablerow,Attr,\
								Emailschedule,Receiver,Reportimg
from monitor.zabbix.models import Zabbixhistory,Zabbixhistoryuint
from monitor import db
from crontab import CronTab
import os,json,time

from subprocess import call

from monitor.item.models import Aws

from config import BY_GROUP_RESULT,PER_INSTANCE_RESULT,BY_GROUP_TABLE_HEAD,PER_INSTANCE_TABLE_HEAD,\
					FUNC_TYPE_COUNT,FUNC_TYPE_AVG,FUNC_TYPE_MAX,FUNC_TYPE_MIN,FUNC_TYPE_SUM,\
					AWS_FEE_TABEL_HEAD,PHANTOMJS,HIGHCHART_CONVERT,REPORT_OUTPUT_DIR,\
					REPORT_OUTPUT_WIDTH,REPORT_OUTPUT_TYPE,REPORT_OUTPUT_SCALE,GENERATE_REPORT_PATH,\
					S3_MONITOR_BUCKET_NAME,S3_MONITOR_SCHEDULE_FOLDER,S3_MONITOR_SHEDULE_ALL_FILENAME,\
					S3_BUCKET_NAME,S3_SCHEDULE_FOLDER,SCHEDULE_ALL_FILENAME,S3_MONITOR_REPORT_FOLDER,\
					S3_BUCKET_FOLDER

from monitor.chart.displaychart import Chart
from monitor.decorators import async
from boto.s3.connection import S3Connection
from datetime import datetime
from monitor.chart.functions import construct_random_str

head_grouptype_map = {
	BY_GROUP_RESULT:BY_GROUP_TABLE_HEAD,
	PER_INSTANCE_RESULT:PER_INSTANCE_TABLE_HEAD
}


class generate_report():

	@classmethod
	def save_report(cls,reportname,selected_metrics,scaletype,functiontype,owner,title,description):

		for aws in Aws.query.all():
			head_grouptype_map[aws.awsname] = AWS_FEE_TABEL_HEAD

		tmp_report = owner.reports.filter_by(reportname=reportname).first()

		if tmp_report != None:
			raise Exception('same name for saving is already exists')

		report = Report(scaletype,functiontype,reportname,owner,title,description)

		db.session.add(report)

		sm = Selectedmetrics(None,report)

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

		return report

	@classmethod
	def delete_report(cls,reportid):

		report = Report.query.get(reportid)
		if report == None:
			raise Exception('report do not exist')

		selectedmetrics = report.selectedmetrics.first()

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

		db.session.delete(report)

	@classmethod
	def generate_report_series_data(cls,report,time_since,time_till):

		if report == None:
			raise Exception('report do not exist')

		ground = int(report.scaletype)
		function_type = int(report.functiontype)

		shared_yaxis = True

		load_report_result = cls.load_report(report.reportid)

		row_result = Chart.selected_metrics_2_metric_content(load_report_result['selected_metrics'])

		series_result = Chart.interval_init_result(time_since,time_till,ground,function_type,row_result,shared_yaxis)

		return series_result

	@classmethod
	def generate_report_y_title(cls,series_data):

		y_title = []
		for series in series_data:
			y_title.append(series['unit_name'])

		return ','.join(y_title)

	@classmethod
	def create_report_chart_json(cls,series_data_str,reportname,y_title):
		tmp_series_data = '''[{'data': [[1423453200000, 17352.0]], 'name': '192.168.1.101'}]'''

		tmp = '''{

			rangeSelector : {
                        // selected : 1,
                        inputEnabled: true
            },
            title : {
            	text : ''' + "'" + reportname + "'" + '''
            },

			series:''' + series_data_str + ''' 


		}'''
		return tmp

	@classmethod
	def generate_infile(cls,save_json,imgname):
		infile_path = '/tmp/' + imgname + '.json'
		f = open(infile_path,'w')
		f.write(save_json)
		f.close()
		return infile_path

	@classmethod
	def generate_callback_js(cls,imgname):
		callback_str = '''function(chart) {}'''
		callback_path = '/tmp/' + imgname + '.js'
		f = open(callback_path,'w')
		f.write(callback_str)
		f.close()
		return callback_path

	@classmethod
	def generate_png_chart(cls,chartname,infile_path,callback_path):
		call([PHANTOMJS,HIGHCHART_CONVERT,"-infile",infile_path,"-callback",callback_path,\
		"-outfile",REPORT_OUTPUT_DIR + chartname, "-width",REPORT_OUTPUT_WIDTH,\
		"-constr",REPORT_OUTPUT_TYPE,"-scale",REPORT_OUTPUT_SCALE])




	@classmethod
	def generate(cls,r,postfix,time_since,time_till):

		imgfilename = r.owner.username + '_' + r.reportname + '_' + postfix + '.png'
		series_data = cls.generate_report_series_data(r,time_since,time_till)
		tmp_series_data_str = str(series_data)
		tmp_series_data_str = tmp_series_data_str.replace('None','null')
		y_title = cls.generate_report_y_title(series_data)
		print y_title
		chart_json = cls.create_report_chart_json(tmp_series_data_str,r.reportname,y_title)
		infile_path = cls.generate_infile(chart_json,imgfilename)
		callback_path = cls.generate_callback_js(imgfilename)
		cls.generate_png_chart(imgfilename,infile_path,callback_path)
		os.unlink(infile_path)
		os.unlink(callback_path)
		# generate_async_chart(current_app,imgfilename)
		return imgfilename

	@classmethod
	def load_report(cls,reportid):

		for aws in Aws.query.all():
			head_grouptype_map[aws.awsname] = AWS_FEE_TABEL_HEAD


		result = {}

		report = Report.query.get(reportid)

		if report == None:
			raise Exception('report do not exist')

		selected_metrics = {}
		selectedmetrics = report.selectedmetrics.first()

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

						selected_metrics[option.optionname][dt.displaytablename]['metric_result'].append(tmp_arr)


		result['selected_metrics'] = selected_metrics

		return result


class generate_schedule():

	@classmethod
	def save_schedule(cls,subject,reportids,email,frequency,start_time,owner,timezone):
		es = Emailschedule(subject,frequency,start_time,owner,timezone)
		db.session.add(es)
		for rid in reportids['report_id_list']:
			r = Report.query.filter_by(reportid=rid).first()
			if r is None:
				raise 'report do not exist : ' + rid
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

	@classmethod
	def gen_new_cron_time(cls,frequency,start_time,timezone):

		# print frequency,start_time
		days = int(frequency)/(3600*24)
		h_m = start_time.split(':')
		new_crontab_time = str(h_m[1]) + ' ' + str(( int(h_m[0]) + 24 - int(timezone) ) % 24) + ' */' + str(days) + ' * *'
		return new_crontab_time

	@classmethod
	def add_specific_cron(cls,es):
		try:
			command = GENERATE_REPORT_PATH + str(es.emailscheduleid)
			new_crontab_time = cls.gen_new_cron_time(es.frequency,es.starttime,es.timezone)
			cron = CronTab()
			job = cron.new(command)
			job.setall(new_crontab_time)
			cron.write()
		except Exception, e:
			raise Exception('install new crontab failed ' + str(e))

	@classmethod
	@async
	def update_schedule_data_2_s3(cls):
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

	@classmethod
	def delete_schedule(cls,es):
		if es == None:
			raise MonitorException('schedule do not exist')
		db.session.delete(es)
		# delete_specific_cron(es)

	@classmethod
	def delete_specific_cron(cls,es):

		try:
			command = GENERATE_REPORT_PATH + str(es.emailscheduleid)
			cron = CronTab()
			iter_cron = cron.find_command(command)
			cron.remove(iter_cron.next())
			cron.write()
		except Exception, e:
			raise Exception('install new crontab failed ' + str(e))


	@classmethod
	@async
	def gen_upload_report_img(cls,emailscheduleid):
		es = Emailschedule.query.get(emailscheduleid)
		day = datetime.today()
		daytime = day.strftime("%Y%m%d")
		
		try:
			print '''... Generate report at server ing....'''
			for r in es.reports.all():
				time_till = int(time.mktime(day.timetuple()))
				time_since = time_till - es.frequency
				postfix = daytime + construct_random_str()
				img = generate_report.generate(r,postfix,time_since,time_till)
				ri = Reportimg(img,daytime,r,es)
				db.session.add(ri)
				cls.upload_img_to_s3(img)
				# async_upload_img_to_s3(current_app,img)
			db.session.commit()
			cls.update_specific_schedule_data_2_s3(emailscheduleid)
		except Exception, e:
			import traceback,sys
			traceback.print_exc(file=sys.stdout)
			db.session.rollback()
			raise Exception('generate img or save img info failed '+str(e))
		finally:
			db.session.remove()

	@classmethod
	def upload_img_to_s3(cls,filename):
		try:
			imgfile = file(REPORT_OUTPUT_DIR + filename,'r')
			con = S3Connection()
			bucket = con.get_bucket(S3_MONITOR_BUCKET_NAME)
			key = bucket.new_key(S3_MONITOR_REPORT_FOLDER + filename)
			key.set_contents_from_file(imgfile)
			imgfile.close()
			key.make_public()
		except Exception, e:
			imgfile = file(REPORT_OUTPUT_DIR + filename,'r')
			con = S3Connection()
			bucket = con.get_bucket(S3_BUCKET_NAME)
			key = bucket.new_key(S3_BUCKET_FOLDER+filename)
			key.set_contents_from_file(imgfile)
			imgfile.close()
			key.make_public()

	@classmethod
	def update_specific_schedule_data_2_s3(cls,esid):
		try:
			con = S3Connection()
			bucket = con.get_bucket(S3_MONITOR_BUCKET_NAME)
			schedule_data_file = bucket.get_key(S3_MONITOR_SCHEDULE_FOLDER+str(esid))
			if schedule_data_file == None:
				schedule_data_file = bucket.new_key(S3_MONITOR_SCHEDULE_FOLDER+str(esid))

			es = Emailschedule.query.get(esid)
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
				
			con = S3Connection()
			bucket = con.get_bucket(S3_BUCKET_NAME)
			schedule_data_file = bucket.get_key(S3_SCHEDULE_FOLDER+str(esid))
			if schedule_data_file == None:
				schedule_data_file = bucket.new_key(S3_SCHEDULE_FOLDER+str(esid))

			es = Emailschedule.query.get(esid)
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

			
				
			

	