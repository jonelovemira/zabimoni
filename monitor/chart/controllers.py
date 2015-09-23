# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for,\
                  send_from_directory
from flask.ext.login import login_required
from monitor import db,app
from monitor.item.models import Area,Service,Host,Aws,Itemtype,Item,Itemdatatype
from monitor.zabbix.models import Zabbixhosts
from monitor.chart.models import *
from monitor.MonitorException import *
from monitor.chart.search import *
from monitor.chart.displaychart import *
from monitor.chart.generate import *
from monitor.chart.overall import *

from flask.ext.principal import Permission, RoleNeed
admin_permission = Permission(RoleNeed('1')).union(Permission(RoleNeed('0')))

from config import WINDOW_CHART,CHART_INIT_DEFAULT_MESSAGE, IN_LOCAL


import json,time

mod_chart = Blueprint('chart', __name__, url_prefix='/chart')

@mod_chart.route('/')
@login_required
def mainboard():
    return render_template("chart/main.html")

@mod_chart.route('/window/', methods=['GET', 'POST'])
@login_required
def window():
	
	windows = g.user.windows.filter_by(type=WINDOW_CHART).all()
	services = Service.query.all()
	itemtypes = Itemtype.query.all()
	tmp_arr = []
	aws_tmp_arr = []
	for it in itemtypes:
		if it.aws == None:
			tmp_arr.append(it.itemtypename)
		else:
			item = it.items.first()
			aws_tmp_arr.append(item.itemname)
	itemtypenames = json.dumps(tmp_arr)
	aws_itemtypenames = json.dumps(aws_tmp_arr)
	return render_template("chart/window.html",title='Window',services=services,windows=windows,itemtypenames=itemtypenames,aws_itemtypenames=aws_itemtypenames)


@mod_chart.route('/page/', methods=['GET', 'POST'])
@login_required
def page():
	services = Service.query.all()
	pages = g.user.pages.all()
	windows = g.user.windows.filter_by(type=WINDOW_CHART).all()
	itemtypes = Itemtype.query.all()
	tmp_arr = []
	aws_tmp_arr = []
	for it in itemtypes:
		if it.aws == None:
			tmp_arr.append(it.itemtypename)
		else:
			item = it.items.first()
			aws_tmp_arr.append(item.itemname)
	itemtypenames = json.dumps(tmp_arr)
	aws_itemtypenames = json.dumps(aws_tmp_arr)
	return render_template("chart/page.html",title='Page',services=services,pages=pages,windows=windows,itemtypenames=itemtypenames,aws_itemtypenames=aws_itemtypenames)


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
	services = Service.query.all()

	itemtypes = Itemtype.query.all()
	tmp_arr = []
	aws_tmp_arr = []
	for it in itemtypes:
		if it.aws == None:
			tmp_arr.append(it.itemtypename)
		else:
			item = it.items.first()
			aws_tmp_arr.append(item.itemname)
	itemtypenames = json.dumps(tmp_arr)
	aws_itemtypenames = json.dumps(aws_tmp_arr)

	if request.method == 'POST':
		try:
			reportname = request.form['reportname']
			selectedmetrics = json.loads(request.form['selectedmetrics'])
			scaletype = request.form['scaletype']
			functiontype = request.form['functiontype']
			title = request.form['title']
			description = request.form['description']
			owner = g.user

			save_result = generate_report.save_report(reportname,selectedmetrics,scaletype,functiontype,owner,title,description)
			app.logger.info(g.user.username + ' add a report ' + reportname )
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

	return render_template('chart/report.html',title='report',services=services,itemtypenames=itemtypenames,aws_itemtypenames=aws_itemtypenames)

@mod_chart.route('/report/delete/<reportid>', methods=['GET', 'POST'])
@login_required
def reportdelete(reportid):
	try:
		# r = Report.query..get(reportid)
		generate_report.delete_report(reportid)
		app.logger.info(g.user.username + ' delete a report ' + reportid )

		# db.session.delete(r)
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
		try:
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
		
			es = generate_schedule.save_schedule(subject,reportids,email,period,start_time,u,timezone)
			db.session.commit()
			generate_schedule.add_specific_cron(es)
			all_es = Emailschedule.query.all()
			generate_schedule.update_schedule_data_2_s3(all_es)
			app.logger.info(g.user.username + ' save an email schedule ' )
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
		es = Emailschedule.query.get(emailscheduleid)
		generate_schedule.delete_schedule(es)
		db.session.commit()
		generate_schedule.delete_specific_cron(es)
		generate_schedule.update_schedule_data_2_s3()
		app.logger.info(g.user.username + ' delete an email schedule ' )
	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('you delete a schedule','success')
	finally:
		db.session.remove()

	return redirect(url_for('chart.report'))


@mod_chart.route('/init/', methods=['GET', 'POST'])
@login_required
def init():
	result = {}
	info = None
	init_result_bool = False
	init_result = None
	if request.method == 'POST':
		try:
			request_data = json.loads(request.data)
			selected_metrics = request_data['selected_metrics']
			chart_config = request_data['chart_config']

			item_list = Chart.smr_2_itemlist(selected_metrics)
			for itemid in item_list:
				item = Item.query.get(itemid)
				if item != None and item.itemtype.aws != None and not admin_permission.can():
					raise Exception('Some lines in your chart is not authorized to access')

			init_result = Chart.init(selected_metrics,chart_config)
			init_result_bool = True
			info = Chart.info
			Chart.info = CHART_INIT_DEFAULT_MESSAGE
			result['selected_metrics'] = selected_metrics
			result['chart_config'] = chart_config
		except Exception, e:
			import traceback,sys
			traceback.print_exc(file=sys.stdout)

			print str(e)
			info = str(e)

	result['init_result_bool'] = init_result_bool
	result['init_result'] = init_result
	result['info'] = info


	return json.dumps(result)

@mod_chart.route('/update/', methods=['GET', 'POST'])
@login_required
def update():
	result = {}
	info = None
	update_result_bool = False
	update_result = None
	if request.method == 'POST':
		# try:
		request_data = json.loads(request.data)
		selected_metrics = request_data['selected_metrics']
		chart_config = request_data['chart_config']
		update_result = Chart.update(selected_metrics,chart_config)
		update_result_bool = True
		info = 'success'
	
	result['update_result_bool'] = update_result_bool
	result['update_result'] = update_result
	result['info'] = info
	return json.dumps(result)



@mod_chart.route('/save/window', methods=['GET', 'POST'])
@login_required
def save_window():
	result = {}
	info = None
	save_result_bool = False
	save_result = None
	if request.method == 'POST':
		try:
			request_data = json.loads(request.data)
			selected_metrics = request_data['selected_metrics']
			chart_config = request_data['chart_config']
			windowname = request_data['windowname']
			user = g.user
			window = Chart.save_window_chart(selected_metrics,chart_config,windowname,user)

			db.session.commit()
			app.logger.info(g.user.username + ' save a window chart : ' +  windowname)

			save_result = {'name':windowname,'indexId':window.windowid}

			save_result_bool = True

			info = 'success'
		except Exception, e:
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			db.session.rollback()
			print str(e)
			info = str(e)

	result['save_result_bool'] = save_result_bool
	result['save_result'] = save_result
	result['info'] = info
	return json.dumps(result)

@mod_chart.route('/load/window', methods=['GET', 'POST'])
@login_required
def load_window():

	result = {}
	info = None
	load_result_bool = False
	load_result = None
	index = None
	selected_windowname = None

	if request.method == 'GET':
		try:
			windowid = request.args.get('windowid',None)
			index = request.args.get('render_index',None)
			selected_windowname = request.args.get('selected_windowname',None)
			load_result = Chart.load_window_chart(windowid)
			info = 'success'
			load_result_bool = True
		except Exception, e:
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			info = str(e)
			print info

	result['info'] = info
	result['load_result_bool'] = load_result_bool
	result['load_result'] = load_result
	result['index'] = index
	result['selected_windowname'] = selected_windowname

	return json.dumps(result)

@mod_chart.route('/delete/window',methods = ['GET','POST'])
@login_required
def delete_window():
	result = {}
	info = None
	delete_result_bool = False
	delete_result = None

	if request.method == 'GET':
		try:
			windowid = request.args.get('windowid',None)
			Chart.delete_window_chart(windowid)
			db.session.commit()
			info = 'success'
			delete_result = windowid
			delete_result_bool = True
			app.logger.info(g.user.username + ' delete a window chart : ' +  windowid)
		except Exception, e:
			db.session.rollback()
			info = str(e)
			print info

	result['info'] = info
	result['delete_result_bool'] = delete_result_bool
	result['delete_result'] = delete_result

	return json.dumps(result)


@mod_chart.route('/save/page', methods=['GET', 'POST'])
@login_required
def save_page():

	result = {}
	info = None
	save_result_bool = False
	save_result = None
	if request.method == 'POST':
		try:
			request_data = json.loads(request.data)

			nine_charts = request_data['nine_charts']
			pagename = request_data['pagename']
			user = g.user
			page = Chart.save_page(nine_charts,pagename,user)

			db.session.commit()

			save_result = {'name':pagename,'indexId':page.pageid}

			save_result_bool = True
			app.logger.info(g.user.username + ' save a page of 9 charts : ' +  pagename)

			info = 'success'
		except Exception, e:
			# import traceback,sys
			# traceback.print_exc(file=sys.stdout)
			db.session.rollback()
			print str(e)
			info = str(e)

	result['save_result_bool'] = save_result_bool
	result['save_result'] = save_result
	result['info'] = info
	return json.dumps(result)

@mod_chart.route('/delete/page', methods=['GET', 'POST'])
@login_required
def delete_page():
	result = {}
	info = None
	delete_result_bool = False
	delete_result = None

	if request.method == 'GET':
		try:
			pageid = request.args.get('pageid',None)
			Chart.delete_page(pageid)
			db.session.commit()
			info = 'success'
			delete_result = pageid
			delete_result_bool = True
			app.logger.info(g.user.username + ' delete a page of 9 charts : ' +  pageid)
		except Exception, e:
			db.session.rollback()
			info = str(e)
			print info

	result['info'] = info
	result['delete_result_bool'] = delete_result_bool
	result['delete_result'] = delete_result

	return json.dumps(result)

@mod_chart.route('/load/page',methods = ['GET','POST'])
@login_required
def load_page():
	result = {}
	info = None
	load_result_bool = False
	load_result = None

	if request.method == 'GET':
		try:
			pageid = request.args.get('pageid',None)
			load_result = Chart.load_page(pageid)
			info = 'success'
			load_result_bool = True
		except Exception, e:
			info = str(e)
			print info

	result['info'] = info
	result['load_result_bool'] = load_result_bool
	result['load_result'] = load_result

	return json.dumps(result)


@mod_chart.route('/report/<path:reportimg>')
def getreportimg(reportimg):
	return app.send_static_file('report/' + reportimg)

@mod_chart.route('/report/generate/<emailscheduleid>')
def report_generate(emailscheduleid):
	#try:
	app.logger.info('generate report of emailschedule in #' + emailscheduleid)
	generate_schedule.gen_upload_report_img(emailscheduleid)
	return 'success'
	#except Exception, e:
	#	return 'failed'

def billing_search(search_value,option,table_head=None):
	if not admin_permission.can():
		raise Exception('You are not authorized to access billing data')
	if table_head is None:
		return SearchWithBilling.search(search_value,option)
	# print table_head
	return SearchWithBilling.search(search_value,option,table_head)



@mod_chart.route('/searchitem/',methods=['POST','GET'])
@login_required
def searchitem():
	result = {}
	info = None
	search_result_bool = False
	search_result = None
	request_option = None
	search_args = {}
	if request.method == 'GET':
		try:
			option = request.args.get('option')
			request_option = option
			search_args['option'] = request_option
			search_value = request.args.get('search_value')
			search_args['search_value'] = search_value
			table_head = request.args.get('table_head',None)
			search_args['table_head'] = table_head
			function_of_option = {'All':SearchWithAll.search,'Basic Metrics':SearchWithBasicMetrics.search,\
									'Browse Metrics':SearchWithAll.search,'billing':billing_search}
			if table_head == None:
				search_result = function_of_option.get(option,SearchInASGGroup.search)(search_value,option)
			else:
				search_result = function_of_option.get(option,SearchInASGGroup.search)(search_value,option,[table_head])
			search_result_bool = True
			info = 'success'
		except Exception, e:
			import sys, traceback 
			traceback.print_exc(file=sys.stdout)
			info = str(e)

	result['search_result_bool'] = search_result_bool
	result['search_result'] = search_result
	result['info'] = info
	result['request_option'] = request_option
	result['args'] = search_args
		# print result
		# print option,search_value
	return json.dumps(result)
		# pass

@mod_chart.route('/browseitem/',methods=['POST','GET'])
@login_required
def browseitem():
	result = {}
	info = None
	browse_result_bool = False
	browse_result = None
	if request.method == 'GET':
		try:
			browse_result = BrowseMetrics.browse()
			browse_result_bool = True
			info = 'success'
		except Exception, e:
			info = str(e)

	result['browse_result_bool'] = browse_result_bool
	result['browse_result'] = browse_result
	result['info'] = info
	return json.dumps(result)

@mod_chart.route('/smr2item',methods=['POST','GET'])
@login_required
def smr2item():
	result = {}
	convert_result = None
	info = None
	convert_result_bool = False
	if request.method == 'POST':
		try:
			selected_metrics = json.loads(request.data)['selected_metrics'] 
			
			convert_result = Chart.smr_2_itemlist(selected_metrics)

			info = 'success'
			convert_result_bool = True
		except Exception, e:
			info = str(e)
			convert_result_bool = False
			convert_result = None

	result['convert_result'] = convert_result
	result['info'] = info
	result['convert_result_bool'] = convert_result_bool
	return json.dumps(result)

@mod_chart.route('/newpage')
@login_required
def newpage():
	services = Service.query.all()
	pages = g.user.pages.all()
	windows = g.user.windows.filter_by(type=WINDOW_CHART).all()
	itemtypes = Itemtype.query.all()
	tmp_arr = []
	aws_tmp_arr = []
	for it in itemtypes:
		if it.aws == None:
			tmp_arr.append(it.itemtypename)
		else:
			item = it.items.first()
			aws_tmp_arr.append(item.itemname)
	itemtypenames = json.dumps(tmp_arr)
	aws_itemtypenames = json.dumps(aws_tmp_arr)
	return render_template("chart/newpage.html",title='Page',services=services,pages=pages,windows=windows,itemtypenames=itemtypenames,aws_itemtypenames=aws_itemtypenames)

@mod_chart.route('/overall')
@login_required
def overall():
	return render_template('chart/overall.html', title='Overall')

@mod_chart.route('/overall/mhd', methods=['POST', 'GET'])
@login_required
def getmhd():
	if not IN_LOCAL:
		result = {}
		get_result = None
		get_result_bool = False
		info = ''
		try:
			o = Overall(1)
			mhd = o.gen_mhd_dict()
			get_result = o.mechine_health(mhd)
			get_result_bool = True
			info = 'success'
		except Exception, e:
			info = str(e)
			get_result_bool = False
			get_result = None

		result['get_result'] = get_result
		result['get_result_bool'] = get_result_bool
		result['info'] = info

		return json.dumps(result)
	else:
		o = Overall(1)
		return o.mechine_health_test()


@mod_chart.route('/overall/s2s', methods=['POST', 'GET'])
@login_required
def gets2s():
	if not IN_LOCAL:
		result = {}
		get_result = None
		get_result_bool = False
		info = ''
		try:
			o = Overall(1)
			s2s = o.gen_s2s_dict()
			get_result = o.server_2_server_data(s2s)
			get_result_bool = True
			info = 'success'
		except Exception, e:
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			info = str(e)
			get_result_bool = False
			get_result = None

		result['get_result'] = get_result
		result['get_result_bool'] = get_result_bool
		result['info'] = info

		return json.dumps(result)
	else:
		o = Overall(1)
		return o.server_2_server_data_test()

@mod_chart.route('/overall/bhd', methods=['POST', 'GET'])
@login_required
def getbhd():
	if not IN_LOCAL:
		result = {}
		get_result = None
		get_result_bool = False
		info = ''
		try:
			o = Overall(1)
			interval = request.args.get('interval', None)
			bhd = o.gen_bhd_dict(interval)
			get_result = o.business_health(bhd)
			get_result_bool = True
			info = 'success'
		except Exception, e:
			info = str(e)
			get_result_bool = False
			get_result = None

		result['get_result'] = get_result
		result['get_result_bool'] = get_result_bool
		result['info'] = info

		return json.dumps(result)
	else:
		o = Overall(1)
		return o.business_health_test()

@mod_chart.route('/overall/cd', methods=['POST', 'GET'])
@login_required
def getcd():
	if not IN_LOCAL:
		result = {}
		get_result = None
		get_result_bool = False
		info = ''
		try:
			o = Overall(1)
			cd = o.gen_cd_dict()
			get_result = o.core_data(cd)
			get_result_bool = True
			info = 'success'
		except Exception, e:
			info = str(e)
			get_result_bool = False
			get_result = None

		result['get_result'] = get_result
		result['get_result_bool'] = get_result_bool
		result['info'] = info

		return json.dumps(result)
	else:
		o = Overall(1)
		return o.core_data_test()



