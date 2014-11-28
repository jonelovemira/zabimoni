from flask.ext.wtf import Form
from wtforms import TextField,widgets,SelectMultipleField,SelectField
from wtforms.validators import DataRequired 

from monitor.item.models import Area,Service,Host,Aws

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class addAreaForm(Form):
	addAreaName = TextField('add name', validators = [DataRequired()])

	def validate(self):
		if not Form.validate(self):
			return False

		area = Area.query.filter_by(areaname=self.addAreaName.data).first()

		if area != None:
			self.addAreaName.errors.append('area name is already exist. try another')
			return False
		return True

class chooseServiceForm(Form):
	
	service_select = MultiCheckboxField('Service')


class addHostForm(Form):
	addHostip = TextField('add ip',validators = [DataRequired()])
	area = SelectField('area',coerce=int)
	service = SelectField('service',coerce=int)




class addServiceForm(Form):
	addServiceName = TextField('add name', validators = [DataRequired()])

	def validate(self):
		if not Form.validate(self):
			return False

		service = Service.query.filter_by(servicename=self.addServiceName.data).first()

		if service != None:
			self.addServiceName.errors.append('service name is already exist. try another')
			return False
		return True

# class indexForm(Form):
# 	allarea = Area.query.all()
# 	areachoice = [(area.areaid,area.areaname) for area in allarea]
# 	areachoice.append((-1,'all'))
# 	allservice = Service.query.all()
# 	servicechoice = [(service.serviceid,service.servicename) for service in allservice]
# 	servicechoice.append((-1,'all'))
# 	allhost = Host.query.all()
# 	hostchoice = [(host.hostid,host.hostname) for host in allhost]
# 	hostchoice.append((-1,'all'))
# 	allaws = Aws.query.all()
# 	awschoice = [(aws.awsid,aws.awsname) for aws in allaws]
# 	awschoice.append((-1,'all'))

# 	area = SelectField('area',coerce=int,choices=areachoice)
# 	service = SelectField('service',coerce=int,choices=servicechoice)
# 	host = SelectField('host',coerce=int,choices=hostchoice)
# 	aws = SelectField('aws',coerce=int,choices=awschoice)

