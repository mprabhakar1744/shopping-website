from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField , TextAreaField , DecimalField,SubmitField,ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired



class RegistrationForm(Form):
	name = StringField('name', [validators.Length(min=4, max=25)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email Address', [validators.Length(min=6, max=35)])
	password = PasswordField('New Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')


class LoginForm(Form):
	email = StringField('Email Address', [validators.Length(min=6, max=35)])
	password = PasswordField('Password', [validators.DataRequired()])


class Addproducts(Form):
	name = StringField('Name', [validators.DataRequired()])
	price = DecimalField('Price',[validators.DataRequired()])
	discount = IntegerField('Discount', default=0)
	stock = IntegerField('Stock',[validators.DataRequired()])
	desc = TextAreaField('discriptiop',[validators.DataRequired()])
	colors = TextAreaField('Colors',[validators.DataRequired()])

	image_1=FileField('Image_1')
	image_2=FileField('Image_2')
	image_3=FileField('Image_3')








