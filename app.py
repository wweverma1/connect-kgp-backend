from app import app
from flask import request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from app.user.models import User
from app import db
import traceback
from sqlalchemy.exc import SQLAlchemyError

CORS(app, origins='*')
socketio = SocketIO(app, cors_allowed_origins='*')

idleUsers = []
matches = {}

def handle_idle(user_id):
    global idleUsers
    global matches

    idleUsers.append(user_id)
    if len(idleUsers) > 1:
        matched_user_1 = idleUsers.pop(0)
        matched_user_2 = idleUsers.pop(0)
        print("** match **\t", matched_user_1, " - ", matched_user_2)
        matches[matched_user_1] = matched_user_2
        matches[matched_user_2] = matched_user_1
        socketio.emit('match', {'user_id': matched_user_2}, to=matched_user_1)
        socketio.emit('match', {'user_id': matched_user_1}, to=matched_user_2)

@socketio.on('connect')
def handle_connect():
    global idleUsers
    global matches

    user_id = request.sid

    print("** user joined **\t", user_id)

    if len(idleUsers):
        match_id = idleUsers.pop(0)
        print("** match **\t", user_id, " - ", match_id)
        matches[user_id] = match_id
        matches[match_id] = user_id
        socketio.emit('match', {'user_id': match_id}, to=user_id)
        socketio.emit('match', {'user_id': user_id}, to=match_id)
    else:
        handle_idle(user_id)

@socketio.on('message')
def handle_chat_message(message):
    global idleUsers
    global matches

    socketio.emit('message', message, to=matches[request.sid])

@socketio.on('disconnect')
def handle_disconnect():
    global idleUsers
    global matches

    user_id = request.sid

    if user_id in idleUsers:
        idleUsers.remove(user_id)
    else:
        match_id = matches[user_id]
        socketio.emit('unmatch', to=match_id)
        del matches[user_id]
        del matches[match_id]
        handle_idle(match_id)

@socketio.on('report')
def handle_report(user_id):
    user = db.session.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        return
    try:
        user.rating -= 1
        db.session.commit()
    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)