from functools import wraps
from flask import session, request, redirect, url_for, jsonify, abort

def _is_api_request():
    """
    Hàm phụ trợ: Kiểm tra xem request này có phải là gọi API không?
    Dựa vào đường dẫn URL bắt đầu bằng '/api/'
    """
    return request.path.startswith('/api/')

# 1. BẮT BUỘC ĐĂNG NHẬP
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Kiểm tra session
        if not session.get('user_id'):
            # A. Nếu là API -> Trả JSON 401
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Yêu cầu đăng nhập (Authentication required)",
                    "code": 401
                }), 401
            
            # B. Nếu là Web -> Đá về trang login
            # 'next' để sau khi login xong tự quay lại trang này
            return redirect(url_for('index.trang_dang_nhap', next=request.url))
            
        return f(*args, **kwargs)
    return wrapper

# 2. BẮT BUỘC XÁC THỰC EMAIL
def verification_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Logic: Đã login nhưng chưa xác thực
        # Lưu ý: Cần check login_required trước hoặc check session user_id ở đây cho chắc
        if session.get('user_id') and not session.get('is_xac_thuc'):
            
            # A. Nếu là API -> Trả JSON 403 (Hoặc 401 tùy quy định team)
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Tài khoản chưa xác thực email (Email verification required)",
                    "code": 403
                }), 403
            
            # B. Nếu là Web -> Đá về trang thông báo "Vui lòng check mail"
            return redirect(url_for('index.xac_thuc_email'))
            
        return f(*args, **kwargs)
    return wrapper

# 3. CHECK ROLE (PHÂN QUYỀN)
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check 1: Phải login trước đã
            if not session.get('user_id'):
                if _is_api_request():
                    return jsonify({"message": "Authentication required"}), 401
                return redirect(url_for('index.trang_dang_nhap'))

            # Check 2: Lấy role hiện tại
            current_role = session.get('vai_tro')

            # Check 3: So sánh role
            if current_role not in allowed_roles:
                # A. Nếu là API -> Trả JSON 403
                if _is_api_request():
                    return jsonify({
                        "status": "error",
                        "message": "Không đủ quyền truy cập (Permission denied)",
                        "code": 403
                    }), 403
                
                # B. Nếu là Web -> Kích hoạt trang lỗi 403 (abort)
                abort(403)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 4. KHÁCH (GUEST ONLY) - Dùng cho trang Login/Register
def guest_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('user_id'):
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper

# 5. UNVERIFIED ONLY - Dùng riêng cho trang "Vui lòng xác thực" (Chống lặp)
def unverified_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Nếu đã xác thực rồi mà cố vào trang này -> Đá về Home
        if session.get('is_xac_thuc'):
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper

# 6. Dùng riêng cho trang "Vui lòng chờ xét duyệt" (Chống lặp)
def unaccepted_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('vai_tro') != 'VODANH':
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper