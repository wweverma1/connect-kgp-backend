from flask import Blueprint

from app.home.controller import (
    home,
    getRating,
    postRating
)

home_api = Blueprint('home', __name__)

home_api.add_url_rule(rule='/', view_func=home, methods=['GET'])
home_api.add_url_rule(rule='/rate', view_func=postRating, methods=['POST'])
home_api.add_url_rule(rule='/rate', view_func=getRating, methods=['POST'])