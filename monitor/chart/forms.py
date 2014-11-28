from flask.ext.wtf import Form
from wtforms import TextField,SelectField,widgets,SelectMultipleField,SelectField
from wtforms.validators import DataRequired 
from monitor.item.models import Area,Service,Host,Aws

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class saveWindowForm(Form):
	savedWindowName = TextField('window_name', validators = [DataRequired()])

	def __init__(self, user, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = user
		# print "user",user
	
	def validate(self):	
		if not Form.validate(self):
			return False

		window = self.user.windows.filter_by(type=0).filter_by(windowname=self.savedWindowName.data).first()
		
		if window != None:
			self.savedWindowName.errors.append('This window name is already exsits,Please choose another one.')
			return False
		return True

class savePageForm(Form):
	savedPageName = TextField('page_name', validators = [DataRequired()])

	def __init__(self, user, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = user
		# print "user",user
	
	def validate(self):	
		if not Form.validate(self):
			return False

		page = self.user.pages.filter_by(pagename=self.savedPageName.data).first()
		
		if page != None:
			self.savedPageName.errors.append('This page name is already exsits,Please choose another one.')
			return False
		return True

class indexForm(Form):
	area = SelectField('area',coerce=int)
	service = SelectField('service',coerce=int)
	host = SelectField('host',coerce=int)
	aws = SelectField('aws',coerce=int)

class checkboxForm(Form):
	areabox = MultiCheckboxField('areas',coerce=int)
	servicebox = MultiCheckboxField('services',coerce=int)
	hostbox = MultiCheckboxField('hosts',coerce=int)
	awsbox = MultiCheckboxField('aws',coerce=int)
	
		

class areacheckboxForm(Form):
	areabox = MultiCheckboxField('areas')

class servicecheckboxForm(Form):
	servicebox = MultiCheckboxField('services')

class hostcheckboxForm(Form):
	hostbox = MultiCheckboxField('hosts')

class awscheckboxForm(Form):
	awsbox = MultiCheckboxField('aws')
		




