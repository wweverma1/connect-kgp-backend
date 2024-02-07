from flask import (
    request, 
    jsonify
)
import bcrypt
from app import db
from app.user.models import User
from app.otp.models import OTP
from app.feed.models import Feed
from app.utils.app_functions import send_email
from datetime import datetime
import traceback
from sqlalchemy.exc import SQLAlchemyError

def signup():
    name = request.form['name']
    email = request.form['email']

    is_email_registered = db.session.query(User).filter_by(email=email).count()
    if is_email_registered != 0:
        return jsonify({"error": "An account already exists with this email"}), 400
    
    otp = OTP.generate_otp(email)
    if not otp:
        return jsonify({"error": "Couldn't generate OTP"}), 500    
    email_body = f"Hello {name},\n\nWe are glad to have you on board.\nUse the below given 5 digit OTP for completing your registration-\n\n{otp.code}\n\nRegards,\nConnectKGP\nMade with ❤️ in KGP for KGP"
    if send_email(email, "Welcome to ConnectKGP 👋", email_body):
        return jsonify({"message": "OTP sent for verification", "otp_id": otp.id}), 200
    else:
        return jsonify({"error": "Couldn't send email"}), 500

def signin():
    email = request.form['email']
    password = request.form['password']
    
    user = db.session.query(User).filter(User.email == email).one_or_none()
    if not user:
        return jsonify({"error": "No account registered with this email address"}), 400
    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({"user_id": user.id}), 200
    else:
        return jsonify({"error": "Incorrect Password, Unable to Login"}), 400
    
def verify():
    otp_id = request.form['otp_id']
    user_otp = request.form['user_otp']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['birthdate']
    
    otp = db.session.query(OTP).filter_by(id=otp_id, created_for=email).first()
    
    if otp and otp.expiry >= datetime.utcnow() and otp.code == user_otp:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.create_user(name, email, dob, hashed_password)
        if not user:
            return jsonify({"error": "Some error occured while creating account"}), 500
        return jsonify({"user_id": user.id}), 200
    else:
        return jsonify({"error": "Incorrect OTP, Unable to Verify"}), 400
    
def getFeeds():
    feeds = db.session.query(Feed).all()
    feeds_list = []

    for feed in feeds:
        feed_data = {
            'id': feed.id,
            'created_at': feed.created_at,
            'content': feed.content,
            'rating': feed.rating,
            'liked_by': feed.liked_by,
            'disliked_by': feed.disliked_by
        }
        feeds_list.append(feed_data)

    return jsonify({"feeds": feeds_list}), 200

def postFeed():
    content = request.form['content']

    feed = Feed.post_feed(content.strip())
    if not feed:
        return jsonify({"error": "Some error occured while posting your status"}), 500
    return jsonify({"message": "Status posted"}), 200

def voteFeed():
    feed_id = request.form['feed_id']
    vote = int(request.form['vote'])
    user_id = request.form['user_id']

    try:
        feed = db.session.query(Feed).filter_by(id=feed_id).one_or_none()
        if not feed:
            return jsonify({"error": "Invalid feed"}), 400

        if vote == 1:
            if user_id in feed.disliked_by:
                feed.disliked_by.remove(user_id)
                feed.liked_by.append(user_id)
                feed.rating += 2
            elif user_id in feed.liked_by:
                feed.liked_by.remove(user_id)
                feed.rating -= 1
            else:
                feed.liked_by.append(user_id)
                feed.rating += 1
        elif vote == -1:
            if user_id in feed.liked_by:
                feed.liked_by.remove(user_id)
                feed.disliked_by.append(user_id)
                feed.rating -= 2
            elif user_id in feed.disliked_by:
                feed.disliked_by.remove(user_id)
                feed.rating += 1
            else:
                feed.disliked_by.append(user_id)
                feed.rating -= 1
        else:
            return jsonify({"error": "Invalid vote value"}), 400

        db.session.commit()
        return jsonify({"message": "Feed voted"}), 200

    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Couldn't vote feed"}), 500

    