from flask import Blueprint

from app.user.controller import (
    signup
)

user_api = Blueprint('user', __name__)

user_api.add_url_rule(rule='/signup', view_func=signup, methods=['POST', ])