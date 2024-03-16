from flask import (
    request, 
    jsonify
)
import bcrypt
from sqlalchemy import desc
from app import db
from app.user.models import User
from app.otp.models import OTP
from app.feed.models import Feed
from app.utils.app_functions import send_email
from datetime import datetime
import traceback
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
    
def signup():
    name = request.form['name'].strip()
    email = request.form['email'].strip()

    if not email.endswith("iitkgp.ac.in") and not email.endswith("gmail.com"):
        return jsonify({"error": "Please use an appropriate email address"}), 400
    
    is_email_registered = db.session.query(User).filter_by(email=email).count()
    if is_email_registered != 0:
        return jsonify({"error": "An account already exists with this email"}), 400
    
    otp = OTP.generate_otp(email)
    if not otp:
        return jsonify({"error": "Couldn't generate OTP"}), 500
    email_body = f"""\
        <html>
        <body>
            <div style="text-align: center;">
                <div style="margin: auto;">
                    <img src='https://connectkgp.netlify.app/images/connectkgp.png' alt='connectkgp icon' style="height: 22px;" />
                    <span style="font-weight: bold; font-size: 32px; color: #6559a2;">ConnectKGP</span>
                </div>
                <span style="font-size: 14px;">KGP ka apna pseudonymous social network</span>
            </div>
            <hr>
            <div>
                <p>Hello {name} 👋,</p>
                <p>We are glad to have you on-board.</p>
                <p>Use the below given 5 digit OTP for completing your registration-</p>
                <div style="text-align: center; margin: 20px">
                    <span style="font-weight: bold; background-color: #6559a2; padding: 10px; color: white; letter-spacing: 5px;">{otp.code}</a>
                </div>
            </div>
            <p>Regards 🤗<br><br>
                <b style="color: #6559a2;">ConnectKGP</b><br>Made with ❤️ in KGP for KGP
            </p>
        </body>
        </html>
    """    
    if send_email(email, "Welcome to ConnectKGP 👋", email_body):
        return jsonify({"message": "OTP sent for verification", "otp_id": otp.id}), 200
    else:
        return jsonify({"error": "Couldn't send email"}), 500

def signin():
    email = request.form['email'].strip()
    password = request.form['password']
    
    user = db.session.query(User).filter(User.email == email).one_or_none()
    if not user:
        return jsonify({"error": "No account registered with this email address"}), 400
    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({"user_id": user.id, "username": user.name }), 200
    else:
        return jsonify({"error": "Incorrect Password, Unable to Login"}), 400
    
def verify():
    otp_id = request.form['otp_id']
    user_otp = request.form['user_otp']
    name = request.form['name'].strip().title()
    email = request.form['email'].strip()
    password = request.form['password']
    
    otp = db.session.query(OTP).filter_by(id=otp_id, created_for=email).first()
    
    if otp and otp.expiry >= datetime.utcnow() and otp.code == user_otp:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.create_user(name, email, hashed_password)
        if not user:
            return jsonify({"error": "Some error occured while creating account"}), 500
        return jsonify({"user_id": user.id, "username": user.name }), 200
    else:
        return jsonify({"error": "Incorrect OTP, Unable to Verify"}), 400

def get_feed_data(feed):
    sorted_children = sorted(feed.children, key=lambda child: child.created_at)
    sorted_children_data = [get_feed_data(child) for child in sorted_children]

    return {
        "id": feed.id,
        "created_at": feed.created_at,
        "content": feed.content,
        "icon": feed.icon,
        "liked_by": feed.liked_by,
        "disliked_by": feed.disliked_by,
        "children": sorted_children_data
    }

def getFeeds():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    feeds = (
        db.session.query(Feed)
        .filter(Feed.created_at >= twenty_four_hours_ago, Feed.parent_feed_id.is_(None))
        .order_by(Feed.created_at)
        .all()
    )

    response_data = {"feeds": [get_feed_data(feed) for feed in feeds]}
    return jsonify(response_data)

def postFeed():
    user_id = request.form['uid']
    content = request.form['content']
    icon = request.form['icon']
    parent_feed_id = request.form.get('parent_feed_id')

    feed = Feed.post_feed(user_id, content.strip(), icon, parent_feed_id)
    if not feed:
        return jsonify({"error": "Some error occurred while posting your status"}), 500
    return jsonify({"message": "Status posted"}), 200

def voteFeed():
    feed_id = request.form['feed_id']
    vote = int(request.form['vote'])
    user_id = int(request.form['user_id'])

    try:
        feed = db.session.query(Feed).filter_by(id=feed_id).one_or_none()
        if not feed:
            return jsonify({"error": "Invalid feed"}), 400
        if vote == 1:
            if user_id in feed.disliked_by:
                feed.disliked_by.remove(user_id)
                feed.liked_by.append(user_id)
            elif user_id in feed.liked_by:
                feed.liked_by.remove(user_id)
            else:
                feed.liked_by.append(user_id)
        elif vote == -1:
            if user_id in feed.liked_by:
                feed.liked_by.remove(user_id)
                feed.disliked_by.append(user_id)
            elif user_id in feed.disliked_by:
                feed.disliked_by.remove(user_id)
            else:
                feed.disliked_by.append(user_id)
        else:
            return jsonify({"error": "Invalid vote value"}), 400

        db.session.commit()
        return jsonify({"message": "Feed voted"}), 200

    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Couldn't vote feed"}), 500
    
def findUser():
    user_email = request.args.get('email')

    try:
        user = db.session.query(User).filter_by(email=user_email).one_or_none()
        if not user:
            return jsonify({"error": "Invalid email address"}), 400
        
        otp = OTP.generate_otp(user.email)
        if not otp:
            return jsonify({"error": "Couldn't generate OTP"}), 500   
        email_body = f"""\
            <html>
            <body>
                <div style="text-align: center;">
                    <div style="margin: auto;">
                        <img src='https://connectkgp.netlify.app/images/connectkgp.png' alt='connectkgp icon' style="height: 22px;" />
                        <span style="font-weight: bold; font-size: 32px; color: #6559a2;">ConnectKGP</span>
                    </div>
                    <span style="font-size: 14px;">KGP ka apna pseudonymous social network</span>
                </div>
                <hr>
                <div>
                    <p>Hello {user.name} 👋,</p>
                    <p>It appears you are having a problem signing in.</p>
                    <p>Use the below given 5 digit OTP to proceed-</p>
                    <div style="text-align: center; margin: 20px">
                        <span style="font-weight: bold; background-color: #6559a2; padding: 10px; color: white; letter-spacing: 5px;">{otp.code}</a>
                    </div>
                </div>
                <p>Regards 🤗<br><br>
                    <b style="color: #6559a2;">ConnectKGP</b><br>Made with ❤️ in KGP for KGP
                </p>
            </body>
            </html>
        """ 
        if send_email(user.email, "Forgot your password? ConnectKGP", email_body):
            return jsonify({"message": "OTP sent for verification", "otp_id": otp.id, "user_id": user.id}), 200
        else:
            return jsonify({"error": "Couldn't send email"}), 500

    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Couldn't find user"}), 500
    
def verifyUser():
    otp_id = request.form['otp_id']
    user_otp = request.form['user_otp']

    otp = db.session.query(OTP).filter_by(id=otp_id).first()
    
    if otp and otp.expiry >= datetime.utcnow() and otp.code == user_otp:
        return jsonify({"message": "otp validated"}), 200
    else:
        return jsonify({"error": "Incorrect OTP, Unable to Verify"}), 400
    
def updatePassword():
    user_id = request.form['user_id']
    password = request.form['password']

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        user = db.session.query(User).filter_by(id=user_id).one_or_none()
        if not user:
            return jsonify({"error": "Invalid user id"}), 400

        user.password = hashed_password
        db.session.commit()
        return jsonify({"user_id": user_id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

def reportUser():
    user_id = request.args.get('uid')

    user = db.session.query(User).filter_by(id=user_id).one_or_none()
    if user:
        try:
            user.rating -= 1
            db.session.commit()
            return jsonify({"message": "user reported"}), 200
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return jsonify({"error": "couldn't report user"}), 500
    else:
        return jsonify({"error": "user not found"}), 400

def addFriend():
    uid = request.form['user_id']
    fid = request.form['friend_id']

    user = db.session.query(User).filter_by(id=uid).one_or_none()
    friend = db.session.query(User).filter_by(id=fid).one_or_none()

    if user and friend:
        if fid in user.friends:
            return jsonify({"message": "You are already friends with this user"}), 400
        else:
            try:
                user.friends.append(fid)
                friend.friends.append(uid)
                db.session.commit()
                return jsonify({"message": "friend added"}), 200
            except SQLAlchemyError as e:
                print(e)
                traceback.print_exc()
                db.session.rollback()
                return jsonify({"error": "couldn't add friend"}), 500
    else:
        return jsonify({"error": "user/users not found"}), 400
    
def getFriends():
    user_id = request.args.get('uid')

    try:
        user = db.session.query(User).filter_by(id=user_id).one_or_none()
        if user:
            friends = User.query.filter(User.id.in_(user.friends)).all()
            friend_list = [{'id': friend.id, 'name': friend.name} for friend in friends]
            return jsonify({'friends': friend_list}), 200
        else:
            return jsonify({'error': 'user not found'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def removeFriend():
    try:
        uid = int(request.form['user_id'])
        fid = int(request.form['friend_id'])

        user = db.session.query(User).filter_by(id=uid).one_or_none()
        friend = db.session.query(User).filter_by(id=fid).one_or_none()

        if user and friend:
            try:
                user.friends.remove(fid)
                friend.friends.remove(uid)
                db.session.commit()
                return jsonify({"message": "Friend removed"}), 200
            except SQLAlchemyError as e:
                print(e)
                traceback.print_exc()
                db.session.rollback()
                return jsonify({"error": "Couldn't remove friend"}), 500
        else:
            return jsonify({"error": "User/users not found"}), 400

    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({"error": "Invalid input"}), 400
    
def sendInvite():
    username = request.form['username']
    email = request.form['email'].strip()
      
    email_body = f"""\
        <html>
        <body>
            <div style="text-align: center;">
                <div style="margin: auto;">
                    <img src='https://connectkgp.netlify.app/images/connectkgp.png' alt='connectkgp icon' style="height: 22px;" />
                    <span style="font-weight: bold; font-size: 32px; color: #6559a2;">ConnectKGP</span>
                </div>
                <span style="font-size: 14px;">KGP ka apna pseudonymous social network</span>
            </div>
            <hr>
            <div>
                <p>Hello 👋,</p>
                <p><b>{username}</b> has invited you to join <b style="color: #6559a2;">ConnectKGP</b>, KGP ka apna pseudonymous social network.</p>
                <p>We're excited to have you join us!</p>
                <p>To get started, just click the button below to connect with KGP-</p>
                <div style="text-align: center; margin: 20px">
                    <a href="https://connectkgp.netlify.app/" target="_blank" style="font-weight: bold; background-color: #6559a2; padding: 10px; color: white; text-decoration: none;">Accept Invite</a>
                </div>
            </div>
            <p>Regards 🤗<br><br>
                <b style="color: #6559a2;">ConnectKGP</b><br>Made with ❤️ in KGP for KGP
            </p>
        </body>
        </html>
    """
    if send_email(email, "Yayy! You have been invited", email_body):
        return jsonify({ "message": "invitation sent" }), 200
    else:
        return jsonify({"error": "Couldn't send invitation"}), 500




