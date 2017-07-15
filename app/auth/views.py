from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePassword, ForgetPassword, ResetPassword, ChangeEmailForm
from .. import db
from ..models import User
from ..email import send_email
from .functions import *


@auth.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid Username or password.')
	return render_template('auth/login.html', form = form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))



@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		year, branch = parse(form.roll.data)
		user = User(roll=form.roll.data, email=form.email.data, username=form.username.data, password=form.password.data, year=year, branch=branch)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm your Account', 'auth/email/confirm', user = user, token = token)
		flash('A confirmation email has been sent to you by email.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html', form = form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePassword()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.new_password.data
			db.session.add(current_user)
			flash('You rpassword has been updated.')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid Password.')
	return render_template('auth/change_password.html', form = form)


@auth.route('/forget_password', methods = ['GET', 'POST'])
def forget_password():
	form = ForgetPassword()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		token = user.generate_reset_token()
		send_email(user.email, 'Password reset', 'auth/email/password_reset', user = user, token = token )
		flash('An email with instructions has been sent to you.')
		return redirect(url_for('auth.login'))
	return render_template('auth/forget_password.html', form = form)




@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset(token, form.new_password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)




@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	else:
		flash('The confirmation link has been expired.')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user = current_user, token = token)
	flash('A new confirmation email has been sent to you email.')
	return redirect(url_for('main.index'))


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))





