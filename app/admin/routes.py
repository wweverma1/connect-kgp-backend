from flask import Blueprint

from app.admin.controller import (
    getInfo,
)

admin_api = Blueprint('admin', __name__)

admin_api.add_url_rule(rule='/info', view_func=getInfo, methods=['GET'])