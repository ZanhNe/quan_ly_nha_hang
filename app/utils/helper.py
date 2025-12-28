import datetime
import jwt
from abc import ABC, abstractmethod
from app.extentions.extentions import bcrypt, mail
from flask_mail import Message
from threading import Thread
from flask import current_app

class IHelper(ABC):
    """
    Interface định nghĩa các hàm tiện ích (Helper) dùng trong hệ thống.
    """
    @abstractmethod
    def hass_pass(self, plain: str) -> str:
        """Băm mật khẩu."""
        pass
    
    @abstractmethod
    def check_pass(self, plain: str, hashed_pass: str) -> bool:
        """Kiểm tra mật khẩu khớp hay không."""
        pass

    @abstractmethod
    def generate_token(self, email: str, type='verify') -> str:
        """Tạo token JWT phục vụ xác thực hoặc reset pass."""
        pass

    @abstractmethod
    def verify_token(self, token: str, type='verify'):
        """Giải mã và kiểm tra token JWT."""
        pass

    @abstractmethod
    def send_verification_email(self, user_email, token):
        """Gửi email chứa link xác nhận tài khoản."""
        pass

    @abstractmethod
    def send_async_email(self, app_instance, msg):
        """Hàm chạy ngầm (thread) để gửi email không gây block main thread."""
        pass

class Helper(IHelper):
    """
    Lớp triển khai cụ thể các hàm bổ trợ bằng thư viện Flask-Bcrypt, PyJWT, v.v.
    """

    def hass_pass(self, plain: str) -> str:
        return bcrypt.generate_password_hash(plain).decode('utf-8')

    def check_pass(self, plain, hashed_pass: str) -> bool:
        return bcrypt.check_password_hash(hashed_pass, plain)
    
    def generate_token(self, email: str, type='verify', expired_minutes: int = 15) -> str:
        payload = {
            'sub': email,
            'type': type,
            'exp': datetime.datetime.now() + datetime.timedelta(minutes=expired_minutes),
            'iat': datetime.datetime.now()
        }

        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    
    def verify_token(self, token: str, type='verify'):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], options={"verify_iat": False})
            
            if payload['type'] != type:
                return None
            
            return payload['sub'] # Trả về email nếu token hợp lệ
        except jwt.ExpiredSignatureError as err:
            raise err
        except jwt.InvalidTokenError as err:
            raise err
        
    def send_async_email(self, app_instance, msg):
        with app_instance.app_context():
            try:
                mail.send(msg)
                print("Hệ thống: Đã gửi email thành công trong background!")
            except Exception as e:
                print(f"Hệ thống: Lỗi gửi email: {e}")

    def send_verification_email(self, user_email, token):
        msg = Message('Xác thực tài khoản Sakura Restaurant',
                    sender='noreply@sakura.com',
                    recipients=[user_email])
        
        link = f"http://127.0.0.1:5000/auth/verify?token={token}"
        msg.body = f"Chào mừng bạn đến với Sakura! Vui lòng nhấn vào link sau để xác minh tài khoản: {link}"

        app_instance = current_app._get_current_object()
        
        thr = Thread(target=self.send_async_email, args=(app_instance, msg))
        thr.start()
        
        return "Email xác thực đang được gửi đi..."

def is_near(tg_str: str):
    """
    Kiểm tra xem mốc thời gian 'tg_str' (định dạng ISO) có còn lại dưới 30 phút so với hiện tại không.
    """
    if not tg_str:
        return False
    tnow = datetime.datetime.now()
    try:
        tg_date = datetime.datetime.strptime(tg_str, "%Y-%m-%dT%H:%M:%S")
        duration = tg_date - tnow
        return duration <= datetime.timedelta(minutes=30)
    except:
        return False
