# Admin Routes - Giao diện quản trị
# Dùng để render HTML cho các trang Admin
from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, session
from app.container.container import injector_instance
from app.decorator.decorators import (login_required, verification_required, role_required)
from app.domain.services.interfaces.interfaces import (
    IAdminTaiKhoanService, IAdminNguoiDungService, IAdminKhuVucService,
    IAdminBanService, IAdminThucDonService, IAdminKhuyenMaiService, 
    IAdminCauHinhThueService, ITaiKhoanService, INguoiDungService
)

admin_bp = Blueprint('admin', __name__)

def get_admin_services():
    return {
        'tai_khoan': injector_instance.get(interface=IAdminTaiKhoanService),
        'nguoi_dung': injector_instance.get(interface=IAdminNguoiDungService),
        'khu_vuc': injector_instance.get(interface=IAdminKhuVucService),
        'ban': injector_instance.get(interface=IAdminBanService),
        'thuc_don': injector_instance.get(interface=IAdminThucDonService),
        'khuyen_mai': injector_instance.get(interface=IAdminKhuyenMaiService),
        'cau_hinh_thue': injector_instance.get(interface=IAdminCauHinhThueService),
        'tai_khoan_xet_duyet': injector_instance.get(interface=ITaiKhoanService),
    }

nguoi_dung_service = injector_instance.get(interface=INguoiDungService)

@admin_bp.context_processor
def vars():
    nguoi_dung_id = session.get('current_user')['user_id']
    ds_thong_bao_out, has_more, unread_count = nguoi_dung_service.xu_ly_lay_thong_bao_nguoi_dung(nguoi_dung_id=nguoi_dung_id, page=1, limit=5)

    return {'ds_thong_bao': ds_thong_bao_out, 'has_more': has_more, 'unread_count': unread_count}


@admin_bp.route('/admin/dashboard')
@login_required
@verification_required
@role_required('ADMIN')
def admin_dashboard():
    # Trang chủ quản lý (Dashboard), xem mấy ông đang chờ duyệt
    services = get_admin_services()
    ds_cho_duyet = services['tai_khoan_xet_duyet'].lay_danh_sach_cho_xet_duyet()
    
    return render_template('page/admin/dashboard.html', 
                           ds_cho_duyet=ds_cho_duyet,
                           pending_count=len(ds_cho_duyet))


@admin_bp.route('/admin/tai-khoan')
@login_required
@verification_required
@role_required('ADMIN')
def admin_tai_khoan():
    # Danh sách account, có phân trang để load cho mượt
    services = get_admin_services()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    filters = {
        'trang_thai': request.args.get('trang_thai'),
        'is_xac_thuc': request.args.get('is_xac_thuc', type=bool) if request.args.get('is_xac_thuc') else None,
        'search': request.args.get('search')
    } # Lọc theo trạng thái, tìm kiếm tên/email...
    
    result = services['tai_khoan'].lay_danh_sach_tai_khoan(page, per_page, filters)
    
    print(result)

    return render_template('page/admin/tai_khoan.html',
                           items=result['items'],
                           total=result['total'],
                           page=result['page'],
                           per_page=result['per_page'],
                           has_next=result['has_next'],
                           filters=filters)


@admin_bp.route('/admin/tai-khoan/cho-duyet')
@login_required
@verification_required
@role_required('ADMIN')
def admin_tai_khoan_cho_duyet():
    """Danh sách tài khoản chờ xét duyệt"""
    services = get_admin_services()
    ds_cho_duyet = services['tai_khoan_xet_duyet'].lay_danh_sach_cho_xet_duyet()
    
    return render_template('page/admin/cho_duyet.html', ds_cho_duyet=ds_cho_duyet)


@admin_bp.route('/admin/nhan-vien')
@login_required
@verification_required
@role_required('ADMIN')
def admin_nhan_vien():
    """Quản lý nhân viên - với phân trang server-side"""
    services = get_admin_services()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    vai_tro = request.args.get('vai_tro')
    
    result = services['nguoi_dung'].lay_danh_sach_nhan_vien(page, per_page, vai_tro)
    ds_khu_vuc = services['khu_vuc'].lay_danh_sach_khuvuc()
    
    return render_template('page/admin/nhan_vien.html',
                           items=result['items'],
                           total=result['total'],
                           page=result['page'],
                           per_page=result['per_page'],
                           has_next=result['has_next'],
                           vai_tro_filter=vai_tro,
                           ds_khu_vuc=ds_khu_vuc)


@admin_bp.route('/admin/khu-vuc')
@login_required
@verification_required
@role_required('ADMIN')
def admin_khu_vuc():
    # Quản lý sảnh, tầng, khu vực bàn ăn
    services = get_admin_services()
    ds_khu_vuc = services['khu_vuc'].lay_danh_sach_khuvuc()
    
    return render_template('page/admin/khu_vuc.html', ds_khu_vuc=ds_khu_vuc)


@admin_bp.route('/admin/ban')
@login_required
@verification_required
@role_required('ADMIN')
def admin_ban():
    # Quản lý từng bàn cụ thể trong khu vực
    services = get_admin_services()
    
    khu_vuc_id = request.args.get('khu_vuc_id', type=int)
    trang_thai = request.args.get('trang_thai')
    
    ds_ban = services['ban'].lay_danh_sach_ban(khu_vuc_id, trang_thai)
    ds_khu_vuc = services['khu_vuc'].lay_danh_sach_khuvuc()
    
    return render_template('page/admin/ban.html',
                           ds_ban=ds_ban,
                           ds_khu_vuc=ds_khu_vuc,
                           khu_vuc_id=khu_vuc_id,
                           trang_thai_filter=trang_thai)


@admin_bp.route('/admin/nhom-mon')
@login_required
@verification_required
@role_required('ADMIN')
def admin_nhom_mon():
    # Chia món ăn theo nhóm (Khai vị, Món chính, Tráng miệng...)
    services = get_admin_services()
    thuc_don = services['thuc_don'].lay_thuc_don_chi_tiet()

    print(thuc_don)
    
    return render_template('page/admin/nhom_mon.html', 
                           ds_nhom_mon=thuc_don.get('ds_nhom_mon', []))


@admin_bp.route('/admin/mon')
@login_required
@verification_required
@role_required('ADMIN')
def admin_mon():
    """Quản lý món ăn - với filter theo nhóm món"""
    services = get_admin_services()
    
    nhom_mon_id = request.args.get('nhom_mon_id', type=int)
    thuc_don = services['thuc_don'].lay_thuc_don_chi_tiet()
    ds_nhom_mon = thuc_don.get('ds_nhom_mon', [])
    
    # Ở đây là lọc món theo filter nếu từ trên có gửi xuống
    ds_mon = []
    for nhom in ds_nhom_mon:
        if nhom_mon_id is None or nhom['id'] == nhom_mon_id:
            for mon in nhom.get('ds_mon', []):
                mon['nhom_mon_ten'] = nhom['ten']
                ds_mon.append(mon)
    
    return render_template('page/admin/mon.html',
                           ds_mon=ds_mon,
                           ds_nhom_mon=ds_nhom_mon,
                           nhom_mon_id=nhom_mon_id)


@admin_bp.route('/admin/khuyen-mai')
@login_required
@verification_required
@role_required('ADMIN')
def admin_khuyen_mai():
    """Quản lý khuyến mãi - với filter theo trạng thái"""
    services = get_admin_services()
    
    hoat_dong_str = request.args.get('hoat_dong')
    hoat_dong = None
    if hoat_dong_str == 'true':
        hoat_dong = True
    elif hoat_dong_str == 'false':
        hoat_dong = False
    
    ds_khuyen_mai = services['khuyen_mai'].lay_danh_sach_khuyen_mai(hoat_dong)
    
    return render_template('page/admin/khuyen_mai.html',
                           ds_khuyen_mai=ds_khuyen_mai,
                           hoat_dong_filter=hoat_dong_str)


@admin_bp.route('/admin/cau-hinh-thue')
@login_required
@verification_required
@role_required('ADMIN')
def admin_cau_hinh_thue():
    """Quản lý cấu hình thuế"""
    services = get_admin_services()
    
    ds_cau_hinh = services['cau_hinh_thue'].lay_danh_sach_cau_hinh_thue()
    cau_hinh_hien_tai = services['cau_hinh_thue'].lay_cau_hinh_thue_hien_tai()
    
    return render_template('page/admin/cau_hinh_thue.html',
                           ds_cau_hinh=ds_cau_hinh,
                           cau_hinh_hien_tai=cau_hinh_hien_tai)