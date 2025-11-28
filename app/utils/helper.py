#Chứa các function hỗ trợ
import datetime
import jwt
from abc import ABC, abstractmethod
from app.extentions.extentions import bcrypt, mail
from flask_mail import Message
from threading import Thread
from flask import current_app



class IHelper(ABC):
    @abstractmethod
    def hass_pass(self, plain: str) -> str:
        pass
    
    @abstractmethod
    def check_pass(self, plain: str, hashed_pass: str) -> bool:
        pass

    @abstractmethod
    def generate_token(self, email: str, type='verify') -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str, type='verify'):
        pass

    @abstractmethod
    def send_verification_email(self, user_email, token):
        pass

    @abstractmethod
    def send_async_email(self, app_instance, msg):
        pass

class Helper(IHelper):

    def hass_pass(self, plain: str) -> str:
        # Trả về chuỗi bytes, cần decode utf-8 để lưu vào Database dạng String
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
            
            return payload['sub'] #Email
        except jwt.ExpiredSignatureError as err:
            raise err
        except jwt.InvalidTokenError as err:
            raise err
        
    def send_async_email(self, app_instance, msg):
    # Cực kỳ quan trọng: Phải nạp context thủ công thì mới đọc được config
        with app_instance.app_context():
            try:
                mail.send(msg)
                print("Đã gửi email thành công trong background!")
            except Exception as e:
                print(f"Lỗi gửi email: {e}")

    def send_verification_email(self, user_email, token):
        # Tạo nội dung email
        msg = Message('Xác thực tài khoản',
                    sender='noreply@your-app.com',
                    recipients=[user_email])
        
        link = f"http://localhost:5000/auth/verify?token={token}"
        msg.body = f"Click vào đây để verify: {link}"

        # --- ĐOẠN NÀY XỬ LÝ ASYNC ---
        
        
        app_instance = current_app._get_current_object()
        
        # Tạo luồng mới
        thr = Thread(target=self.send_async_email, args=(app_instance, msg))
        
        # Kích hoạt luồng (Nó sẽ chạy song song, code phía dưới chạy tiếp luôn không chờ)
        thr.start()
        
        return "Email đang được gửi..."

def is_near(tg: datetime.datetime):
    """
    Dùng để kiểm tra thời gian chỉ định cách thời gian hiện tại có ít nhất 30 phút
    """
    if not tg:
        return False
    tnow = datetime.datetime.now()
    tg_date = datetime.datetime.strptime(tg, "%Y-%m-%dT%H:%M:%S")
    duration = tg_date - tnow
    return duration <= datetime.timedelta(minutes=30)


