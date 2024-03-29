# Standard library imports
import time
from datetime import datetime

# import os
import os

# Related third party imports
from flask import request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Local app specific imports
from app import app

sender_email = os.getenv("EMAIL")
sender_password = os.getenv("EMAIL_PASS")

@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if request.endpoint:
        end_time = time.time()
        latency = int((end_time - request.start_time) * 1000)
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        print(f'[ {str(datetime.now())} ] endpoint {request.endpoint} latency {latency} req_id {request.environ.get("FLASK_REQUEST_ID")}')
    return response

def send_email(recipient_email, subject, body):
    try:
        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f'Email Sending Failed: {str(e)}')
        return False
    
def send_bcc_email(recipients, subject, body):
    try:
        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['Bcc'] = ', '.join(recipients)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, message.as_string())
        return True
    except Exception as e:
        print(f'Email Sending Failed: {str(e)}')
        return False