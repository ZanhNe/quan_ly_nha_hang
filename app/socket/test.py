# events.py
from flask import request
from flask_socketio import emit, join_room, leave_room
from app.extentions.extentions import socketio

# 1. Sự kiện kết nối (Mặc định)
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Có thể xác thực user ở đây nếu cần

# 2. Sự kiện ngắt kết nối (Mặc định)
@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

# 3. Sự kiện: Tham gia phòng (Ví dụ: Vào trang chi tiết đơn hàng #123)
@socketio.on("join_room")
def on_join(data):
    room = data.get('room')
    username = data.get('username')
    
    join_room(room) # Gom socket này vào phòng
    
    # Gửi thông báo cho mọi người TRONG PHÒNG đó (trừ người gửi)
    emit("notification", f"{username} đã vào phòng.", to=room, include_self=False)

# 4. Sự kiện: Gửi tin nhắn / Cập nhật trạng thái
@socketio.on("send_message")
def handle_message(data):
    room = data.get('room')
    msg = data.get('message')
    username = data.get('username')

    print(f"Nhận tin từ {username} tại phòng {room}: {msg}")

    # Gửi lại tin nhắn cho TẤT CẢ mọi người trong phòng
    emit("receive_message", {
        "user": username,
        "msg": msg
    }, to=room)