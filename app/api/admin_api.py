# Admin API Blueprint
# Quản lý mấy cái API CRUD cho Admin (Tài khoản, Nhân viên, Khu vực, Bàn, Thực đơn...)
from flask import Blueprint, request, jsonify, session
from marshmallow import ValidationError
from app.decorator.decorators import login_required, role_required, verification_required
from app.container.container import injector_instance
from app.domain.services.interfaces.interfaces import (
    IAdminTaiKhoanService, IAdminNguoiDungService, IAdminKhuVucService,
    IAdminBanService, IAdminThucDonService, IAdminKhuyenMaiService, IAdminCauHinhThueService,
    ITaiKhoanService  # For account approval workflow
)

from app.schemas.init_schema import (
    admin_tai_khoan_create_schema, admin_tai_khoan_update_schema, admin_duyet_tai_khoan_schema,
    admin_nhan_vien_create_schema, admin_nhan_vien_update_schema,
    admin_khu_vuc_create_schema, admin_khu_vuc_update_schema,
    admin_ban_create_schema, admin_ban_update_schema,
    admin_nhom_mon_create_schema, admin_nhom_mon_update_schema,
    admin_mon_create_schema, admin_mon_update_schema, admin_mon_trang_thai_schema,
    admin_khuyen_mai_create_schema, admin_khuyen_mai_update_schema,
    admin_cau_hinh_thue_create_schema, admin_cau_hinh_thue_update_schema
)


admin_api_bp = Blueprint('admin_api', __name__)

# Get services from DI container
admin_tai_khoan_service = injector_instance.get(interface=IAdminTaiKhoanService)
admin_nguoi_dung_service = injector_instance.get(interface=IAdminNguoiDungService)
admin_khu_vuc_service = injector_instance.get(interface=IAdminKhuVucService)
admin_ban_service = injector_instance.get(interface=IAdminBanService)
admin_thuc_don_service = injector_instance.get(interface=IAdminThucDonService)
admin_khuyen_mai_service = injector_instance.get(interface=IAdminKhuyenMaiService)
admin_cau_hinh_thue_service = injector_instance.get(interface=IAdminCauHinhThueService)




def handle_validation_error(err: ValidationError):
    # Helper để báo lỗi khi client gửi data sai (thiếu trường, sai format...)
    errors = err.messages
    if isinstance(errors, dict):
        first_field = list(errors.keys())[0]
        first_error = errors[first_field][0] if isinstance(errors[first_field], list) else errors[first_field]
        return jsonify({'message': f'{first_field}: {first_error}'}), 400
    return jsonify({'message': str(errors)}), 400


# ============================================================
# TÀI KHOẢN ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/tai-khoan', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_tai_khoan():
    # Lấy danh sách tài khoản, có hỗ trợ search và filter trạng thái
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        filters = {
            'trang_thai': request.args.get('trang_thai'),
            'is_xac_thuc': request.args.get('is_xac_thuc', type=bool) if request.args.get('is_xac_thuc') else None,
            'search': request.args.get('search')
        }
        result = admin_tai_khoan_service.lay_danh_sach_tai_khoan(page, per_page, filters)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_chi_tiet_tai_khoan(tai_khoan_id):
    """Lấy chi tiết tài khoản"""
    try:
        result = admin_tai_khoan_service.lay_chi_tiet_tai_khoan(tai_khoan_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_tai_khoan():
    """Tạo tài khoản mới"""
    try:
        data = tai_khoan_create_schema.load(request.get_json())
        result = admin_tai_khoan_service.tao_tai_khoan(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_tai_khoan(tai_khoan_id):
    """Cập nhật tài khoản"""
    try:
        data = admin_tai_khoan_update_schema.load(request.get_json())
        result = admin_tai_khoan_service.cap_nhat_tai_khoan(tai_khoan_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_tai_khoan(tai_khoan_id):
    """Xóa tài khoản"""
    try:
        admin_tai_khoan_service.xoa_tai_khoan(tai_khoan_id)
        return jsonify({'message': 'Xóa tài khoản thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>/khoa', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def khoa_tai_khoan(tai_khoan_id):
    """Khóa tài khoản"""
    try:
        result = admin_tai_khoan_service.khoa_tai_khoan(tai_khoan_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>/mo-khoa', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def mo_khoa_tai_khoan(tai_khoan_id):
    """Mở khóa tài khoản"""
    try:
        result = admin_tai_khoan_service.mo_khoa_tai_khoan(tai_khoan_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# XÉT DUYỆT TÀI KHOẢN ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/tai-khoan/cho-duyet', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_cho_duyet():
    # Mấy ông mới đăng ký xong, đang chờ Admin duyệt để vào hệ thống
    try:
        result = admin_tai_khoan_service.lay_danh_sach_cho_xet_duyet()
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>/duyet', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def duyet_tai_khoan(tai_khoan_id):
    # Cấp quyền cho nhân viên truy cập hệ thống
    try:
        data = admin_duyet_tai_khoan_schema.load(request.get_json())
        vai_tro = data['vai_tro']
        
        admin_id = session.get('current_user')['user_id']
        result = admin_tai_khoan_service.xu_ly_duyet_tai_khoan(admin_id, tai_khoan_id, vai_tro)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/tai-khoan/<int:tai_khoan_id>/tu-choi', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def tu_choi_tai_khoan(tai_khoan_id):
    """Admin từ chối tài khoản (khóa tài khoản)"""
    try:
        admin_id = session.get('current_user')['user_id']
        admin_tai_khoan_service.xu_ly_tu_choi_tai_khoan(admin_id, tai_khoan_id)
        return jsonify({'message': 'Từ chối tài khoản thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# NHÂN VIÊN ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/nhan-vien', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_nhan_vien():
    """Lấy danh sách nhân viên"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        vai_tro = request.args.get('vai_tro')
        result = admin_nguoi_dung_service.lay_danh_sach_nhan_vien(page, per_page, vai_tro)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhan-vien', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_nhan_vien():
    """Tạo nhân viên mới"""
    try:
        data = admin_nhan_vien_create_schema.load(request.get_json())
        result = admin_nguoi_dung_service.tao_nhan_vien(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhan-vien/<int:nguoi_dung_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_nhan_vien(nguoi_dung_id):
    """Cập nhật nhân viên"""
    try:
        data = admin_nhan_vien_update_schema.load(request.get_json())
        result = admin_nguoi_dung_service.cap_nhat_nhan_vien(nguoi_dung_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhan-vien/<int:nguoi_dung_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_nhan_vien(nguoi_dung_id):
    """Xóa nhân viên"""
    try:
        admin_nguoi_dung_service.xoa_nhan_vien(nguoi_dung_id)
        return jsonify({'message': 'Xóa nhân viên thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# KHU VỰC ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/khu-vuc', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_khu_vuc():
    """Lấy danh sách khu vực"""
    try:
        result = admin_khu_vuc_service.lay_danh_sach_khuvuc()
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khu-vuc', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_khu_vuc():
    """Tạo khu vực mới"""
    try:
        data = admin_khu_vuc_create_schema.load(request.get_json())
        result = admin_khu_vuc_service.tao_khuvuc(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khu-vuc/<int:khu_vuc_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_khu_vuc(khu_vuc_id):
    """Cập nhật khu vực"""
    try:
        data = admin_khu_vuc_update_schema.load(request.get_json())
        result = admin_khu_vuc_service.cap_nhat_khuvuc(khu_vuc_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khu-vuc/<int:khu_vuc_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_khu_vuc(khu_vuc_id):
    """Xóa khu vực"""
    try:
        admin_khu_vuc_service.xoa_khuvuc(khu_vuc_id)
        return jsonify({'message': 'Xóa khu vực thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# BÀN ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/ban', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_ban():
    # Xem danh sách bàn theo từng khu vực
    try:
        khu_vuc_id = request.args.get('khu_vuc_id', type=int)
        trang_thai = request.args.get('trang_thai')
        result = admin_ban_service.lay_danh_sach_ban(khu_vuc_id, trang_thai)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/ban', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_ban():
    """Tạo bàn mới"""
    try:
        data = admin_ban_create_schema.load(request.get_json())
        result = admin_ban_service.tao_ban(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/ban/<int:ban_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_ban(ban_id):
    """Cập nhật bàn"""
    try:
        data = admin_ban_update_schema.load(request.get_json())
        result = admin_ban_service.cap_nhat_ban(ban_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/ban/<int:ban_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_ban(ban_id):
    """Xóa bàn"""
    try:
        admin_ban_service.xoa_ban(ban_id)
        return jsonify({'message': 'Xóa bàn thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/ban/<int:ban_id>/reset', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def reset_trang_thai_ban(ban_id):
    # Dùng khi có lỗi logic cần đưa bàn về trạng thái Trống ngay lập tức
    try:
        result = admin_ban_service.reset_trang_thai_ban(ban_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# THỰC ĐƠN ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/thuc-don', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_thuc_don():
    """Lấy thực đơn chi tiết"""
    try:
        result = admin_thuc_don_service.lay_thuc_don_chi_tiet()
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhom-mon', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_nhom_mon():
    """Tạo nhóm món mới"""
    try:
        data = admin_nhom_mon_create_schema.load(request.get_json())
        result = admin_thuc_don_service.tao_nhom_mon(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhom-mon/<int:nhom_mon_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_nhom_mon(nhom_mon_id):
    """Cập nhật nhóm món"""
    try:
        data = admin_nhom_mon_update_schema.load(request.get_json())
        result = admin_thuc_don_service.cap_nhat_nhom_mon(nhom_mon_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/nhom-mon/<int:nhom_mon_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_nhom_mon(nhom_mon_id):
    """Xóa nhóm món"""
    try:
        admin_thuc_don_service.xoa_nhom_mon(nhom_mon_id)
        return jsonify({'message': 'Xóa nhóm món thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/mon', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_mon():
    """Tạo món mới"""
    try:
        data = admin_mon_create_schema.load(request.get_json())
        result = admin_thuc_don_service.tao_mon(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/mon/<int:mon_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_mon(mon_id):
    """Cập nhật món"""
    try:
        data = admin_mon_update_schema.load(request.get_json())
        result = admin_thuc_don_service.cap_nhat_mon(mon_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/mon/<int:mon_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_mon(mon_id):
    # Không xóa hẳn data, chỉ cho nó ẩn đi (không bán nữa)
    try:
        admin_thuc_don_service.xoa_mon(mon_id)
        return jsonify({'message': 'Xóa món thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/mon/<int:mon_id>/trang-thai', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_trang_thai_mon(mon_id):
    """Cập nhật trạng thái món"""
    try:
        data = admin_mon_trang_thai_schema.load(request.get_json())
        result = admin_thuc_don_service.cap_nhat_trang_thai_mon(mon_id, data['trang_thai'])
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# KHUYẾN MÃI ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/khuyen-mai', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_khuyen_mai():
    """Lấy danh sách khuyến mãi"""
    try:
        hoat_dong = request.args.get('hoat_dong', type=bool) if request.args.get('hoat_dong') else None
        result = admin_khuyen_mai_service.lay_danh_sach_khuyen_mai(hoat_dong)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khuyen-mai', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_khuyen_mai():
    """Tạo khuyến mãi mới"""
    try:
        data = admin_khuyen_mai_create_schema.load(request.get_json())
        result = admin_khuyen_mai_service.tao_khuyen_mai(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khuyen-mai/<int:khuyen_mai_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_khuyen_mai(khuyen_mai_id):
    """Cập nhật khuyến mãi"""
    try:
        data = admin_khuyen_mai_update_schema.load(request.get_json())
        print(data)
        result = admin_khuyen_mai_service.cap_nhat_khuyen_mai(khuyen_mai_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khuyen-mai/<int:khuyen_mai_id>', methods=['DELETE'])
@login_required
@verification_required
@role_required('ADMIN')
def xoa_khuyen_mai(khuyen_mai_id):
    """Xóa khuyến mãi (soft delete)"""
    try:
        admin_khuyen_mai_service.xoa_khuyen_mai(khuyen_mai_id)
        return jsonify({'message': 'Xóa khuyến mãi thành công'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khuyen-mai/<int:khuyen_mai_id>/kich-hoat', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def kich_hoat_khuyen_mai(khuyen_mai_id):
    """Kích hoạt khuyến mãi"""
    try:
        result = admin_khuyen_mai_service.kich_hoat_khuyen_mai(khuyen_mai_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/khuyen-mai/<int:khuyen_mai_id>/vo-hieu-hoa', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def vo_hieu_hoa_khuyen_mai(khuyen_mai_id):
    """Vô hiệu hóa khuyến mãi"""
    try:
        result = admin_khuyen_mai_service.vo_hieu_hoa_khuyen_mai(khuyen_mai_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


# ============================================================
# CẤU HÌNH THUẾ ENDPOINTS
# ============================================================

@admin_api_bp.route('/api/admin/cau-hinh-thue', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_cau_hinh_thue():
    """Lấy danh sách cấu hình thuế"""
    try:
        result = admin_cau_hinh_thue_service.lay_danh_sach_cau_hinh_thue()
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/cau-hinh-thue/hien-tai', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_cau_hinh_thue_hien_tai():
    """Lấy cấu hình thuế đang hoạt động"""
    try:
        result = admin_cau_hinh_thue_service.lay_cau_hinh_thue_hien_tai()
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/cau-hinh-thue', methods=['POST'])
@login_required
@verification_required
@role_required('ADMIN')
def tao_cau_hinh_thue():
    """Tạo cấu hình thuế mới"""
    try:
        data = admin_cau_hinh_thue_create_schema.load(request.get_json())
        result = admin_cau_hinh_thue_service.tao_cau_hinh_thue(data)
        return jsonify(result), 201
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/cau-hinh-thue/<int:cau_hinh_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def cap_nhat_cau_hinh_thue(cau_hinh_id):
    """Cập nhật cấu hình thuế"""
    try:
        data = admin_cau_hinh_thue_update_schema.load(request.get_json())
        result = admin_cau_hinh_thue_service.cap_nhat_cau_hinh_thue(cau_hinh_id, data)
        return jsonify(result), 200
    except ValidationError as err:
        return handle_validation_error(err)
    except Exception as err:
        return jsonify({'message': str(err)}), 400


@admin_api_bp.route('/api/admin/cau-hinh-thue/<int:cau_hinh_id>/kich-hoat', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def kich_hoat_cau_hinh_thue(cau_hinh_id):
    """Kích hoạt cấu hình thuế"""
    try:
        result = admin_cau_hinh_thue_service.kich_hoat_cau_hinh_thue(cau_hinh_id)
        return jsonify(result), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 400
