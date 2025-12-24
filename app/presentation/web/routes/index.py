from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from app.container.container import injector_instance
from app.domain.services.interfaces.interfaces import IKhuVucService, IPhienBanService, IThucDonService, INguoiDungService, IDoanhThuService, IKhuyenMaiService, IBaoCaoService
from app.decorator.decorators import (login_required, verification_required, role_required )
from datetime import date, timedelta



index_bp = Blueprint('index', __name__)


khuvuc_service = injector_instance.get(interface=IKhuVucService)
phien_ban_service = injector_instance.get(interface=IPhienBanService)
thuc_don_service = injector_instance.get(interface=IThucDonService)
nguoi_dung_service = injector_instance.get(interface=INguoiDungService)
doanh_thu_service = injector_instance.get(interface=IDoanhThuService)
khuyen_mai_service = injector_instance.get(interface=IKhuyenMaiService)
bao_cao_service = injector_instance.get(interface=IBaoCaoService)


@index_bp.context_processor
def vars():
    nguoi_dung_id = session.get('current_user')['user_id']
    ds_thong_bao_out, has_more, unread_count = nguoi_dung_service.xu_ly_lay_thong_bao_nguoi_dung(nguoi_dung_id=nguoi_dung_id, page=1, limit=5)

    return {'ds_thong_bao': ds_thong_bao_out, 'has_more': has_more, 'unread_count': unread_count}

@index_bp.route('/')
def index():
    return redirect(url_for('index.trang_chu'))


@index_bp.route('/trang-chu')
@login_required
@verification_required
@role_required('PHUCVU', 'LETAN', 'DAUBEP', 'ADMIN', 'QUANLY', 'THUNGAN')
def trang_chu():
    return render_template('tong_quan.html')


@index_bp.route('/so-do-ban')
@login_required
@verification_required
@role_required('LETAN')
def so_do_ban():
    ds_khuvuc_schema = khuvuc_service.get_all_khuvuc()
    return render_template('page/le_tan/danh_dau.html', ds_khuvuc=ds_khuvuc_schema)
        


@index_bp.route('/danh-sach-phien')
@login_required
@verification_required
@role_required('PHUCVU')
def danh_sach_phien():
    try:
        phucvu_id = session.get('current_user')['user_id']
        ds_phien_ban = phien_ban_service.lay_danh_sach_phien_cua_phuc_vu(phucvu_id=phucvu_id)

        return render_template('page/phuc_vu/phien_ban.html', ds_phien_ban=ds_phien_ban)
    except Exception as e:
        print(e)

@index_bp.route('/danh-sach-phien/chi-tiet/<int:phien_ban_id>')        
@login_required
@verification_required
@role_required('PHUCVU')
def chi_tiet_phien(phien_ban_id):
    try:
        user_id = session['current_user']['user_id']
        phien_ban = phien_ban_service.lay_phien_ban_chi_tiet(phien_ban_id=phien_ban_id, user_id=user_id)
        return render_template('page/phuc_vu/chi_tiet_phien.html', phien_ban=phien_ban)
    except Exception as e:
        print(e)
        flash(str(e), 'err_msg')
        return redirect(url_for('index.trang_chu'))
    
@index_bp.route('/phien-ban/<int:phien_ban_id>/phieu-mon/<int:phieu_mon_id>', methods=['GET'])        
@login_required
@verification_required
@role_required('PHUCVU')
def chi_tiet_phieu_mon(phien_ban_id, phieu_mon_id):
    try:
        phieu_mon_out = phien_ban_service.lay_chi_tiet_phieu_mon(phien_ban_id=phien_ban_id, phieu_mon_id=phieu_mon_id)
        thuc_don_out = thuc_don_service.lay_thuc_don()
        return render_template('page/phuc_vu/ghi_mon.html', phieu_mon=phieu_mon_out, thuc_don=thuc_don_out)
    except Exception as err:
        print(err)
        return redirect(url_for('index.chi_tiet_phien', phien_ban_id=phien_ban_id))
    

@index_bp.route('/bep/danh-sach-phieu', methods=['GET'])        
@login_required
@verification_required
@role_required('DAUBEP')
def danh_sach_phieu_gui_bep():
    try:
        dau_bep_id = session['current_user']['user_id']
        ds_phieu_mon_out = phien_ban_service.lay_toan_bo_phieu_mon_da_gui_bep(dau_bep_id=dau_bep_id)

        return render_template('page/dau_bep/phieu_cho_bep.html', ds_phieu_mon=ds_phieu_mon_out)
    except Exception as err:
        print(err)
        return redirect(url_for('index.trang_chu'))

@index_bp.route('/bep/phieu-mon/<int:phieu_mon_id>', methods=['GET'])        
@login_required
@verification_required
@role_required('DAUBEP')
def chi_tiet_phieu_mon_dau_bep(phieu_mon_id):
    try:
        dau_bep_id = session.get('current_user')['user_id']
        phieu_mon_out = phien_ban_service.lay_chi_tiet_phieu_mon_cho_bep(dau_bep_id=dau_bep_id, phieu_mon_id=phieu_mon_id)
        return render_template('page/dau_bep/chi_tiet_phieu_mon.html', phieu_mon=phieu_mon_out)
    except Exception as err:
        print(err)
        return redirect(url_for('index.danh_sach_phieu_gui_bep'))
        

@index_bp.route('/thu-ngan/phien-thanh-toan', methods=['GET'])        
@login_required
@verification_required
@role_required('THUNGAN')
def phien_thanh_toan():
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        ds_phien_ban = phien_ban_service.lay_danh_sach_phien_cua_thu_ngan(thu_ngan_id=thu_ngan_id)
        ds_doanh_thu = doanh_thu_service.lay_doanh_thu_cua_thu_ngan(thu_ngan_id=thu_ngan_id)
        return render_template('page/thu_ngan/phien_thanh_toan.html', ds_phien_ban=ds_phien_ban, ds_doanh_thu=ds_doanh_thu)
    except Exception as err:
        print(err)
        return redirect(url_for('index.trang_chu'))

@index_bp.route('/thu-ngan/thanh-toan/<int:phien_ban_id>', methods=['GET'])        
@login_required
@verification_required
@role_required('THUNGAN')
def thanh_toan(phien_ban_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        phien_ban = phien_ban_service.lay_phien_ban_chi_tiet(phien_ban_id=phien_ban_id, user_id=thu_ngan_id)
        doanh_thu =  doanh_thu_service.lay_doanh_thu_cua_phien_ban(thu_ngan_id=thu_ngan_id, phien_ban_id=phien_ban_id)
        ds_khuyen_mai = khuyen_mai_service.lay_danh_sach_khuyen_mai_tuy_chon(thu_ngan_id=thu_ngan_id)
        if not doanh_thu:
            return render_template('page/thu_ngan/thanh_toan.html', phien_ban=phien_ban, ds_khuyen_mai=ds_khuyen_mai)
        preview = doanh_thu_service.xu_ly_tam_tinh(thu_ngan_id=thu_ngan_id, phien_ban_id=phien_ban_id)

        if not preview:
            print("Preview lỗi")
        
        return render_template('page/thu_ngan/thanh_toan.html', phien_ban=phien_ban, ds_khuyen_mai=ds_khuyen_mai, preview=preview)
    except Exception as err:
        print(err)
        return redirect(url_for('index.phien_thanh_toan'))


@index_bp.route('/thu-ngan/doanh-thu/<int:doanh_thu_id>', methods=['GET'])        
@login_required
@verification_required
@role_required('THUNGAN')
def trang_hoa_don(doanh_thu_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        doanh_thu_out = doanh_thu_service.lay_doanh_thu_chi_tiet(thu_ngan_id=thu_ngan_id, doanh_thu_id=doanh_thu_id)
        return render_template('page/thu_ngan/hoa_don.html', doanh_thu=doanh_thu_out)
    except Exception as err:
        print(err)
        return redirect(url_for('index.trang_chu'))


# ==========================================
# ROUTES CHO QUẢN LÝ
# ==========================================
@index_bp.route('/quan-ly/dashboard', methods=['GET'])        
@login_required
@verification_required
@role_required('QUANLY')
def quan_ly_dashboard():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        ds_yeu_cau = phien_ban_service.lay_danh_sach_yeu_cau(quan_ly_id=quan_ly_id)
        print(ds_yeu_cau)
        return render_template('page/quan_ly/dashboard.html', ds_yeu_cau=ds_yeu_cau)
    except Exception as err:
        print(err)
        flash(str(err), 'err_msg')
        return redirect(url_for('index.trang_chu'))


@index_bp.route('/quan-ly/bao-cao', methods=['GET'])        
@login_required
@verification_required
@role_required('QUANLY')
def bao_cao_tong_quan():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        # Lấy params từ query string, mặc định 7 ngày gần nhất
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=7)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_tong_quan(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return render_template('page/quan_ly/bao_cao.html', **data)
    except Exception as err:
        print(err)
        flash(str(err), 'err_msg')
        return redirect(url_for('index.quan_ly_dashboard'))


@index_bp.route('/quan-ly/bao-cao/doanh-thu', methods=['GET'])        
@login_required
@verification_required
@role_required('QUANLY')
def bao_cao_doanh_thu():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_bao_cao_doanh_thu(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return render_template('page/quan_ly/doanh_thu.html', **data)
    except Exception as err:
        print(err)
        flash(str(err), 'err_msg')
        return redirect(url_for('index.bao_cao_tong_quan'))


@index_bp.route('/quan-ly/bao-cao/nhan-vien', methods=['GET'])        
@login_required
@verification_required
@role_required('QUANLY')
def bao_cao_nhan_vien():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_hieu_suat_nhan_vien(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return render_template('page/quan_ly/nhan_vien.html', **data)
    except Exception as err:
        print(err)
        flash(str(err), 'err_msg')
        return redirect(url_for('index.bao_cao_tong_quan'))


@index_bp.route('/quan-ly/bao-cao/mon-an', methods=['GET'])        
@login_required
@verification_required
@role_required('QUANLY')
def bao_cao_mon_an():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_thong_ke_mon_an(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return render_template('page/quan_ly/mon_an.html', **data)
    except Exception as err:
        print(err)
        flash(str(err), 'err_msg')
        return redirect(url_for('index.bao_cao_tong_quan'))

