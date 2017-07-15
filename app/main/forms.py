from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from ..models import User, Role

from flask_pagedown.fields import PageDownField

class EditProfileForm(FlaskForm):
	name = StringField('Real Name', validators=[Length(0,64)])
	location = StringField('Location', validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')




class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    head = StringField('Title', validators=[Required()])
    body = PageDownField("Details", validators=[Required()])
    year = SelectField(u"Select the year.", choices=[('0', 'Every Year'), ('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017') ])
    branch = SelectField(u'Select the branch', choices=[('ALL', 'Not specefic'), ('ME', 'Mechanical'), ('CE', 'Civil'), ('CSE', 'Computer Science'), ('EE', 'Electronics'), ('IT', 'IT')])
    submit = SubmitField("Post")


class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Comment')


class SortForm(FlaskForm):
    branch = SelectField(u'Select Branch', choices=[('ME', 'Mechanical'), ('CE', 'Civil'), ('CSE', 'Computer Science'), ('EE', 'Electronics'), ('IT', 'IT')])
    year = SelectField(u"Select Year", choices=[('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017') ])
    submit = SubmitField('Get Students')