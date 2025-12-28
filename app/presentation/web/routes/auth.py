from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from marshmallow import ValidationError
from jwt import ExpiredSignatureError, InvalidTokenError
from app.container.container import injector_instance
from app.domain.services.interfaces.interfaces import ITaiKhoanService
from app.decorator.decorators import (guest_required, login_required, 
                                      unverified_required, unaccepted_required)
from app.schemas.init_schema import tai_khoan_create_schema, tai_khoan_login_schema



auth_bp = Blueprint('auth', __name__)

tai_khoan_service = injector_instance.get(interface=ITaiKhoanService)


@auth_bp.route('/yeu-cau-xac-thuc')
@login_required
@unverified_required
def yeu_cau_xac_thuc():
    # Trang báo lỗi/yêu cầu check mail để kích hoạt tài khoản
    return render_template('page/xac_thuc/yeu_cau_xac_thuc.html')


@auth_bp.route('/cho-xet-duyet')
@login_required
@unaccepted_required
def cho_xet_duyet():
    return render_template('page/xac_thuc/cho_xet_duyet.html')


@auth_bp.route('/dang-xuat')
@login_required
def dang_xuat():
    # Clear hết session rồi đá về trang login
    session.clear()
    return redirect(url_for('auth.trang_dang_nhap'))

@auth_bp.route('/dang-nhap')
@guest_required
def trang_dang_nhap():
    # Show giao diện login
    return render_template('page/xac_thuc/dang_nhap.html')


@auth_bp.route('/dang-nhap', methods=['POST'])
def xu_ly_dang_nhap():
    # Nhận data từ form, check login rồi lưu vào session
    try:
        data = request.form.to_dict()
        # print(data)
        tai_khoan_dang_nhap = tai_khoan_login_schema.load(data)
        print(tai_khoan_dang_nhap)
        nguoi_dung = tai_khoan_service.dang_nhap_tai_khoan(tai_khoan_login=tai_khoan_dang_nhap)

        current_user = {
            'user_id': nguoi_dung['id'],
            'vai_tro': nguoi_dung['tai_khoan']['vai_tro']['vai_tro'],
            'is_xac_thuc': nguoi_dung['tai_khoan']['is_xac_thuc'],
            'ten': nguoi_dung['ho_ten']
        }
    
        session['current_user'] = current_user

        flash('Đăng nhập thành công', 'success')

        return redirect(url_for('index.trang_chu')) 
    except Exception as err:
        flash(str(err), 'error')
        print(err)
        return redirect(url_for('auth.trang_dang_nhap'))





@auth_bp.route('/dang-ky')
@guest_required
def trang_dang_ky():
    # Show giao diện đăng ký tài khoản mới
    return render_template('page/xac_thuc/dang_ky.html')

    
@auth_bp.route('/dang-ky', methods=['POST'])
def xu_ly_dang_ky():
    # Xử lý tạo user mới, gửi mail xác nhận các thứ
    try:
        data = request.form.to_dict()
        tai_khoan = tai_khoan_create_schema.load(data)
        flag = tai_khoan_service.dang_ky_tai_khoan(tai_khoan_create=tai_khoan)
        if flag:
            flash('Đăng ký thành công, vui lòng kiểm tra email để xác nhận', 'success')
            return redirect(url_for('auth.trang_dang_nhap'))
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            flash(f'{err.messages}', 'error')
            return redirect(url_for('auth.trang_dang_ky'))
        elif isinstance(err, Exception):
            flash(str(err), 'error')
            return redirect(url_for('auth.trang_dang_ky'))

@auth_bp.route('/auth/verify')
def xac_thuc_email():
    # Click link trong mail thì nhảy vào đây để kích hoạt account
    try:
        token = request.args.get('token')
        flag = tai_khoan_service.xac_thuc_tai_khoan(token=token)
        if not token or not flag:
            flash('Không hợp lệ', 'wrong_token')
        else:
            flash('Xác thực thành công', 'success_token')
        return render_template('page/xac_thuc/xac_thuc.html')
    
    except (ExpiredSignatureError, InvalidTokenError, Exception) as e:
        if isinstance(e, ExpiredSignatureError):
            print(e)
            flash('Token đã hết hạn', 'exp_token')
        elif isinstance(e, InvalidTokenError):
            print(e)
            flash('Token không hợp lệ', 'wrong_token')
        
        return render_template('page/xac_thuc/xac_thuc.html')