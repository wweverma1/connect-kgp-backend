from flask import (
    request, 
    jsonify
)
from sqlalchemy import cast, Date, and_
from app.user.models import User, Log
from datetime import datetime
from app import app, db
from datetime import datetime, timedelta
from app.utils.app_functions import send_email, send_bcc_email
from threading import Thread

def getInfo():
    infoType = request.args.get('type')
    date = request.args.get('date')

    if not date or not infoType:
        return jsonify({"error": "invalid request"}), 400

    date_obj = datetime.strptime(date, '%d-%m-%Y').date()
    
    if infoType == "1":
        users = db.session.query(User).filter(cast(User.created_at, Date) == date_obj).all()
        users_list = [{'id': user.id, 'name': user.name, 'email': user.email, 'created_at': user.created_at} for user in users]

        return jsonify({"date": date, "info": users_list}), 200
    elif infoType == "2":
        logs = db.session.query(Log).filter(cast(Log.time, Date) == date_obj).all()
        users_list = [{'id': log.user_id, 'accessed_at': log.time} for log in logs]
        return jsonify({"date": date, "info": users_list}), 200
    else:
        return jsonify({"error": "invalid request"}), 400
    
def sendInactivityAlerts():
    five_days_ago = datetime.now() - timedelta(days=5)
    one_day_ago = datetime.now() - timedelta(days=1)
    inactive_users = db.session.query(User.id, User.name, User.email).filter(and_(User.last_active < five_days_ago, (User.last_promotional_mail.is_(None) | (User.last_promotional_mail < one_day_ago)))).distinct().all()
    if inactive_users:
        sendAlerts(inactive_users)
        return jsonify({"message": f"sending inactivity alerts to {len(inactive_users)} users"}), 200
    else:
        return jsonify({"message": "no user found"}), 400
    
def sendAlerts(inactive_users):
    recipients = [user.email for user in inactive_users]
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
            <p>It has been awhile since you've been on ConnectKGP, we've missed having you around.</p>
            <p>See what you've been missing or kindly let us know how we can improve.</p>
            <div style="text-align: center; margin: 20px">
                <a href="https://connectkgp.netlify.app/" target="_blank" style="font-weight: bold; background-color: #6559a2; padding: 10px; color: white; text-decoration: none;">Sign in Now</a>
            </div>
            </div>
            <p>Regards 🤗 <br>
            <br>
            <b style="color: #6559a2;">ConnectKGP</b>
            <br>Made with ❤️ in KGP for KGP
            </p>
        </body>
        </html>
    """    
    if send_bcc_email(recipients, "We miss you on ConnectKGP", email_body):
        for user in inactive_users:
            updateUser = db.session.query(User).filter(User.email in recipients).one_or_none()
            if updateUser:
                updateUser.last_promotional_mail = datetime.now()
                db.session.commit()