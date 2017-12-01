from flask import Blueprint
from . import authentication, post, user, comment, errors

api = Blueprint('api', __name__)
