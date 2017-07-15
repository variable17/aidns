

import hashlib

from flask import request, url_for

from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from markdown import markdown
import bleach
from .exceptions import ValidationError



class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80





class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name




class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	head = db.Column(db.Text)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	year = db.Column(db.String(64), index = True)
	branch = db.Column(db.String(64), index = True)


	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
		    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'br']
		target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
			tags=allowed_tags, strip = True))



	@staticmethod
	def from_json(json_post):
		body = json_post.get('body')
		if body is None or body == '':
			raise ValidationError('Post does not have a body')
		return Post(body=body)



	@staticmethod
	def generate_fake(count=100):
		from random import seed, randint
		import forgery_py
		import random

		year = ['2013', '2014', '2015', '2016', '2017']
		branch = ['CSE', 'IT', 'CE', 'EE', 'ME']
		user_count = User.query.count()
		seed()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
			 timestamp=forgery_py.date.date(True), author=u,
			 year = random.choice(year), branch = random.choice(branch)
			 )
			db.session.add(p)
			db.session.commit()

	def to_json(self):
		json_post = {
		    'id': self.id,
		    'url': url_for('api.get_post', id=self.id, _external=True),
		    'name': self.author.username,
		    'avatar': self.author.gravatar(size=40),
		    'head': self.head,
    	    'body': self.body,
    	    'timestamp': self.timestamp,
    	    'branch' : self.branch,
    	    'year' : self.year,
    	    'author': url_for('api.get_user', id=self.author_id, _external=True),
    	    'comments': url_for('api.get_post_comments', id=self.id, _external=True),
    	    'comment_count': self.comments.count()
		}
		return json_post

db.event.listen(Post.body, 'set', Post.on_changed_body)




class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(64), unique = True, index = True)
	username = db.Column(db.String(64), unique = True, index = True)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default = datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
	password_hash = db.Column(db.String(128))
	avatar_hash = db.Column(db.String(32))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean, default=False)
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	roll = db.Column(db.Integer, unique = True, index = True)
	branch = db.Column(db.String(64), index = True)
	year = db.Column(db.Integer, index = True)



	def to_json(self):
		json_user = {
		    'url': url_for('api.get_user', id=self.id, _external=True),
		    'username': self.username,
		    'avatar': self.avatar_hash,
		    'branch': self.branch,
		    'year': self.year,
		    'roll': self.roll,
		    'member_since': self.member_since,
		    'last_seen': self.last_seen,
		    'posts': url_for('api.get_user_posts', id = self.id, _external=True),
		    'post_count': self.posts.count()
		}
		return json_user






	def generate_auth_token(self, expiration):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id':self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data['id'])



	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py
		import random

		year = ['2013', '2014', '2015', '2016', '2017']
		branch = ['CSE', 'IT', 'EE', 'CE', 'ME']
		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     name=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True),
                     year = random.choice(year),
                     branch = random.choice(branch))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()



	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
			if self.email is not None and self.avatar_hash is None:
				self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()



	def __repr__(self):
		return '<User %r>' %self.username


	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		if self.email is None:
			pass
		else:
			email = self.email
			hash = self.avatar_hash or hashlib.md5(email.encode('utf-8')).hexdigest()
			return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)




	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)


	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))


	def can(self, permissions):
		return self.role is not None and \
		(self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)



	@property
	def password(self):
		raise AttributeError('Password is not a redable attribute.')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)


	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	
	def generate_confirmation_token(self, expiration = 3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm':self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.id, 'new_email': new_email})



	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email =  new_email
		self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		db.session.add(self)
		return True




	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	def reset(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True



class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False


login_manager.anonymous_user = AnonymousUser



class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


	def to_json(self):
		json_comment = {
		    'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True)
		}
		return json_comment

	@staticmethod
	def from_json(json_comment):
		body = json_comment.get('body')
		if body is None or body == '':
			raise ValidationError('comment does not have a body')
		return Comment(body=body)

