"""
Flask-Admin Configuration cho vai trò ADMIN
Quản lý tất cả các model trong hệ thống
"""
from flask import session, redirect, url_for, request
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field
from markupsafe import Markup
from wtforms import PasswordField
from app.extentions.extentions import admin, db
from app.data.models import (
    VaiTro, TaiKhoan, NguoiDung, QuanLy, ThuNgan, PhucVu, LeTan, DauBep,
    KhuVuc, Ban, PhienBan, PhanCong, KhungGio, KhungGioAn, KhungGioDatBan,
    ThucDon, NhomMon, MoTaMon, NhomTuyChon, TuyChonMon,
    PhieuMon, MonGhi, ThongBao,
    DoanhThu, ThanhToan, CauHinhThue, KhuyenMai, KhuyenMaiTheoPhanTram, KhuyenMaiCung,
    YeuCau, YCMonGhi, YCPhieuMon
)
from app.data.models import (
    TrangThaiTaiKhoan, TrangThaiBan, TrangThai, TrangThaiPhieu, TrangThaiMonGhi,
    TrangThaiMon, LoaiNhomTuyChon, TenVaiTro, PhanLoaiThongBao,
    TrangThaiDoanhThu, TrangThaiThanhToan, PhuongThucThanhToan, TrangThaiYeuCau
)
from app.utils.helper import Helper


class SecureAdminIndexView(AdminIndexView):
    """Custom Admin Index View với authentication và dashboard"""
    
    @expose('/')
    def index(self):
        if not self.is_accessible():
            return redirect(url_for('auth.trang_dang_nhap'))
        
        
        from app.data.models import (
            TaiKhoan, NguoiDung, PhienBan, DoanhThu, YeuCau,
            TrangThaiDoanhThu, TrangThaiYeuCau, TrangThai
        )
        from sqlalchemy import func, cast, Date
        from datetime import date
        from flask import current_app
        
        today = date.today()
        
        stats = {}
        session = db.session
        
        stats['total_accounts'] = session.query(func.count(TaiKhoan.id)).scalar() or 0
        
        stats['total_users'] = session.query(func.count(NguoiDung.id)).scalar() or 0
        
        stats['active_sessions'] = session.query(func.count(PhienBan.id))\
            .filter(PhienBan.trang_thai == TrangThai.MO).scalar() or 0
        
        stats['today_revenue'] = session.query(func.coalesce(func.sum(DoanhThu.tien_cuoi_cung), 0))\
            .filter(DoanhThu.trang_thai == TrangThaiDoanhThu.DAHOANTHANH)\
            .filter(cast(DoanhThu.ngay_tao, Date) == today).scalar() or 0
        
        stats['pending_requests'] = session.query(func.count(YeuCau.id))\
            .filter(YeuCau.trang_thai == TrangThaiYeuCau.CHODUYET).scalar() or 0
        
        return self.render('admin/index.html', stats=stats)
    
    def is_accessible(self):
        """Chỉ ADMIN mới được truy cập"""
        if not session.get('current_user'):
            return False
        
        user_role = session.get('current_user', {}).get('vai_tro')
        is_verified = session.get('current_user', {}).get('is_xac_thuc', False)
        
        return user_role == 'ADMIN' and is_verified
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect nếu không có quyền"""
        return redirect(url_for('auth.trang_dang_nhap'))


class SecureModelView(ModelView):
    """Base ModelView với authentication và authorization"""
    
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    
    page_size = 50
    
    def is_accessible(self):
        """Chỉ ADMIN mới được truy cập"""
        if not session.get('current_user'):
            return False
        
        user_role = session.get('current_user', {}).get('vai_tro')
        is_verified = session.get('current_user', {}).get('is_xac_thuc', False)
        
        return user_role == 'ADMIN' and is_verified
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect nếu không có quyền"""
        return redirect(url_for('auth.trang_dang_nhap'))


# ============================================================
# CUSTOM MODEL VIEWS
# ============================================================

class TaiKhoanModelView(SecureModelView):
    """ModelView cho Tài Khoản với chức năng xét duyệt"""
    column_list = ['id', 'ten_tai_khoan', 'email', 'vai_tro', 'trang_thai', 'is_xac_thuc', 'ngay_tao', 'nguoi_dung']
    column_searchable_list = ['ten_tai_khoan', 'email']
    column_filters = ['trang_thai', 'is_xac_thuc', 'vai_tro.vai_tro']
    column_editable_list = ['trang_thai']
    
    form_columns = ['ten_tai_khoan', 'email', 'mat_khau', 'vai_tro', 'trang_thai', 'is_xac_thuc']
    form_overrides = {
        'mat_khau': PasswordField
    }
    
    def _format_vai_tro(view, context, model, name):
        """Format hiển thị vai trò"""
        if model.vai_tro:
            return model.vai_tro.vai_tro.value if hasattr(model.vai_tro.vai_tro, 'value') else str(model.vai_tro.vai_tro)
        return '-'
    
    def _format_nguoi_dung(view, context, model, name):
        """Format hiển thị người dùng"""
        if model.nguoi_dung:
            return model.nguoi_dung.ho_ten
        return '-'
    
    def _format_cho_duyet(view, context, model, name):
        """Hiển thị badge cho tài khoản chờ duyệt"""
        from app.data.models import TenVaiTro
        if model.is_xac_thuc and model.vai_tro.vai_tro == TenVaiTro.VODANH:
            return Markup('<span class="label label-warning">⏳ Chờ duyệt</span>')
        return '-'
    
    column_formatters = {
        'vai_tro': _format_vai_tro,
        'nguoi_dung': _format_nguoi_dung,
        'cho_duyet': _format_cho_duyet
    }
    
    def on_model_change(self, form, model, is_created):
        """Hash password khi tạo/sửa"""
        if form.mat_khau.data:
            helper = Helper()
            model.mat_khau = helper.hass_pass(form.mat_khau.data)
    
    column_labels = {
        'ten_tai_khoan': 'Tên tài khoản',
        'email': 'Email',
        'mat_khau': 'Mật khẩu',
        'vai_tro': 'Vai trò',
        'trang_thai': 'Trạng thái',
        'is_xac_thuc': 'Đã xác thực',
        'ngay_tao': 'Ngày tạo',
        'nguoi_dung': 'Người dùng'
    }
    
    def get_query(self):
        """Override để có thể filter tài khoản chờ duyệt"""
        return super().get_query()
    
    def get_count_query(self):
        """Override count query"""
        return super().get_count_query()


class NguoiDungModelView(SecureModelView):
    """ModelView cho Người Dùng"""
    column_list = ['id', 'ho_ten', 'type', 'tai_khoan', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    column_filters = ['type']
    
    form_args = {
        'tai_khoan_id': {
            'label': 'Tài khoản',
            'get_label': lambda x: f"{x.ten_tai_khoan} ({x.email})" if x.email else x.ten_tai_khoan
        }
    }
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'type': 'Loại',
        'tai_khoan': 'Tài khoản',
        'ngay_tao': 'Ngày tạo'
    }


class PhucVuModelView(SecureModelView):
    """ModelView cho Phục Vụ"""
    column_list = ['id', 'ho_ten', 'tai_khoan', 'khu_vuc', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    column_filters = ['khu_vuc_id']  # Sử dụng foreign key để filter
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    def _format_khu_vuc(view, context, model, name):
        """Format hiển thị khu vực"""
        if model.khu_vuc:
            return model.khu_vuc.ten
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan,
        'khu_vuc': _format_khu_vuc
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'tai_khoan': 'Tài khoản',
        'khu_vuc': 'Khu vực',
        'ngay_tao': 'Ngày tạo'
    }


class BanModelView(SecureModelView):
    """ModelView cho Bàn"""
    column_list = ['id', 'ten', 'so_ghe', 'trang_thai', 'khu_vuc', 'ngay_tao']
    column_searchable_list = ['ten']
    column_filters = ['trang_thai', 'khu_vuc']
    column_editable_list = ['trang_thai']
    
    form_args = {
        'khu_vuc_id': {
            'label': 'Khu vực',
            'get_label': lambda x: x.ten
        }
    }
    
    def _format_khu_vuc(view, context, model, name):
        """Format hiển thị khu vực"""
        if model.khu_vuc:
            return model.khu_vuc.ten
        return '-'
    
    column_formatters = {
        'khu_vuc': _format_khu_vuc
    }
    
    column_labels = {
        'ten': 'Tên bàn',
        'so_ghe': 'Số ghế',
        'trang_thai': 'Trạng thái',
        'khu_vuc': 'Khu vực',
        'ngay_tao': 'Ngày tạo'
    }


class PhienBanModelView(SecureModelView):
    """ModelView cho Phiên Bàn"""
    column_list = ['id', 'trang_thai', 'le_tan', 'nguoi_dam_nhan', 'khung_gio', 'ngay_tao']
    column_filters = ['trang_thai']
    
    form_args = {
        'le_tan_id': {
            'label': 'Lễ tân',
            'get_label': lambda x: x.ho_ten
        },
        'nguoi_dam_nhan_id': {
            'label': 'Người đảm nhận',
            'get_label': lambda x: x.ho_ten
        },
        'khung_gio_id': {
            'label': 'Khung giờ',
            'get_label': lambda x: f"{x.tg_bat_dau.strftime('%H:%M')} - {x.tg_ket_thuc_du_kien.strftime('%H:%M')}" if x.tg_bat_dau and x.tg_ket_thuc_du_kien else f"Khung giờ #{x.id}"
        }
    }
    
    def _format_le_tan(view, context, model, name):
        """Format hiển thị lễ tân"""
        if model.le_tan:
            return model.le_tan.ho_ten
        return '-'
    
    def _format_nguoi_dam_nhan(view, context, model, name):
        """Format hiển thị người đảm nhận"""
        if model.nguoi_dam_nhan:
            return model.nguoi_dam_nhan.ho_ten
        return '-'
    
    def _format_khung_gio(view, context, model, name):
        """Format hiển thị khung giờ"""
        if model.khung_gio:
            from datetime import datetime
            tg_bd = model.khung_gio.tg_bat_dau.strftime('%H:%M') if model.khung_gio.tg_bat_dau else '-'
            tg_kt = model.khung_gio.tg_ket_thuc_du_kien.strftime('%H:%M') if model.khung_gio.tg_ket_thuc_du_kien else '-'
            return f"{tg_bd} - {tg_kt}"
        return '-'
    
    column_formatters = {
        'le_tan': _format_le_tan,
        'nguoi_dam_nhan': _format_nguoi_dam_nhan,
        'khung_gio': _format_khung_gio
    }
    
    column_labels = {
        'trang_thai': 'Trạng thái',
        'le_tan': 'Lễ tân',
        'nguoi_dam_nhan': 'Người đảm nhận',
        'khung_gio': 'Khung giờ',
        'ngay_tao': 'Ngày tạo'
    }


class PhieuMonModelView(SecureModelView):
    """ModelView cho Phiếu Món"""
    column_list = ['id', 'trang_thai', 'phien_ban', 'ngay_tao']
    column_filters = ['trang_thai']
    
    form_args = {
        'phien_ban_id': {
            'label': 'Phiên bàn',
            'get_label': lambda x: f"Phiên #{x.id}"
        }
    }
    
    def _format_phien_ban(view, context, model, name):
        """Format hiển thị phiên bàn"""
        if model.phien_ban:
            trang_thai = model.phien_ban.trang_thai
            if hasattr(trang_thai, 'value'):
                trang_thai_str = trang_thai.value
            else:
                trang_thai_str = str(trang_thai)
            return f"Phiên #{model.phien_ban.id} - {trang_thai_str}"
        return '-'
    
    column_formatters = {
        'phien_ban': _format_phien_ban
    }
    
    column_labels = {
        'trang_thai': 'Trạng thái',
        'phien_ban': 'Phiên bàn',
        'ngay_tao': 'Ngày tạo'
    }


class MonGhiModelView(SecureModelView):
    """ModelView cho Món Ghi"""
    column_list = ['id', 'so_luong', 'trang_thai', 'phieu_mon', 'mo_ta_mon', 'ghi_chu', 'ngay_tao']
    column_searchable_list = ['ghi_chu']
    column_filters = ['trang_thai']
    
    form_args = {
        'phieu_mon_id': {
            'label': 'Phiếu món',
            'get_label': lambda x: f"Phiếu #{x.id}"
        },
        'mo_ta_mon_id': {
            'label': 'Món',
            'get_label': lambda x: f"{x.ten} ({x.gia:,} đ)"
        }
    }
    
    def _format_phieu_mon(view, context, model, name):
        """Format hiển thị phiếu món"""
        if model.phieu_mon:
            return f"Phiếu #{model.phieu_mon.id}"
        return '-'
    
    def _format_mo_ta_mon(view, context, model, name):
        """Format hiển thị món"""
        if model.mo_ta_mon:
            return f"{model.mo_ta_mon.ten} ({model.mo_ta_mon.gia:,} đ)"
        return '-'
    
    column_formatters = {
        'phieu_mon': _format_phieu_mon,
        'mo_ta_mon': _format_mo_ta_mon
    }
    
    column_labels = {
        'so_luong': 'Số lượng',
        'trang_thai': 'Trạng thái',
        'phieu_mon': 'Phiếu món',
        'mo_ta_mon': 'Món',
        'ghi_chu': 'Ghi chú',
        'ngay_tao': 'Ngày tạo'
    }


class DoanhThuModelView(SecureModelView):
    """ModelView cho Doanh Thu"""
    column_list = ['id', 'tong_tien', 'tien_giam_gia', 'tien_cuoi_cung', 'trang_thai', 'thu_ngan', 'phien_ban', 'ngay_tao']
    column_filters = ['trang_thai', 'thu_ngan_id']  # Sử dụng thu_ngan_id thay vì thu_ngan để tránh lỗi Join
    column_default_sort = ('ngay_tao', True)
    
    form_args = {
        'thu_ngan_id': {
            'label': 'Thu ngân',
            'get_label': lambda x: x.ho_ten
        },
        'phien_ban_id': {
            'label': 'Phiên bàn',
            'get_label': lambda x: f"Phiên #{x.id}"
        }
    }
    
    def _format_currency(view, context, model, name):
        """Format số tiền thành VNĐ"""
        value = getattr(model, name, 0) or 0
        return f"{value:,} đ"
    
    def _format_thu_ngan(view, context, model, name):
        """Format hiển thị thu ngân"""
        if model.thu_ngan:
            return model.thu_ngan.ho_ten
        return '-'
    
    def _format_phien_ban(view, context, model, name):
        """Format hiển thị phiên bàn"""
        if model.phien_ban:
            return f"Phiên #{model.phien_ban.id}"
        return '-'
    
    column_formatters = {
        'tong_tien': _format_currency,
        'tien_giam_gia': _format_currency,
        'tien_cuoi_cung': _format_currency,
        'tien_thue': _format_currency,
        'thu_ngan': _format_thu_ngan,
        'phien_ban': _format_phien_ban
    }
    
    column_labels = {
        'tong_tien': 'Tổng tiền',
        'tien_giam_gia': 'Giảm giá',
        'tien_cuoi_cung': 'Thực thu',
        'tien_thue': 'Thuế',
        'trang_thai': 'Trạng thái',
        'thu_ngan': 'Thu ngân',
        'phien_ban': 'Phiên bàn',
        'ngay_tao': 'Ngày tạo'
    }


class KhuyenMaiModelView(SecureModelView):
    """ModelView cho Khuyến Mãi"""
    column_list = ['id', 'ten', 'hoat_dong', 'tu_dong_ap_dung', 'gia_tri_don_hang_toi_thieu', 'ngay_bat_dau', 'ngay_het_han']
    column_searchable_list = ['ten']
    column_filters = ['hoat_dong', 'tu_dong_ap_dung']
    column_editable_list = ['hoat_dong']
    
    column_labels = {
        'ten': 'Tên khuyến mãi',
        'hoat_dong': 'Hoạt động',
        'tu_dong_ap_dung': 'Tự động áp dụng',
        'gia_tri_don_hang_toi_thieu': 'Giá trị tối thiểu',
        'ngay_bat_dau': 'Ngày bắt đầu',
        'ngay_het_han': 'Ngày hết hạn'
    }


class MoTaMonModelView(SecureModelView):
    """ModelView cho Mô Tả Món"""
    column_list = ['id', 'ten', 'gia', 'trang_thai', 'nhom_mon', 'hinh', 'ngay_tao']
    column_searchable_list = ['ten']
    column_filters = ['trang_thai', 'nhom_mon']
    column_editable_list = ['trang_thai']
    
    form_args = {
        'nhom_mon_id': {
            'label': 'Nhóm món',
            'get_label': lambda x: x.ten
        }
    }
    
    def _format_price(view, context, model, name):
        """Format giá thành VNĐ"""
        value = getattr(model, name, 0) or 0
        return f"{value:,} đ"
    
    def _format_image(view, context, model, name):
        """Hiển thị hình ảnh"""
        url = getattr(model, name, None)
        if url:
            return Markup(f'<img src="{url}" style="max-width: 50px; max-height: 50px; border-radius: 4px;">')
        return '-'
    
    def _format_nhom_mon(view, context, model, name):
        """Format hiển thị nhóm món"""
        if model.nhom_mon:
            return model.nhom_mon.ten
        return '-'
    
    column_formatters = {
        'gia': _format_price,
        'hinh': _format_image,
        'nhom_mon': _format_nhom_mon
    }
    
    column_labels = {
        'ten': 'Tên món',
        'gia': 'Giá',
        'trang_thai': 'Trạng thái',
        'nhom_mon': 'Nhóm món',
        'hinh': 'Hình ảnh',
        'ngay_tao': 'Ngày tạo'
    }


class YeuCauModelView(SecureModelView):
    """ModelView cho Yêu Cầu"""
    column_list = ['id', 'trang_thai', 'ly_do', 'quan_ly_duyet_id', 'ngay_tao']
    column_filters = ['trang_thai']
    column_searchable_list = ['ly_do']
    
    column_labels = {
        'trang_thai': 'Trạng thái',
        'ly_do': 'Lý do',
        'quan_ly_duyet_id': 'Quản lý duyệt',
        'ngay_tao': 'Ngày tạo'
    }


class VaiTroModelView(SecureModelView):
    """ModelView cho Vai Trò - Chỉ đọc (không cho phép sửa/xóa)"""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ['id', 'vai_tro', 'ngay_tao']
    
    column_labels = {
        'vai_tro': 'Vai trò',
        'ngay_tao': 'Ngày tạo'
    }


class PhanCongModelView(SecureModelView):
    """ModelView cho Phân Công"""
    column_list = ['id', 'trang_thai', 'dam_nhan_ghi_mon', 'phuc_vu', 'ban', 'phien_ban', 'ngay_tao']
    column_filters = ['trang_thai', 'phuc_vu_id', 'ban_id', 'phien_ban_id']
    
    form_args = {
        'phuc_vu_id': {
            'label': 'Phục vụ',
            'get_label': lambda x: x.ho_ten
        },
        'ban_id': {
            'label': 'Bàn',
            'get_label': lambda x: f"{x.ten} (Khu: {x.khu_vuc.ten if x.khu_vuc else 'N/A'})"
        },
        'phien_ban_id': {
            'label': 'Phiên bàn',
            'get_label': lambda x: f"Phiên #{x.id}"
        }
    }
    
    def _format_phuc_vu(view, context, model, name):
        """Format hiển thị phục vụ"""
        if model.phuc_vu:
            return model.phuc_vu.ho_ten
        return '-'
    
    def _format_ban(view, context, model, name):
        """Format hiển thị bàn"""
        if model.ban:
            return f"{model.ban.ten} (Khu: {model.ban.khu_vuc.ten if model.ban.khu_vuc else 'N/A'})"
        return '-'
    
    def _format_phien_ban(view, context, model, name):
        """Format hiển thị phiên bàn"""
        if model.phien_ban:
            return f"Phiên #{model.phien_ban.id}"
        return '-'
    
    column_formatters = {
        'phuc_vu': _format_phuc_vu,
        'ban': _format_ban,
        'phien_ban': _format_phien_ban
    }
    
    column_labels = {
        'trang_thai': 'Trạng thái',
        'dam_nhan_ghi_mon': 'Đảm nhận ghi món',
        'phuc_vu': 'Phục vụ',
        'ban': 'Bàn',
        'phien_ban': 'Phiên bàn',
        'ngay_tao': 'Ngày tạo'
    }


class LeTanModelView(SecureModelView):
    """ModelView cho Lễ Tân"""
    column_list = ['id', 'ho_ten', 'tai_khoan', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    
    form_args = {
        'tai_khoan_id': {
            'label': 'Tài khoản',
            'get_label': lambda x: f"{x.ten_tai_khoan} ({x.email})" if x.email else x.ten_tai_khoan
        }
    }
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'tai_khoan': 'Tài khoản',
        'ngay_tao': 'Ngày tạo'
    }


class ThuNganModelView(SecureModelView):
    """ModelView cho Thu Ngân"""
    column_list = ['id', 'ho_ten', 'tai_khoan', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    
    form_args = {
        'tai_khoan_id': {
            'label': 'Tài khoản',
            'get_label': lambda x: f"{x.ten_tai_khoan} ({x.email})" if x.email else x.ten_tai_khoan
        }
    }
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'tai_khoan': 'Tài khoản',
        'ngay_tao': 'Ngày tạo'
    }


class DauBepModelView(SecureModelView):
    """ModelView cho Đầu Bếp"""
    column_list = ['id', 'ho_ten', 'tai_khoan', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    
    form_args = {
        'tai_khoan_id': {
            'label': 'Tài khoản',
            'get_label': lambda x: f"{x.ten_tai_khoan} ({x.email})" if x.email else x.ten_tai_khoan
        }
    }
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'tai_khoan': 'Tài khoản',
        'ngay_tao': 'Ngày tạo'
    }


class QuanLyModelView(SecureModelView):
    """ModelView cho Quản Lý"""
    column_list = ['id', 'ho_ten', 'tai_khoan', 'ngay_tao']
    column_searchable_list = ['ho_ten']
    
    form_args = {
        'tai_khoan_id': {
            'label': 'Tài khoản',
            'get_label': lambda x: f"{x.ten_tai_khoan} ({x.email})" if x.email else x.ten_tai_khoan
        }
    }
    
    def _format_tai_khoan(view, context, model, name):
        """Format hiển thị tài khoản"""
        if model.tai_khoan:
            email = model.tai_khoan.email if model.tai_khoan.email else ''
            if email:
                return f"{model.tai_khoan.ten_tai_khoan} ({email})"
            return model.tai_khoan.ten_tai_khoan
        return '-'
    
    column_formatters = {
        'tai_khoan': _format_tai_khoan
    }
    
    column_labels = {
        'ho_ten': 'Họ tên',
        'tai_khoan': 'Tài khoản',
        'ngay_tao': 'Ngày tạo'
    }


class NhomMonModelView(SecureModelView):
    """ModelView cho Nhóm Món"""
    column_list = ['id', 'ten', 'thuc_don', 'ngay_tao']
    column_searchable_list = ['ten']
    column_filters = ['thuc_don_id']
    
    form_args = {
        'thuc_don_id': {
            'label': 'Thực đơn',
            'get_label': lambda x: f"Thực đơn #{x.id}"
        }
    }
    
    def _format_thuc_don(view, context, model, name):
        """Format hiển thị thực đơn"""
        if model.thuc_don:
            return f"Thực đơn #{model.thuc_don.id}"
        return '-'
    
    column_formatters = {
        'thuc_don': _format_thuc_don
    }
    
    column_labels = {
        'ten': 'Tên nhóm món',
        'thuc_don': 'Thực đơn',
        'ngay_tao': 'Ngày tạo'
    }


class TuyChonMonModelView(SecureModelView):
    """ModelView cho Tùy Chọn Món"""
    column_list = ['id', 'ten', 'gia', 'nhom_tuy_chon', 'hinh', 'ngay_tao']
    column_searchable_list = ['ten']
    column_filters = ['nhom_tuy_chon_id']
    
    form_args = {
        'nhom_tuy_chon_id': {
            'label': 'Nhóm tùy chọn',
            'get_label': lambda x: x.ten
        }
    }
    
    def _format_price(view, context, model, name):
        """Format giá thành VNĐ"""
        value = getattr(model, name, 0) or 0
        return f"{value:,} đ"
    
    def _format_nhom_tuy_chon(view, context, model, name):
        """Format hiển thị nhóm tùy chọn"""
        if model.nhom_tuy_chon:
            return model.nhom_tuy_chon.ten
        return '-'
    
    def _format_image(view, context, model, name):
        """Hiển thị hình ảnh"""
        url = getattr(model, name, None)
        if url:
            return Markup(f'<img src="{url}" style="max-width: 50px; max-height: 50px; border-radius: 4px;">')
        return '-'
    
    column_formatters = {
        'gia': _format_price,
        'nhom_tuy_chon': _format_nhom_tuy_chon,
        'hinh': _format_image
    }
    
    column_labels = {
        'ten': 'Tên tùy chọn',
        'gia': 'Giá',
        'nhom_tuy_chon': 'Nhóm tùy chọn',
        'hinh': 'Hình ảnh',
        'ngay_tao': 'Ngày tạo'
    }


class ThanhToanModelView(SecureModelView):
    """ModelView cho Thanh Toán"""
    column_list = ['id', 'so_tien', 'phuong_thuc', 'trang_thai', 'doanh_thu_id', 'ngay_tao']
    column_filters = ['trang_thai', 'phuong_thuc', 'doanh_thu_id']
    
    form_args = {
        'doanh_thu_id': {
            'label': 'Doanh thu',
            'get_label': lambda x: f"Doanh thu #{x.id} - {x.tien_cuoi_cung:,} đ"
        }
    }
    
    def _format_currency(view, context, model, name):
        """Format số tiền thành VNĐ"""
        value = getattr(model, name, 0) or 0
        return f"{value:,} đ"
    
    def _format_doanh_thu_id(view, context, model, name):
        """Format hiển thị doanh thu ID"""
        if model.doanh_thu_id:
            return f"Doanh thu #{model.doanh_thu_id}"
        return '-'
    
    column_formatters = {
        'so_tien': _format_currency,
        'doanh_thu_id': _format_doanh_thu_id
    }
    
    column_labels = {
        'so_tien': 'Số tiền',
        'phuong_thuc': 'Phương thức',
        'trang_thai': 'Trạng thái',
        'doanh_thu_id': 'Doanh thu',
        'ngay_tao': 'Ngày tạo'
    }


class YCMonGhiModelView(SecureModelView):
    """ModelView cho Yêu Cầu Món Ghi"""
    column_list = ['id', 'trang_thai', 'ly_do', 'trang_thai_truoc', 'mon_ghi', 'quan_ly_duyet_id', 'ngay_tao']
    column_filters = ['trang_thai']
    column_searchable_list = ['ly_do']
    
    form_args = {
        'mon_ghi_id': {
            'label': 'Món ghi',
            'get_label': lambda x: f"Món ghi #{x.id} - {x.mo_ta_mon.ten if x.mo_ta_mon else 'N/A'}"
        }
    }
    
    def _format_mon_ghi(view, context, model, name):
        """Format hiển thị món ghi"""
        if model.mon_ghi:
            mon_ten = model.mon_ghi.mo_ta_mon.ten if model.mon_ghi.mo_ta_mon else 'N/A'
            return f"Món ghi #{model.mon_ghi.id} - {mon_ten}"
        return '-'
    
    column_formatters = {
        'mon_ghi': _format_mon_ghi
    }
    
    column_labels = {
        'trang_thai': 'Trạng thái',
        'ly_do': 'Lý do',
        'trang_thai_truoc': 'Trạng thái trước',
        'mon_ghi': 'Món ghi',
        'quan_ly_duyet_id': 'Quản lý duyệt',
        'ngay_tao': 'Ngày tạo'
    }


class ThongBaoModelView(SecureModelView):
    """ModelView cho Thông Báo"""
    column_list = ['id', 'tieu_de', 'noi_dung', 'phan_loai', 'da_doc', 'nguoi_nhan_id', 'link', 'ngay_tao']
    column_filters = ['phan_loai', 'da_doc', 'nguoi_nhan_id']
    column_searchable_list = ['tieu_de', 'noi_dung']
    
    def _format_nguoi_nhan_id(view, context, model, name):
        """Format hiển thị người nhận ID"""
        # ThôngBao không có relationship, chỉ có nguoi_nhan_id
        # Có thể query để lấy tên nếu cần
        return f"Người dùng #{model.nguoi_nhan_id}"
    
    column_formatters = {
        'nguoi_nhan_id': _format_nguoi_nhan_id
    }
    
    column_labels = {
        'tieu_de': 'Tiêu đề',
        'noi_dung': 'Nội dung',
        'phan_loai': 'Phân loại',
        'da_doc': 'Đã đọc',
        'nguoi_nhan_id': 'Người nhận',
        'link': 'Link',
        'ngay_tao': 'Ngày tạo'
    }


class ChoXetDuyetView(SecureModelView):
    """View riêng để Admin xét duyệt tài khoản"""
    column_list = ['id', 'ten_tai_khoan', 'email', 'nguoi_dung', 'ngay_tao']
    column_searchable_list = ['ten_tai_khoan', 'email']
    
    can_create = False
    can_edit = False
    can_delete = False
    
    def _format_nguoi_dung(view, context, model, name):
        """Format hiển thị người dùng"""
        if model.nguoi_dung:
            return model.nguoi_dung.ho_ten
        return '-'
    
    column_formatters = {
        'nguoi_dung': _format_nguoi_dung
    }
    
    def get_query(self):
        """Chỉ hiển thị tài khoản chờ xét duyệt"""
        from app.data.models import TenVaiTro
        query = super().get_query()
        return query.join(VaiTro).filter(
            TaiKhoan.is_xac_thuc == True,
            VaiTro.vai_tro == TenVaiTro.VODANH
        )
    
    column_labels = {
        'ten_tai_khoan': 'Tên tài khoản',
        'email': 'Email',
        'nguoi_dung': 'Người dùng',
        'ngay_tao': 'Ngày đăng ký'
    }


def init_admin(app):
    """Khởi tạo Flask-Admin với các ModelView"""
    
    # Set template mode và base template trước khi init_app
    admin.template_mode = 'bootstrap4'
    admin.base_template = 'admin/base.html'  # Sử dụng custom base template
    
    # Set index view với custom template
    admin.init_app(
        app, 
        index_view=SecureAdminIndexView(name='Trang chủ', url='/admin')
    )
    
    # ============================================================
    # ĐĂNG KÝ CÁC MODEL VIEW
    # ============================================================
    
    # 1. Quản lý hệ thống
    admin.add_view(ChoXetDuyetView(TaiKhoan, db.session, name='Chờ Xét Duyệt', category='Hệ Thống', endpoint='cho_xet_duyet'))
    admin.add_view(TaiKhoanModelView(TaiKhoan, db.session, name='Tài Khoản', category='Hệ Thống'))
    admin.add_view(NguoiDungModelView(NguoiDung, db.session, name='Người Dùng', category='Hệ Thống'))
    admin.add_view(VaiTroModelView(VaiTro, db.session, name='Vai Trò', category='Hệ Thống'))
    
    # 2. Nhân viên
    admin.add_view(PhucVuModelView(PhucVu, db.session, name='Phục Vụ', category='Nhân Viên'))
    admin.add_view(LeTanModelView(LeTan, db.session, name='Lễ Tân', category='Nhân Viên'))
    admin.add_view(DauBepModelView(DauBep, db.session, name='Đầu Bếp', category='Nhân Viên'))
    admin.add_view(ThuNganModelView(ThuNgan, db.session, name='Thu Ngân', category='Nhân Viên'))
    admin.add_view(QuanLyModelView(QuanLy, db.session, name='Quản Lý', category='Nhân Viên'))
    
    # 3. Nhà hàng
    admin.add_view(SecureModelView(KhuVuc, db.session, name='Khu Vực', category='Nhà Hàng'))
    admin.add_view(BanModelView(Ban, db.session, name='Bàn', category='Nhà Hàng'))
    admin.add_view(PhienBanModelView(PhienBan, db.session, name='Phiên Bàn', category='Nhà Hàng'))
    admin.add_view(PhanCongModelView(PhanCong, db.session, name='Phân Công', category='Nhà Hàng'))
    
    # 4. Khung giờ
    admin.add_view(SecureModelView(KhungGio, db.session, name='Khung Giờ', category='Lịch'))
    admin.add_view(SecureModelView(KhungGioAn, db.session, name='Khung Giờ Ăn', category='Lịch'))
    admin.add_view(SecureModelView(KhungGioDatBan, db.session, name='Khung Giờ Đặt Bàn', category='Lịch'))
    
    # 5. Thực đơn
    admin.add_view(SecureModelView(ThucDon, db.session, name='Thực Đơn', category='Thực Đơn'))
    admin.add_view(NhomMonModelView(NhomMon, db.session, name='Nhóm Món', category='Thực Đơn'))
    admin.add_view(MoTaMonModelView(MoTaMon, db.session, name='Mô Tả Món', category='Thực Đơn'))
    admin.add_view(SecureModelView(NhomTuyChon, db.session, name='Nhóm Tùy Chọn', category='Thực Đơn'))
    admin.add_view(TuyChonMonModelView(TuyChonMon, db.session, name='Tùy Chọn Món', category='Thực Đơn'))
    
    # 6. Đơn hàng
    admin.add_view(PhieuMonModelView(PhieuMon, db.session, name='Phiếu Món', category='Đơn Hàng'))
    admin.add_view(MonGhiModelView(MonGhi, db.session, name='Món Ghi', category='Đơn Hàng'))
    
    # 7. Doanh thu & Thanh toán
    admin.add_view(DoanhThuModelView(DoanhThu, db.session, name='Doanh Thu', category='Tài Chính'))
    admin.add_view(ThanhToanModelView(ThanhToan, db.session, name='Thanh Toán', category='Tài Chính'))
    admin.add_view(SecureModelView(CauHinhThue, db.session, name='Cấu Hình Thuế', category='Tài Chính'))
    
    # 8. Khuyến mãi
    admin.add_view(KhuyenMaiModelView(KhuyenMai, db.session, name='Khuyến Mãi', category='Khuyến Mãi'))
    admin.add_view(SecureModelView(KhuyenMaiTheoPhanTram, db.session, name='KM Theo %', category='Khuyến Mãi'))
    admin.add_view(SecureModelView(KhuyenMaiCung, db.session, name='KM Cố Định', category='Khuyến Mãi'))
    
    # 9. Yêu cầu & Thông báo
    admin.add_view(YeuCauModelView(YeuCau, db.session, name='Yêu Cầu', category='Hệ Thống'))
    admin.add_view(YCMonGhiModelView(YCMonGhi, db.session, name='YC Món Ghi', category='Hệ Thống'))
    admin.add_view(SecureModelView(YCPhieuMon, db.session, name='YC Phiếu Món', category='Hệ Thống'))
    admin.add_view(ThongBaoModelView(ThongBao, db.session, name='Thông Báo', category='Hệ Thống'))
    
    print("✅ Flask-Admin đã được khởi tạo thành công!")

