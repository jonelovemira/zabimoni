# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, PasswordField,SelectField #,EmailField# BooleanField

# Import Form validators
from wtforms.validators import DataRequired, Email, EqualTo
from monitor.auth.models import User


# Define the login form (WTForms)

class LoginForm(Form):
    name    = TextField('User name', [
                DataRequired(message='Forgot your username?')])
    password = PasswordField('Password', [
                DataRequired(message='Must provide a password. ;-)')])

class AddUserForm(Form):
	usertypearr = [(1,'admin'),(2,'normal')]
	loginpermissionarr = [(1,'allowed'), (0,'not allowed')]
	name = TextField('User name', [	DataRequired(message='Add an username')])
	password = PasswordField('Password', [DataRequired(message='Must provide a password. ;-)')])
	confirmPassword = PasswordField('Password')
	usertype = SelectField('Choose user type',coerce=int,choices=usertypearr)
	loginpermission = SelectField('Choose user type',coerce=int,choices=loginpermissionarr)
	email = TextField('email address',[DataRequired()])


	def validate(self):
		if not Form.validate(self):
			return False
		user = User.query.filter_by(username = self.name.data).first()

		if user != None:
			self.name.errors.append('user name is already exist. try another')
			return False
		print self.password.data , self.confirmPassword.data
		if self.password.data != self.confirmPassword.data:
			self.password.errors.append('confirm password error')
			return False
		return True