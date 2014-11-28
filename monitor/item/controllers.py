from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask.ext.login import login_required
from monitor import db

from monitor.item.models import Area,Service,Host,Itemdatatype,Itemtype,Zbxitemtype
from monitor.item.forms import addAreaForm,addServiceForm,chooseServiceForm,addHostForm
# from monitor.item.functions import mass_add_1_level,mass_add_host_item_for_area,mass_add_itemtype,add_host
from monitor.item.functions import *
from monitor.zabbix_api import zabbix_api
from monitor.MonitorException import *
import json


mod_item = Blueprint('item', __name__, url_prefix='/item')

@mod_item.route('/')
@login_required
def mainboard():
	area = Area.query.all()
	service = Service.query.all()
	host = Host.query.all()
	itemtype = Itemtype.query.all()
	return render_template("item/main.html",area=area,service=service,host=host,itemtype=itemtype)


@mod_item.route('/area/', methods=['GET', 'POST'])
@login_required
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
		except Exception, e:
			db.session.rollback()
			flash(str(e),'error')
			return redirect(url_for('item.area'))
		else:
			db.session.commit()
			flash('You add an area')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/area.html',services=services)

@mod_item.route('/area/delete/<areaid>', methods=['GET', 'POST'])
@login_required
def areadelete(areaid):
	try:
		area = Area.query.filter_by(areaid=areaid).first()
		db.session.delete(area)
	except Exception, e:
		db.session.rollback()
		flash(str(e),'error')
	else:
		db.session.commit()
		flash('you delete an area')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))

@mod_item.route('/service/', methods=['GET', 'POST'])
@login_required
def service():

	# areaelb = get_all_area_elb()
	# print areaelb
	area = Area.query.all()
	if request.method == 'POST':
		try:
			areaid = request.form.get('areaid')
			usetype = request.form.get('usetype')
			servicename = None
			if usetype == '1':
				servicename = request.form.get('servicename')
			elif usetype == '2':
				servicename = request.form.get('elbname')
			service = Service(servicename=servicename)
			db.session.add(service)	
			addhost = request.form.get('addhost')
			if addhost == '1' and usetype == '2':
				add_host_register_in_elb(servicename,areaid)
		except Exception, e:
			db.session.rollback()
			flash(str(e),'error')
			db,session.remove()
			return redirect(url_for('item.service'))
		else:
			db.session.commit()
			flash('You add a service')
			db.session.remove()
			return redirect(url_for('item.mainboard'))
			
	# return render_template('item/service.html')
	return render_template('item/service.html',area = area)

@mod_item.route('/elbforarea/', methods=['GET', 'POST'])
@login_required
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
def servicedelete(serviceid):
	try:
		service = Service.query.filter_by(serviceid=serviceid).first()
		db.session.delete(service)
	except Exception, e:
		db.session.rollback()
		flash(str(e),'error')
	else:
		db.session.commit()
		flash('you delete a service type')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))


@mod_item.route('/host/', methods=['GET', 'POST'])
@login_required
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
			add_host(hostname, servicename,host_ip,areaname);
		except Exception, e:
			db.session.rollback()
			flash(str(e),'error')
			return redirect(url_for('item.host'))
		else:
			db.session.commit()
			flash('You add a host')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/host.html',areas=areas,services=services)

@mod_item.route('/host/delete/<hostid>', methods=['GET'])
@login_required
def hostdelete(hostid):
	try:
		delete_host(hostid)
	except Exception, e:
		db.session.rollback()
		flash(str(e),'error')
	else:
		db.session.commit()
		flash('You delete a host')
	finally:
		db.session.remove()

	return redirect(url_for('item.mainboard'))


@mod_item.route('/itemtype/', methods=['GET', 'POST'])
@login_required
def itemtype():
	areas = Area.query.all()
	services = Service.query.all()
	hosts = Host.query.all()
	idts = Itemdatatype.query.all()

	if request.method == 'POST':
		try:
			kinds = request.form.get('kinds')
			indexid = request.form.get('indexid'+kinds)
			key = request.form.get('key')
			itemdatatypename = request.form.get('itemdatatypeid')
			unitname = request.form.get('unitname')
			zabbixvaluetype = request.form.get('datatype')
			# print kinds,indexid,key,itemdatatypename,unitname,zabbixvaluetype
			add_key(kinds,indexid,key,itemdatatypename,unitname,zabbixvaluetype)
		except Exception, e:
			db.session.rollback()
			flash(str(e),'error')
			return redirect(url_for('item.itemtype'))
			# return redirect(url_for('item.itemtype',areas=areas,services=services,hosts=hosts,idts=idts))
		else:
			db.session.commit()
			flash(' you add an item ')
			return redirect(url_for('item.mainboard'))
		finally:
			db.session.remove()		

	return render_template('item/itemtype.html',areas=areas,services=services,hosts=hosts,idts=idts)

@mod_item.route('/itemtype/delete/<itemtypeid>', methods=['GET', 'POST'])
@login_required
def itemtypedelete(itemtypeid):
	try:
		it = Itemtype.query.filter_by(itemtypeid = itemtypeid).first()
		if it != None:
			items = it.items
			zabbix = zabbix_api()
			for i in items:
				itemid = i.itemid
				zabbix.item_delete(itemid)
				db.session.delete(i)
			db.session.delete(it)
			# hosts = Host.query.all()
			# for h in hosts:
			# 	update_host(h.hostid,h.hostname,h.area.areaid,h.service.serviceid)
	except Exception, e:
		db.session.rollback()
		flash(str(e),'error')
	else:
		db.session.commit()
		flash('delete an item')
	# finally:
	# 	db.session.remove()
	
	return redirect(url_for('item.mainboard'))



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