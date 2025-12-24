# events.py
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from app.extentions.extentions import socketio

users = {}

@socketio.on("connect")
def handle_connect():
    user_id = session.get('current_user')['user_id']
    users[user_id] = request.sid
    print(f"Client connected: {request.sid}")
    

@socketio.on("disconnect")
def handle_disconnect():
    user_id = session.get('current_user')['user_id']
    users.pop(user_id)

