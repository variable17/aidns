from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, IntegerField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')



class RegistrationForm(FlaskForm):
	roll = StringField('Roll No.', validators=[Required(), Length(1,10)])
	email = StringField('Email', validators=[Required(), Email(), Length(1,64)])
	username = StringField('Username', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters, numbers, dots or underscores') ])
	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match.')])
	password2 = PasswordField('Confirm Password', validators=[Required()])
	submit = SubmitField('Register')





	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already registered')

	def validate_roll(self, field):
		try:
			a = int(field.data)
		except:
			raise ValidationError('Enter Valid roll no.')
		if User.query.filter_by(roll=field.data).first():
			raise ValidationError('Roll no already registered.')


class ChangePassword(FlaskForm):
	old_password = StringField('Old Password', validators=[Required()])
	new_password = StringField('New Password', validators=[Required(), EqualTo('new_password2', message='Password must match.')])
	new_password2 = StringField('Confirm Password', validators=[Required(),])
	submit = SubmitField('Change Password')

class ForgetPassword(FlaskForm):
	email = StringField('Email', validators=[Required()])
	submit = SubmitField('Submit')


	def validate_email(self, field):
		if not User.query.filter_by(email=field.data).first():
			raise ValidationError('Email not registered.')



class ResetPassword(FlaskForm):
	email = StringField("Email", validators=[Required(), Email(), Length(1,64)])
	new_password = PasswordField('New Password', validators=[Required(), EqualTo('new_password2', message='Password must match')])
	new_password2 = PasswordField('Confirm Password', validators=[Required()])
	submit = SubmitField('Change Password')


	def validate_email(self, field):
		if not User.query.filter_by(email=field.data).first():
			raise ValidationError('Email not registered.')



class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
