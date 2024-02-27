from app import app
from flask import request, session
from flask_socketio import SocketIO, emit
from app.user.models import User
from app import db
import traceback
from sqlalchemy.exc import SQLAlchemyError
import random

socketio = SocketIO(app, cors_allowed_origins='*')

users = {}
available_users = {'text': set(), 'voice': set()}

def matchmake(user_sid, chatType):
    available_users[chatType].add(user_sid)

    if len(available_users[chatType] >= 2):
        match_sid = random.choice(list(available_users[chatType] - {user_sid}))

        users[user_sid]['match_sid'] = match_sid
        users[match_sid]['match_sid'] = user_sid

        if chatType == "text":
            socketio.emit('match', {'user_id': match_sid}, to=user_sid)
            socketio.emit('match', {'user_id': user_sid}, to=match_sid)
        else:
            if random.choice([user_sid, match_sid]) == user_sid:
                socketio.emit('match', {'user_id': match_sid}, to=user_sid)
            else:
                socketio.emit('match', {'user_id': user_sid}, to=match_sid)

        available_users[chatType].remove(user_sid)
        available_users[chatType].remove(match_sid)

@socketio.on('connection')
def handle_connection(data):
    user_sid = request.sid
    chatType = data.get('chat_type')
    user_id = data.get('uid')

    if user_id is not None:
        print("** user joined **\t", user_sid, chatType, user_id)

        users[user_sid] = {
            'user_id': user_id,
            'chat_type': chatType,
            'match_sid': None
        }
        matchmake(user_sid, chatType)

@socketio.on('callUser')
def handle_call_user(signal):
    match_sid = users[request.sid]['match_sid']
    socketio.emit('callUser', { 'signal': signal, 'match_id': request.sid }, to=match_sid)

@socketio.on('answerCall')
def handle_answer_call(signal):
    socketio.emit('callAccepted', signal, to=users[request.sid]['match_sid'])

@socketio.on('message')
def handle_chat_message(message):
    socketio.emit('message', message, to=users[request.sid]['match_sid'])

@socketio.on('disconnect')
def handle_disconnect():
    user_sid = request.sid
    chatType = users[user_sid]['chat_type']
    match_sid = users[user_sid]['match_sid']
    if match_sid is not None:
        print("** user left **\t", user_sid, chatType, "not-idle")
        users[match_sid]['match_sid'] = None
        socketio.emit('unmatch', to=match_sid)
        matchmake(match_sid, chatType)
    else:
        print("** user left **\t", user_sid, chatType, "idle")
    del users[user_sid]

@socketio.on('report')
def handle_report():
    user_sid = request.sid
    match_sid = users[user_sid]['match_sid']
    match_uid = users[match_sid]['user_id']

    print("** reporting user **\t", match_uid)
    user = db.session.query(User).filter_by(id=match_uid).one_or_none()
    if user:
        try:
            user.rating -= 1
            db.session.commit()
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
    
@socketio.on('shuffleCall')
def shuffleCall():
    user_sid = request.sid
    match_sid = users[user_sid]['match_sid']
    
    socketio.emit('unmatch', to=match_sid)
    
    users[user_sid]['match_sid'] = None
    users[match_sid]['match_sid'] = None
    
    matchmake(user_sid, "voice")
    matchmake(match_sid, "voice")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
