# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for,\
                  send_from_directory
from flask.ext.login import login_required
from monitor import db,app
from monitor.item.models import Area,Service,Host,Aws,Itemtype,Item,Itemdatatype
from monitor.zabbix.models import Zabbixhosts
from monitor.chart.models import *
from monitor.chart.functions import *
from monitor.MonitorException import *

# from send_email import monitor_status_notification

import json,time

mod_chart = Blueprint('chart', __name__, url_prefix='/chart')

# Set the route and accepted methods
@mod_chart.route('/')
@login_required
def mainboard():
    return render_template("chart/main.html")

@mod_chart.route('/window/', methods=['GET', 'POST'])
@login_required
def window():
	index_result = {}
	index_result = result_for_index()
	idt = Itemdatatype.query.all()
	windows = g.user.windows.filter_by(type=0).all()
	return render_template("chart/window.html",title='Window',index_result=index_result,idt=idt,windows=windows)
	
@mod_chart.route('/window/delete/<windowid>', methods=['GET', 'POST'])
@login_required
def window_delete(windowid):
	try:
		delete_window(windowid)
		db.session.commit()
		return json.dumps(1)
	except Exception, e:
		db.session.rollback()
	finally:
		db.session.remove()

	return json.dumps(0)

@mod_chart.route('/page/', methods=['GET', 'POST'])
@login_required
def page():
	index_result = {}
	index_result = result_for_index()
	idt = Itemdatatype.query.all()
	pages = g.user.pages.all()
	return render_template("chart/page.html",title='Page',index_result=index_result,idt=idt,pages=pages)

@mod_chart.route('/page/delete/<pageid>', methods=['GET', 'POST'])
@login_required
def page_delete(pageid):
	try:
		delete_page(pageid)
		db.session.commit()
		return json.dumps(1)
	except Exception, e:
		db.session.rollback()
	finally:
		db.session.remove()

	return json.dumps(0)

@mod_chart.route('/report')
@login_required
def report():
	u = g.user
	emailschedule = u.schedules.all()
	report = u.reports.all()
	return render_template('chart/reportmain.html',title='Report',emailschedule=emailschedule,report=report)

@mod_chart.route('/addreport/', methods=['GET', 'POST'])
@login_required
def addreport():
	index_result = {}
	index_result = result_for_index()
	idt = Itemdatatype.query.all()
	if request.method == 'POST':
		reportname = request.form['reportname']
		seriesinfo = request.form['seriesinfo']
		scaletype = request.form['scaletype']
		functiontype = request.form['functiontype']
		title = request.form['title']
		discription = request.form['discription']
		owner = g.user
		try:
			save_report(reportname,seriesinfo,scaletype,functiontype,owner,title,discription)
			db.session.commit()
		except Exception, e:
			db.session.rollback()
			flash(str(e),'danger')
			return redirect(url_for('chart.addreport'))
		else:
			flash('you add a report','success')
			return redirect(url_for('chart.report'))
		finally:
			db.session.remove()

	return render_template('chart/report.html',title='report',index_result=index_result,idt=idt)

@mod_chart.route('/report/delete/<reportid>', methods=['GET', 'POST'])
@login_required
def reportdelete(reportid):
	try:
		r = Report.query.filter_by(reportid=reportid).first()
		db.session.delete(r)
		db.session.commit()
	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash(' you delete a report ','success')
	finally:
		db.session.remove()

	return redirect(url_for('chart.report'))

@mod_chart.route('/reportlist/', methods=['GET', 'POST'])
@login_required
def reportlist():
	user = g.user
	reports = user.reports
	result = []
	for r in reports:
		tmp = {}
		tmp['reportname'] = r.reportname
		tmp['reportid'] = r.reportid
		result.append(tmp)
	return json.dumps(result)

@mod_chart.route('/addschedule/', methods=['GET', 'POST'])
@login_required
def addschedule():
	if request.method == 'POST':
		f = request.form
		email = []
		for key in f.keys():
		    for value in f.getlist(key):
		    	if len(value) != 0:
					if key == 'email[]':
						email.append(value)
		reportids = json.loads(request.form['reportid'])
		subject = request.form['emailsubject']
		u = g.user
		period = request.form['period']
		start_time = request.form['timestart']
		timezone = request.form['timezone']
		try:
			es = save_emailschedule(subject,reportids,email,period,start_time,u,timezone)
			db.session.commit()
			add_specific_cron(es)
			update_schedule_data_2_s3()
		except Exception, e:
			db.session.rollback()
			flash(str(e),'danger')
		else:
			flash('Save email schedule successfully','success')
			return redirect(url_for('chart.report'))
		finally:
			db.session.remove()
		
		
	return render_template('chart/schedule.html',title='schedule')

@mod_chart.route('/schedule/delete/<emailscheduleid>', methods=['GET'])
@login_required
def scheduledelete(emailscheduleid):
	try:
		es = Emailschedule.query.filter_by(emailscheduleid=emailscheduleid).first()
		delete_schedule(emailscheduleid)
		db.session.commit()
		update_schedule_data_2_s3()
	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('you delete a schedule','success')
	finally:
		db.session.remove()

	return redirect(url_for('chart.report'))



@mod_chart.route('/itemtype/', methods=['GET', 'POST'])
@login_required
def itemtype():
	area = request.args.get('area')
	service = request.args.get('service')
	host = request.args.get('host')
	aws = request.args.get('aws')
	result = index_arg_2_array(area,service,host,aws)
	itemtype_result = get_all_itemtypes(result['area'],result['service'],result['host'],result['aws'])
	return json.dumps(itemtype_result)

@mod_chart.route('/history/',methods=['GET','POST'])
@login_required
def history():
	if request.method == 'POST':
		request_data = json.loads(request.data)
		current_series_info = request_data['current_series_info']
		time_frequency = request_data['time_frequency']
		for series in current_series_info:
			if current_series_info[0].has_key('series_item_list'):
				data_result = history_result(current_series_info,time_frequency)
				y_title = get_init_y_title(current_series_info)
				result = {'data':data_result,'y_title':y_title}
				return json.dumps(result)
	return json.dumps(0)

@mod_chart.route('/interval/',methods=['GET','POST'])
@login_required
def interval():
	if request.method == 'POST':
		request_data = json.loads(request.data)
		current_series_info = request_data['current_series_info']
		time_since = request_data['time_since']
		time_till = request_data['time_till']
		time_frequency = request_data['time_frequency']

		for series in current_series_info:
			if current_series_info[0].has_key('series_item_list'):
				data_result = interval_result(current_series_info,int(time_till),int(time_since),time_frequency)
				y_title = get_init_y_title(current_series_info)
				result = {'data':data_result,'y_title':y_title}
				return json.dumps(result)
	return json.dumps(0)

@mod_chart.route('/init/', methods=['GET', 'POST'])
@login_required
def init():
	sortId = 0
	if request.method == 'POST':
		request_data = json.loads(request.data)
		current_series_info = request_data['current_series_info']
		time_frequency = request_data['time_frequency']
		sortId = request_data['sortId']

		for series in current_series_info:
			if series.has_key('series_item_list'):
				data_result = init_result(current_series_info,time_frequency)
				y_title = get_init_y_title(current_series_info)
				result = {'data':data_result,'y_title':y_title,'sortId':sortId}
				return json.dumps(result)

		# if not current_series_info[0].has_key('series_item_list'):
		# 	return json.dumps(0)

		# data_result = init_result(current_series_info,time_frequency)
		# y_title = get_init_y_title(current_series_info)
		# result = {'data':data_result,'y_title':y_title}
		# return json.dumps(result)
	return json.dumps({'data':0,'sortId':sortId})

@mod_chart.route('/update/', methods=['GET', 'POST'])
@login_required
def update():
	result = []
	if request.method == 'POST':
		request_data = json.loads(request.data)
		series_info = request_data['series_info']
		time_frequency = request_data['time_frequency']
		time_till = request_data['time_till']
		result = update_result(series_info,time_frequency,time_till)
	return json.dumps(result)


@mod_chart.route('/save/window', methods=['GET', 'POST'])
@login_required
def save_window():
	if request.method == 'POST':
		request_data = json.loads(request.data)
		wc_name = request_data['wc_name']
		current_series = request_data['series']
		user = g.user
		try:
			result = None
			w = user.windows.filter_by(type=0,windowname=wc_name).first()
			if w != None:
				update_window_chart(wc_name,current_series,user)
			else:
				w = save_window_chart(wc_name,current_series,user)
				result = w

			db.session.commit()
		except Exception, e:
			db.session.rollback()
			raise MonitorException('save window failed ' + str(e))
		else:
			if result != None:
				return json.dumps({'id':result.windowid,'name':result.windowname})
		finally:
			db.session.remove()
	return json.dumps({})

@mod_chart.route('/save/page', methods=['GET', 'POST'])
@login_required
def save_page():

	if request.method == 'POST':
		request_data = json.loads(request.data)
		pagename = request_data['pagename']
		series_info = request_data['series_info']
		user = g.user
		try:
			result = None
			p = user.pages.filter_by(pagename=pagename).first()
			if p != None:
				update_page_chart(pagename,series_info,user)
			else:
				p = save_page_chart(pagename,series_info,user)
				result = p

			db.session.commit()
		except Exception, e:
			db.session.rollback()
			raise MonitorException('save page failed ' + str(e))
		else:
			if result != None:
				return json.dumps({'id':result.pageid,'name':result.pagename})
		finally:
			db.session.remove()

	return json.dumps({})




@mod_chart.route('/load/window', methods=['GET', 'POST'])
@login_required
def load_window():
	user = g.user
	windows = user.windows.filter_by(type=0).all()
	result = []
	for w in windows:
		tmp = {}
		tmp['id'] = w.windowid
		tmp['name'] = w.windowname
		result.append(tmp)

	return json.dumps(result)

@mod_chart.route('/load/pageinfo', methods=['GET', 'POST'])
@login_required
def load_pageinfo():
	user = g.user
	pageid = request.args.get('pageid')

	page = user.pages.filter_by(pageid = pageid).first()

	# print page

	result = {}
	series_info = []
	sortids = []
	for x in xrange(0,9):
		tmp = []
		series_info.append(tmp)

	if page != None:
		windows = page.windows.all()
		# print "windows",windows
		for w in windows:
			index = w.index
			sortids.append(index)
			seriescount = w.window_series.count()
			for x in xrange(0,seriescount):
				tmp = {}
				series_info[index].append(tmp)
			series = w.window_series.all()
			s_r = get_series_info(series)
			for s in s_r:
				series_info[index][s] = s_r[s]

		result['window_data'] = series_info
		result['sortids'] = sortids

	return json.dumps(result)


@mod_chart.route('/load/page', methods=['GET', 'POST'])
@login_required
def load_page():
	user = g.user
	pages = user.pages.all()
	result = []
	for p in pages:
		tmp = {}
		tmp['id'] = p.pageid
		tmp['name'] = p.pagename
		result.append(tmp)

	return json.dumps(result)

@mod_chart.route('/load/series', methods=['GET', 'POST'])
@login_required
def load_series():
	windowid = request.args.get('windowid')

	w = Window.query.filter_by(windowid = windowid).first()

	series = w.window_series.all()

	result = {}

	result = get_series_info(series)

	# print result[0]['series_item_list']

	return json.dumps(result)

@mod_chart.route('/report/init2/', methods=['POST'])
@login_required
def reportinit2():
	if request.method == 'POST':
		request_data = json.loads(request.data)
		current_series_info = request_data['current_series_info']
		time_frequency = request_data['time_frequency']
		time_since = int(time.time()) - 7200
		time_till = int(time.time())
		functiontype = request_data['functiontype']
		data_result = report_series_result(current_series_info,time_frequency,time_since,time_till,functiontype)
		result = {'time_since':time_since,'time_till':time_till,'data':data_result}
		return json.dumps(result)
	return json.dumps(0)


	
@mod_chart.route('/report/<path:reportimg>')
def getreportimg(reportimg):
	return app.send_static_file('report/' + reportimg)

@mod_chart.route('/report/generate/<emailscheduleid>')
def report_generate(emailscheduleid):
	try:
		gen_upload_report_img(emailscheduleid)
		return 'success'
	except Exception, e:
		return 'failed'

# @mod_chart.route('/schedule/data/')
# def all_schedule_data():
# 	return send_schedule_data()


# @mod_chart.route('/schedule/data/<esid>')
# def specific_schedule_data(esid):
# 	try:
# 		pass
# 	except Exception, e:
# 		raise e
# 	return send_specific_schedule(esid)

