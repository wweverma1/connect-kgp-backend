from flask import Blueprint

from app.admin.controller import (
    getInfo,
    sendInactivityAlerts
)

admin_api = Blueprint('admin', __name__)

admin_api.add_url_rule(rule='/get-info', view_func=getInfo, methods=['GET'])
admin_api.add_url_rule(rule='/inactivity-alert', view_func=sendInactivityAlerts, methods=['GET'])
