from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask.ext.login import login_required
from monitor import db,app

from monitor.item.models import Area,Service,Host,Itemdatatype,Itemtype,Zbxitemtype,Aws,Action
# from monitor.item.functions import mass_add_1_level,mass_add_host_item_for_area,mass_add_itemtype,add_host
from monitor.item.functions import *
from monitor.zabbix.zabbix_api import zabbix_api
from monitor.MonitorException import *
import json
import boto.ec2.autoscale
from config import AUTOSCALE_COMMAND_PATH ,AUTOSCALE,EMAILNOTIFICATION,MAIL_USE_SNS,EMAIL_SNS_PATH,EMAIL_NORMAL_PATH,AREA,\
					ZABBIX_TEMPLATE_PREFIX,TEMPLATE_GROUP_SPLITER,HOST_GROUP_NAME

from flask.ext.principal import Permission, RoleNeed
admin_permission = Permission(RoleNeed('1')).union(Permission(RoleNeed('0')))

from monitor.zabbix.models import Zabbixhosts,Zabbixinterface
from monitor.item.alarm import Alarm

mod_item = Blueprint('item', __name__, url_prefix='/item')

from flask.views import View

class ItemTypeListView(View):

	def __init__(self,template_name,objectytpe,objectname):
		self.template_name = template_name
		self.objecttype = objectytpe
		self.objectname = objectname

	def render_template(self,context):
		return render_template(self.template_name,**context)

	def dispatch_request(self,objectid):
		objects = self.objecttype.query.get(objectid).itemtypes.all()
		context = {'itemtype':objects,'name':self.objectname}
		return self.render_template(context)

class HostItemView(View):

	def __init__(self,template_name):
		self.template_name = template_name

	def render_template(self,context):
		return render_template(self.template_name,**context)

	def dispatch_request(self,hostid):
		items = Host.query.get(hostid).items.all()
		context = {'objects':items,'name':Host.query.get(hostid).hostname}
		return self.render_template(context)

class HostListView(View):

	def __init__(self,template_name,objectytpe,objectname):
		self.template_name = template_name
		self.objecttype = objectytpe
		self.objectname = objectname

	def render_template(self,context):
		return render_template(self.template_name,**context)

	def dispatch_request(self,objectid):
		host_monitor = self.objecttype.query.get(objectid).hosts.all()
		host = host_with_zabbix_data(host_monitor)
		context = {'host':host,'name':self.objectname}
		return self.render_template(context)



mod_item.add_url_rule('/host/itemtype/<objectid>',view_func=ItemTypeListView.as_view('host_it',template_name='item/it.html',objectytpe=Host,objectname='Host'))
mod_item.add_url_rule('/host/item/<hostid>',view_func=HostItemView.as_view('host_i',template_name='item/item.html'))
mod_item.add_url_rule('/service/itemtype/<objectid>',view_func=ItemTypeListView.as_view('service_it',template_name='item/it.html',objectytpe=Service,objectname='Service'))
mod_item.add_url_rule('/service/host/<objectid>',view_func=HostListView.as_view('service_host',template_name='item/hostall.html',objectytpe=Service,objectname='Service'))
mod_item.add_url_rule('/area/itemtype/<objectid>',view_func=ItemTypeListView.as_view('area_it',template_name='item/it.html',objectytpe=Area,objectname='Area'))
mod_item.add_url_rule('/area/host/<objectid>',view_func=HostListView.as_view('area_host',template_name='item/hostall.html',objectytpe=Area,objectname='Area'))



@mod_item.route('/')
@login_required
def mainboard():
	area = Area.query.all()
	service = Service.query.all()
	host_monitor = Host.query.all()
	host = host_with_zabbix_data(host_monitor)
	itemtype = Itemtype.query.all()
	trigger = Trigger.query.all()
	return render_template("item/main.html",area=area,service=service,host=host,itemtype=itemtype,trigger=trigger)


@mod_item.route('/area/', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def area():
	# form = addAreaForm()
	# choose = chooseServiceForm()
	services = Service.query.all()
	if request.method == 'POST':
		try:
			areaname = request.form.get('areaname')
			f = request.form
			serviceselect = []
			for key in f.keys():
			    for value in f.getlist(key):
			    	if len(value) != 0:
						if key == 'service':
							serviceselect.append(value)
			area = Area(areaname=areaname)
			db.session.add(area)
			for serviceid in serviceselect:
				service = Service.query.filter_by(serviceid=int(serviceid)).first()
				a = area.add_service(service)
				db.session.add(a)

			db.session.commit()
			app.logger.info(g.user.username + ' add an area type : ' + areaname)
		except Exception, e:
			db.session.rollback()
			flash(str(e),'danger')
			return redirect(url_for('item.area'))
		else:
			flash('You add an area','success')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/area.html',services=services)

@mod_item.route('/area/delete/<areaid>', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
@login_required
def areadelete(areaid):
	try:
		area = Area.query.filter_by(areaid=areaid).first()
		db.session.delete(area)
		db.session.commit()
		app.logger.info(g.user.username + ' delete an area record : ' + areaid )
	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('you delete an area','success')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))

@mod_item.route('/service/', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def service():

	# areaelb = get_all_area_elb()
	# print areaelb
	area = Area.query.all()
	if request.method == 'POST':
		try:
			zabbix = zabbix_api()
			areaid = request.form.get('areaid')
			usetype = request.form.get('usetype')
			servicename = None
			if usetype == '1':
				servicename = request.form.get('servicename')
			elif usetype == '2':
				servicename = request.form.get('elbname')

			add_group_template(servicename,zabbix)
			service = Service(servicename=servicename)
			db.session.add(service)	
			addhost = request.form.get('addhost')
			if addhost == '1' and usetype == '2':
				add_host_register_in_elb(servicename,areaid)

			db.session.commit()

			app.logger.info(g.user.username + ' add a service type : ' + servicename)

		except Exception, e:
			db.session.rollback()
			zabbix.rollback()
			flash(str(e),'danger')
			db.session.remove()
			return redirect(url_for('item.service'))
		else:
			flash('You add a service','success')
			db.session.remove()
			return redirect(url_for('item.mainboard'))
			
	# return render_template('item/service.html')
	return render_template('item/service.html',area = area)

@mod_item.route('/service_json',methods=['POST','GET'])
@login_required
def service_json():
	result = {}
	load_service_result = None
	load_service_result_bool = False
	info = None
	try:
		load_service_result = []
		for s in Service.query.all():
			load_service_result.append(s.servicename)
		load_service_result_bool = True
		info = 'success'
	except Exception, e:
		info = str(e)

	result['load_service_result'] = load_service_result
	result['load_service_result_bool'] = load_service_result_bool
	result['info'] = info

	return json.dumps(result)


@mod_item.route('/service/host_json/<serviceid>',methods=['POST','GET'])
@login_required
def service_host_json(serviceid):
	service = Service.query.get(serviceid)
	if service == None:
		return json.dumps(0)
	host_monitor = service.hosts.all()
	host = []
	for h in host_monitor:
		tmp = {}
		tmp['hostid'] = h.hostid
		tmp['hostname'] = h.hostname
		zh = Zabbixhosts.query.get(h.hostid)
		zi = Zabbixinterface.query.filter_by(hostid=h.hostid).first()
		tmp['ip'] = zi.ip
		tmp['available'] = zh.available
		tmp['error'] = zh.error
		host.append(tmp)
	if len(host) == 0:
		return json.dumps(0)
	return json.dumps({'host':host,'indexId':service.serviceid,'servicename':service.servicename})

@mod_item.route('/elbforarea/', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def elbforarea():
	areaid = request.args.get('areaid','')
	result = []
	try:
		areaname = Area.query.filter_by(areaid=areaid).first().areaname
		result = get_elb_for_area(areaname)
	except Exception, e:
		raise MonitorException('get elb error, ' + str(e))
	finally:
		return json.dumps(result)


@mod_item.route('/service/delete/<serviceid>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def servicedelete(serviceid):
	try:
		zabbix = zabbix_api()
		service = Service.query.filter_by(serviceid=serviceid).first()
		delete_group_template(service.servicename,zabbix)
		db.session.delete(service)
		db.session.commit()
		app.logger.info(g.user.username + ' delete a service group : ' + serviceid)
	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('you delete a service type','success')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))


@mod_item.route('/host/', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def host():
	services = Service.query.all()
	areas = Area.query.all()

	if request.method == 'POST':
		try:
			hostname = request.form.get('hostname')
			host_ip = request.form.get('hostip')
			areaid = request.form.get('areaid')
			serviceid = request.form.get('serviceid')
			# print " areaid,serviceid", areaid,serviceid
			servicename = Service.query.filter_by(serviceid = serviceid).first().servicename
			areaname = Area.query.filter_by(areaid = areaid).first().areaname
			# print hostname,host_ip,servicename,areaname
			add_host(hostname, servicename,host_ip,areaname)
			db.session.commit()
			app.logger.info(g.user.username + ' add a host : ' + hostname)
		except Exception, e:
			db.session.rollback()
			flash(str(e),'danger')
			return redirect(url_for('item.host'))
		else:
			flash('You add a host','success')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/host.html',areas=areas,services=services)

@mod_item.route('/host/delete/<hostid>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def hostdelete(hostid):
	try:
		delete_host(hostid)
		db.session.commit()
		app.logger.info(g.user.username + ' delete a host : ' + hostid)

	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('You delete a host','success')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))


@mod_item.route('/itemtype/', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def itemtype():
	areas = Area.query.all()
	services = Service.query.all()
	hosts = Host.query.all()
	idts = Itemdatatype.query.all()

	if request.method == 'POST':
		zabbix = zabbix_api()
		try:
			kinds = request.form.get('kinds')
			indexid = request.form.get('indexid'+kinds)
			key = request.form.get('key')
			itemdatatypename = request.form.get('itemdatatypeid')
			unitname = request.form.get('unitname')
			zabbixvaluetype = request.form.get('datatype')
			# print kinds,indexid,key,itemdatatypename,unitname,zabbixvaluetype
			add_key(kinds,indexid,key,itemdatatypename,unitname,zabbixvaluetype,zabbix)
			db.session.commit()
			app.logger.info(g.user.username + ' add an item : ' + key)

		except Exception, e:
			traceback.print_exc(file=sys.stdout)
			zabbix.rollback()
			db.session.rollback()
			flash(str(e),'danger')
			return redirect(url_for('item.itemtype'))
			# return redirect(url_for('item.itemtype',areas=areas,services=services,hosts=hosts,idts=idts))
		else:
			flash(' you add an item ','success')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/itemtype.html',areas=areas,services=services,hosts=hosts,idts=idts)

@mod_item.route('/itemtype/delete/<itemtypeid>', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def itemtypedelete(itemtypeid):
	zabbix = zabbix_api()
	try:
		it = Itemtype.query.filter_by(itemtypeid = itemtypeid).first()

		delete_template_item(it,zabbix)

		if it != None:
			items = it.items
			itemids = []
			for i in items:
				itemids.append(i.itemid)
				db.session.delete(i)
			zabbix.item_delete(itemids)
			db.session.delete(it)
			db.session.commit()
			app.logger.info(g.user.username + ' delete an item : ' + itemtypeid)

			# hosts = Host.query.all()
			# for h in hosts:
			# 	update_host(h.hostid,h.hostname,h.area.areaid,h.service.serviceid)
	except Exception, e:
		db.session.rollback()
		zabbix.rollback()
		flash(str(e),'danger')
	else:
		flash('delete an item','success')
	# finally:
	# 	db.session.remove()
	
	return redirect(url_for('item.mainboard'))


@mod_item.route('/trigger/delete/<triggerid>',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def trigger_delete(triggerid):
	zabbix = zabbix_api()
	try:
		Alarm.delete_alarm(zabbix,triggerid)
		db.session.commit()
		app.logger.info(g.user.username + ' delete an alarm : ' + triggerid)

	except Exception, e:
		db.session.rollback()
		flash(str(e),'danger')
	else:
		flash('delete a trigger','success')
	# finally:
	# 	db.session.remove()
	
	return redirect(url_for('item.mainboard'))

@mod_item.route('/trigger/<triggerid>',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def trigger_load(triggerid):
	result = {}
	load_result = None
	load_result_bool = False
	info = None
	try:
		load_result = Alarm.load_alarm(triggerid)
		load_result_bool = True
		info = 'success'
		# load_result['Threshold'] = 'net.if.in[eth1] > 12345.0 for 300s'
		# load_result['Actions'] = 'sending email to topic including addresses in below: xuzhongyong@tp-link.net ; 670271826@qq.com'
		# load_result['Namespace'] = 'Monitor'
		# load_result['Metric Name'] = 'net.if.in[eth1]'
		# load_result['Period'] = '1 minute'
		# load_result['Statistic'] = 'Average'

	except Exception, e:
		load_result = None
		load_result_bool = False
		info = str(e)

	result['load_result'] = load_result
	result['load_result_bool'] = load_result_bool
	result['info'] = info

	return json.dumps(result)


@mod_item.route('/generateformula',methods=['GET','POST'])
@login_required
def generateformula():
	scale = request.args.get('scale')
	scale_operator = request.args.get('scaleoperator')
	first_itemids = request.args.get('first_itemids')
	fs_operator = request.args.get('fs_operator')
	second_itemids = request.args.get('second_itemids')
	brackets_position = int(request.args.get('brackets_position'))

	first_itemids = arg_2_array(first_itemids)
	second_itemids = arg_2_array(second_itemids)

	result = create_calculated_items_formula(scale,scale_operator,first_itemids,fs_operator,second_itemids,brackets_position)

	# print result
	return json.dumps(result)

@mod_item.route('/autoscalegroup',methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=403)
def autoscalegroup():

	result = {}
	load_result = None
	load_result_bool = False
	info = None
	try:
		areaname = AREA
		con = boto.ec2.autoscale.connect_to_region(areaname)
		asg = con.get_all_groups()
		
		load_result = []
		for a in asg:
			load_result.append(a.name)
		load_result_bool = True
		info = 'success'

	except Exception, e:
		info = str(e)
		print info
	
	result['load_result'] = load_result
	result['load_result_bool'] = load_result_bool
	result['info'] = info

	return json.dumps(result)

@mod_item.route('/alarm',methods=['GET','POST'])
@login_required
def alarm():
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
		# print request.form
		try:
			zabbix = zabbix_api()
			f = request.form
			form_arg = {}
			for key in f.keys():
				form_arg[key] = []
				for value in f.getlist(key):
					if len(value) != 0:
						form_arg[key].append(value)

			for key in form_arg:
				print key,form_arg[key]

			Alarm.create_alarm(form_arg,zabbix)
			db.session.commit()
			app.logger.info(g.user.username + ' create an alarm')
			flash('You created an alarm','success')
			return redirect(url_for('item.mainboard'))
		except Exception, e:
			db.session.rollback()
			zabbix.rollback()
			import traceback,sys
			traceback.print_exc(file=sys.stdout)
			flash(str(e),'danger')

	return render_template('item/alarm.html',itemtypenames=itemtypenames,aws_itemtypenames=aws_itemtypenames)


# @mod_item.route('/test')
# @login_required
# def item_test():
# 	try:
# 		test_add()
# 	except Exception, e:
# 		db.session.rollback()
# 		# pass
# 	else:
# 		db.session.commit()
# 	finally:
# 		zit = Zbxitemtype.query.all()
# 		t = ''
# 		for z in zit:
# 			t += str(z.zbxitemtypeid )
# 		return t
