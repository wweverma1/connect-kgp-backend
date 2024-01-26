# Standard library imports
import time
from datetime import datetime
# import os
import logging

# Related third party imports
from flask import request
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# Local app specific imports
from app import app

# Move configuration settings to environment variables
# EMAIL_SERVER = os.environ.get('EMAIL_SERVER', 'smtp.example.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'username')
# EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'password')


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if request.endpoint:
        end_time = time.time()
        latency = int((end_time - request.start_time) * 1000)
        print(f'[ {str(datetime.now())} ] endpoint {request.endpoint} latency {latency} req_id {request.environ.get("FLASK_REQUEST_ID")}')
    return response