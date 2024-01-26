from flask import (
    request, 
    jsonify
)
import random
from app.user.models import User
from app.utils.app_functions import send_email

def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['birthdate']

    if User.is_email_registered(email):
        return jsonify({"error": "An account already exists with this email"}), 400
    
    otp = str(random.randint(10000, 99999))
    email_body = f"Hello {name},\n\nWe are glad to have you on board.\nUse this 5-digit OTP for completing your registration-\n\n{otp}\n\nThanks,\nConnectKGP\nMade with ❤️ in KGP for KGP"
    if send_email(email, "Welcome to ConnectKGP 👋", email_body):
        return jsonify({"message": "OTP sent for verification"}), 200
    else:
        return jsonify({"error": "Couldn't send email"}), 500

def signin():
    email = request.form['email']
    password = request.form['password']
    print(email, password)
    return jsonify({"result": "Information sent"}), 200