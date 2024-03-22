from flask import (
    request, 
    jsonify
)

from sqlalchemy import cast, Date
from app.user.models import User, Log
from datetime import datetime
from app import db

def getInfo():
    infoType = request.args.get('type')
    date = request.args.get('date')

    if not date or not infoType:
        return jsonify({"error": "invalid request"}), 400

    date_obj = datetime.strptime(date, '%d-%m-%Y').date()
    
    if infoType == "1":
        users = db.session.query(User).filter(cast(User.created_at, Date) == date_obj).all()
        users_list = [{'id': user.id, 'name': user.name, 'created_at': user.created_at} for user in users]

        return jsonify({"date": date, "info": users_list}), 200
    elif infoType == "2":
        logs = db.session.query(Log).filter(cast(Log.time, Date) == date_obj).all()
        users_list = [{'id': log.user_id, 'accessed_at': log.time} for log in logs]
        return jsonify({"date": date, "info": users_list}), 200
    else:
        return jsonify({"error": "invalid request"}), 400
