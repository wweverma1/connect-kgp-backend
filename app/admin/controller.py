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
        return jsonify({"date": date, "info": users}), 200
    elif infoType == "2":
        users = db.session.query(Log).filter(cast(Log.time, Date) == date_obj).all()
        return jsonify({"date": date, "info": users}), 200
    else:
        return jsonify({"error": "invalid request"}), 400
