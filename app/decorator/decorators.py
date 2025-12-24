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
        if not session.get('current_user'):
            # A. Nếu là API -> Trả JSON 401
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Yêu cầu đăng nhập (Authentication required)",
                    "code": 401
                }), 401
            
            # B. Nếu là Web -> Đá về trang login
            # 'next' để sau khi login xong tự quay lại trang này
            return redirect(url_for('auth.trang_dang_nhap'))
            
        return f(*args, **kwargs)
    return wrapper

# 2. BẮT BUỘC XÁC THỰC EMAIL VÀ ĐÃ ĐƯỢC ADMIN DUYỆT
def verification_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        current_user = session.get('current_user')
        
        if not current_user:
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Yêu cầu đăng nhập (Authentication required)",
                    "code": 401
                }), 401
            return redirect(url_for('auth.trang_dang_nhap'))
        
        # Check 1: Chưa xác thực email
        if not current_user.get('is_xac_thuc'):
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Tài khoản chưa xác thực email (Email verification required)",
                    "code": 403
                }), 403
            return redirect(url_for('auth.xac_thuc_email'))
        
        # Check 2: Đã xác thực email nhưng chưa được Admin duyệt (vai trò VODANH)
        if current_user.get('vai_tro') == 'VODANH':
            if _is_api_request():
                return jsonify({
                    "status": "error",
                    "message": "Tài khoản đang chờ Admin xét duyệt (Pending admin approval)",
                    "code": 403
                }), 403
            return redirect(url_for('auth.cho_xet_duyet'))
            
        return f(*args, **kwargs)
    return wrapper

# 3. CHECK ROLE (PHÂN QUYỀN)
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check 1: Phải login trước đã
            if not session.get('current_user'):
                if _is_api_request():
                    return jsonify({"message": "Authentication required"}), 401
                return redirect(url_for('auth.trang_dang_nhap'))

            # Check 2: Lấy role hiện tại
            current_role = session.get('current_user')['vai_tro']

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
        if session.get('current_user'):
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper

# 5. UNVERIFIED ONLY - Dùng riêng cho trang "Vui lòng xác thực" (Chống lặp)
def unverified_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Nếu đã xác thực rồi mà cố vào trang này -> Đá về Home
        if session.get('current_user')['is_xac_thuc']:
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper

# 6. Dùng riêng cho trang "Vui lòng chờ xét duyệt" (Chống lặp)
def unaccepted_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('current_user')['vai_tro'] != 'VODANH':
            return redirect(url_for('index.trang_chu'))
        return f(*args, **kwargs)
    return wrapper