from flask import (
    request, 
    jsonify
)
from sqlalchemy import cast, Date
from app.user.models import User, Log
from datetime import datetime
from app import db
from datetime import datetime, timedelta
from app.utils.app_functions import send_email
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
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    inactive_users = db.session.query(User.name, User.email).filter(User.last_active < twenty_four_hours_ago).distinct().all()
    Thread(target=sendAlerts(inactive_users)).start()
    return jsonify({"message": f"sending inactivity alerts to {len(inactive_users)}"}), 200
    
def sendAlerts(inactive_users):
    for user in inactive_users:
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
                <p>Hey <b>{user.name}</b> 👋,</p>
                <p>It has been awhile since you've been on ConnectKGP, we've missed having you around.</p>
                <p>See what you've been missing or kindly let us know how we can help.</p>
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
        send_email(user.email, "We miss you on ConnectKGP 😢", email_body)
    return