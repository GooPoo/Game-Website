from app import socketio
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user

@socketio.on('join_game')
def handle_join_game(data):
    room = data.get('room')
    join_room(room)
    emit('user_joined', {'user': current_user.username}, to=room)

@socketio.on('leave_game')
def handle_leave_game(data):
    room = data.get('room')
    leave_room(room)
    emit('user_left', {'user': current_user.username}, to=room)

@socketio.on('message')
def handle_message(message):
    print('Received message: ' + message)
    emit('response', {'data': 'Echo: ' + message})
