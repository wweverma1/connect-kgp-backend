from app import app
from flask import request, session
from flask_socketio import SocketIO, emit
from app.user.models import User
from app import db
import traceback
from sqlalchemy.exc import SQLAlchemyError

socketio = SocketIO(app, cors_allowed_origins='*')

idleUsers = set()
idleAudioUsers = set()
matches = {}

class UserData:
    def __init__(self, user_id, chat_type, uid):
        self.user_id = user_id
        self.chat_type = chat_type
        self.uid = uid

def get_user_data(user_id):
    user_data_dict = session.get('user_data', {})
    return user_data_dict.get(user_id)

def handle_idle(user_id, chatType):
    global idleUsers
    global idleAudioUsers
    global matches

    if chatType == "voice":
        idleAudioUsers.add(user_id)
        if len(idleAudioUsers) > 1:
            matched_user_1 = idleAudioUsers.pop()
            matched_user_2 = idleAudioUsers.pop()
            if matched_user_1 != matched_user_2:
                print("** match **\t", matched_user_1, " - ", matched_user_2)
                matches[matched_user_1] = matched_user_2
                matches[matched_user_2] = matched_user_1
                socketio.emit('match', {'user_id': matched_user_2}, to=matched_user_1)
    else:
        idleUsers.add(user_id)
        if len(idleUsers) > 1:
            matched_user_1 = idleUsers.pop()
            matched_user_2 = idleUsers.pop()
            if matched_user_1 != matched_user_2:
                print("** match **\t", matched_user_1, " - ", matched_user_2)
                matches[matched_user_1] = matched_user_2
                matches[matched_user_2] = matched_user_1
                socketio.emit('match', {'user_id': matched_user_2}, to=matched_user_1)
                socketio.emit('match', {'user_id': matched_user_1}, to=matched_user_2)

@socketio.on('connection')
def handle_connection(chatType, uid):
    global idleUsers
    global idleAudioUsers
    global matches

    user_id = request.sid

    print("** user joined **\t", user_id, chatType)
    
    user_data = UserData(user_id, chatType, uid)
    session['user_data'] = {user_data.user_id: user_data}
    
    if chatType == "voice":
        if idleAudioUsers:
            match_id = idleAudioUsers.pop()
            if user_id != match_id:
                print("** match **\t", user_id, " - ", match_id)
                matches[user_id] = match_id
                matches[match_id] = user_id
                socketio.emit('match', {'user_id': match_id}, to=user_id)
        else:
            handle_idle(user_id, chatType)
    else:
        if idleUsers:
            match_id = idleUsers.pop()
            if user_id != match_id:
                print("** match **\t", user_id, " - ", match_id)
                matches[user_id] = match_id
                matches[match_id] = user_id
                socketio.emit('match', {'user_id': match_id}, to=user_id)
                socketio.emit('match', {'user_id': user_id}, to=match_id)
        else:
            handle_idle(user_id, chatType)

@socketio.on('callUser')
def handle_call_user(signal):
    global matches 
    print('received call from ', request.sid)
    match_id = matches[request.sid]
    socketio.emit('callUser', { 'signal': signal, 'match_id': match_id }, to=matches[request.sid])

@socketio.on('answerCall')
def handle_answer_call(signal):
    global matches
    print('received answered by ', request.sid)
    socketio.emit('callAccepted', signal, to=matches[request.sid])

@socketio.on('message')
def handle_chat_message(message):
    global idleUsers
    global matches

    socketio.emit('message', message, to=matches[request.sid])

@socketio.on('disconnect')
def handle_disconnect():
    global idleUsers
    global matches
    global idleAudioUsers

    user_id = request.sid
    user_data = get_user_data(user_id)
    chatType = user_data.get('chat_type', None)

    print("** user left **\t", user_id, chatType)

    if chatType == "voice":
        if user_id in idleAudioUsers:
            idleAudioUsers.remove(user_id)
        else:
            match_id = matches[user_id]
            socketio.emit('unmatch', to=match_id)
            del matches[user_id]
            del matches[match_id]
            handle_idle(match_id, chatType)
    elif chatType == "text":
        if user_id in idleUsers:
            idleUsers.remove(user_id)
        else:
            match_id = matches[user_id]
            socketio.emit('unmatch', to=match_id)
            del matches[user_id]
            del matches[match_id]
            handle_idle(match_id, chatType)
    else:
        print("invalid chat type")

@socketio.on('report')
def handle_report():
    user_id = request.sid
    match_id = matches[user_id]
    report_user_data = get_user_data(match_id)
    print("reporting user: ", report_user_data.uid)
    user = db.session.query(User).filter_by(id=report_user_data.uid).one_or_none()
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
    global idleUsers
    global matches
    global idleAudioUsers

    user_id = request.sid
    match_id = matches[user_id]
    socketio.emit('unmatch', to=match_id)
    del matches[user_id]
    del matches[match_id]
    handle_idle(match_id, 'voice')
    handle_idle(user_id, 'voice')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
