from flask import Blueprint, request, jsonify, session, url_for
from marshmallow import ValidationError
from app.decorator.decorators import login_required, role_required, verification_required
from app.container.container import injector_instance
from app.domain.services.interfaces.interfaces import IBanService, IPhienBanService, IThucDonService, IDoanhThuService, IBaoCaoService, ITaiKhoanService
from datetime import date, timedelta
from app.schemas.init_schema import (ds_ban_in_schema, ds_mon_ghi_create_schema, mon_ghi_status_update_schema
                                     , khuyen_mai_in_schema, yc_create_schema)
from app.extentions.extentions import socketio
from app.socket.socket import users
from dotenv import load_dotenv
import os

load_dotenv()


api_bp = Blueprint('api', __name__)

ban_service = injector_instance.get(interface=IBanService)
phien_ban_service = injector_instance.get(interface=IPhienBanService)
thuc_don_service = injector_instance.get(interface=IThucDonService)
doanh_thu_service = injector_instance.get(interface=IDoanhThuService)
bao_cao_service = injector_instance.get(interface=IBaoCaoService)
tai_khoan_service = injector_instance.get(interface=ITaiKhoanService)


@api_bp.route('/api/v1/bans', methods=['POST'])
@login_required
@verification_required
@role_required('LETAN')
def chon_ban():
    try:
        data = request.get_json()
        letan_id = session.get('current_user')['user_id']
        ds_ban_in = ds_ban_in_schema.load(data=data['table_ids'])
        ds_ban_out = ban_service.xu_ly_chon_ban(letan_id=letan_id, ban_schemas_in=ds_ban_in)

        socketio.emit('chon_ban', ds_ban_out, skip_sid=users[letan_id])

        return jsonify(ds_ban_out), 200
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            print(err)
            return jsonify({'message': str(err)}), 400
        else:
            print(err)
            return jsonify({'message': str(err)}), 400
        
@api_bp.route('/api/v1/resend-email-verify')
def gui_lai_xac_thuc_email():
    pass

@api_bp.route('/api/v1/phien-ban/<int:phien_ban_id>/dam-nhan', methods=['POST'])
@login_required
@verification_required
@role_required('PHUCVU')
def phien_ban_dam_nhan(phien_ban_id):
    try:
        phucvu_id = session.get('current_user')['user_id']
        phien_ban_out = phien_ban_service.xu_ly_dam_nhan_phien_ban(phien_ban_id=phien_ban_id, phucvu_id=phucvu_id)

        return jsonify(phien_ban_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400
    
@api_bp.route('/api/v1/phien-ban/<int:phien_ban_id>/phieu-mon', methods=['POST'])
@login_required
@verification_required
@role_required('PHUCVU')
def tao_phieu_mon(phien_ban_id):
    try:
        phucvu_id = session.get('current_user')['user_id']
        phieu_mon_out = phien_ban_service.xu_ly_tao_phieu_mon(phien_ban_id=phien_ban_id, phucvu_id=phucvu_id)
        return jsonify(phieu_mon_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/phieu-mon/<int:phieu_mon_id>/mon-ghi', methods=['POST'])
@login_required
@verification_required
@role_required('PHUCVU')
def them_mon_ghi(phieu_mon_id):
    try:
        data = request.get_json()
        phucvu_id = session['current_user']['user_id']
        ds_mon_ghi_create = ds_mon_ghi_create_schema.load(data=data)
        phieu_mon_out, phieu_mon_out_less = phien_ban_service.xu_ly_them_mon_ghi_phieu_mon(phucvu_id=phucvu_id, phieu_mon_id=phieu_mon_id, mon_ghi_create_schemas=ds_mon_ghi_create)
        ds_mon_ghi_out = phieu_mon_out['ds_mon_ghi']

        socketio.emit('gui_phieu', phieu_mon_out_less, skip_sid=users[phucvu_id])

        return jsonify({'data': ds_mon_ghi_out}), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

@api_bp.route('/api/v1/mon-ghi/<int:mon_ghi_id>/yeu-cau', methods=['POST'])
@login_required
@verification_required
@role_required('PHUCVU')
def cap_nhat_trang_thai_mon(mon_ghi_id):
    try:
        data = request.get_json()
        phucvu_id = session.get('current_user')['user_id']
        yc_create = yc_create_schema.load(data=data)
        yc_out = phien_ban_service.xu_ly_tao_yeu_cau_mon_ghi(phuc_vu_id=phucvu_id, mon_ghi_id=mon_ghi_id, yc_create=yc_create)
        return jsonify(yc_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

@api_bp.route('/api/v1/mon-ghi/<int:mon_ghi_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('DAUBEP')
def bep_cap_nhat_trang_thai_mon(mon_ghi_id):
    try:
        data = request.get_json()
        dau_bep_id = session['current_user']['user_id']
        mon_ghi_status_update = mon_ghi_status_update_schema.load(data=data)
        
        tb_out = None

        info_out = phien_ban_service.xu_ly_cap_nhat_trang_thai_mon(dau_bep_id=dau_bep_id, mon_ghi_id=mon_ghi_id, mon_ghi_status_update=mon_ghi_status_update)
        if isinstance(info_out, tuple):
            info_out, tb_out = info_out
            socketio.emit('hoan_thanh_phieu', tb_out, to=users[tb_out['nguoi_nhan_id']])
    

        return jsonify(info_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

@api_bp.route('/api/v1/phien-ban/<int:phien_ban_id>', methods=['GET'])
@login_required
@verification_required
@role_required('PHUCVU', 'LETAN', 'DAUBEP', 'ADMIN', 'QUANLY', 'THUNGAN')
def lay_chi_tiet_phien_ban(phien_ban_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        phien_ban_out = phien_ban_service.lay_phien_ban_chi_tiet(phien_ban_id=phien_ban_id, user_id=thu_ngan_id)
        return jsonify(phien_ban_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/thuc-don', methods=['GET'])
@login_required
@verification_required
@role_required('PHUCVU')
def thuc_don():
    try:
        thuc_don_out = thuc_don_service.lay_thuc_don()
        return jsonify(thuc_don_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400
    

@api_bp.route('/api/v1/phien-ban/<int:phien_ban_id>/doanh_thu/preview', methods=['GET'])
@login_required
@verification_required
@role_required('THUNGAN')
def lay_doanh_thu_preview(phien_ban_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        data_preview = doanh_thu_service.xu_ly_tam_tinh(thu_ngan_id=thu_ngan_id, phien_ban_id=phien_ban_id)

        return jsonify(data_preview), 200
    except Exception as err:
        print(err)
        return jsonify(str(err)), 400
    

@api_bp.route('/api/v1/doanh-thu/<int:doanh_thu_id>', methods=['GET'])
@login_required
@verification_required
@role_required('THUNGAN')
def chi_tiet_doanh_thu(doanh_thu_id):
    try:
        thu_ngan_id = thu_ngan_id = session.get('current_user')['user_id']
        doanh_thu_out = doanh_thu_service.lay_doanh_thu_chi_tiet(thu_ngan_id=thu_ngan_id, doanh_thu_id=doanh_thu_id)
        return jsonify(doanh_thu_out), 200
    except Exception as err:
        print(err)
        return jsonify(str(err)), 400

@api_bp.route('/api/v1/doanh-thu/<int:doanh_thu_id>', methods=['PUT'])
@login_required
@verification_required
@role_required('THUNGAN')
def ap_dung_khuyen_mai(doanh_thu_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        data = request.get_json()
        khuyen_mai_in = khuyen_mai_in_schema.load(data)
        data_preview = doanh_thu_service.xu_ly_ap_dung_khuyen_mai(thu_ngan_id=thu_ngan_id, doanh_thu_id=doanh_thu_id, khuyen_mai_in_schema=khuyen_mai_in)

        return jsonify(data_preview), 200
    except Exception as err:
        print(err)
        return jsonify(str(err)), 400
    
@api_bp.route('/api/v1/doanh-thu/<int:doanh_thu_id>/thanh-toan/tien-mat', methods=['POST'])
@login_required
@verification_required
@role_required('THUNGAN')
def thanh_toan_tien_mat(doanh_thu_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        data = request.get_json()
        khuyen_mai_in = khuyen_mai_in_schema.load(data)

        doanh_thu_out = doanh_thu_service.xu_ly_thanh_toan_tien_mat(thu_ngan_id=thu_ngan_id, doanh_thu_id=doanh_thu_id, khuyen_mai_in_schema=khuyen_mai_in)
        doanh_thu_out['redirect_url'] = url_for('index.trang_hoa_don', doanh_thu_id=doanh_thu_out['id'])
        return jsonify(doanh_thu_out), 200
    except Exception as err:
        print(err)
        return jsonify(str(err)), 400
    
@api_bp.route('/api/v1/doanh-thu/<int:doanh_thu_id>/thanh-toan/online', methods=['POST'])
@login_required
@verification_required
@role_required('THUNGAN')
def thanh_toan_online(doanh_thu_id):
    try:
        thu_ngan_id = session.get('current_user')['user_id']
        data = request.get_json()
        khuyen_mai_in = khuyen_mai_in_schema.load(data)

        doanh_thu_out = doanh_thu_service.xu_ly_thanh_toan_online(thu_ngan_id=thu_ngan_id, doanh_thu_id=doanh_thu_id, khuyen_mai_in_schema=khuyen_mai_in)
        doanh_thu_out['redirect_url'] = None
        return jsonify(doanh_thu_out), 200
    except Exception as err:
        print(err)
        return jsonify(str(err)), 400
    

@api_bp.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # 1. Lấy dữ liệu thô (raw bytes) - Bắt buộc phải dùng raw data để check chữ ký
        payload = request.get_data()
        sig_header = request.headers.get('STRIPE_SIGNATURE')
        endpoint_secret = os.getenv('WEBHOOK_SECRET')
        
        # print("Vào webhook")
        doanh_thu_service.xu_ly_hoan_thanh_online(payload=payload, sig_header=sig_header, endpoint_secret=endpoint_secret)
        
        return jsonify({'status': 'success'}), 200
    except Exception as err:
        print(err)
        return jsonify({'error': str(err)}), 200


# ==========================================
# API CHO QUẢN LÝ - XỬ LÝ YÊU CẦU
# ==========================================
@api_bp.route('/api/v1/yeu-cau/<int:yeu_cau_id>/chap-thuan', methods=['PUT'])
@login_required
@verification_required
@role_required('QUANLY')
def chap_thuan_yeu_cau(yeu_cau_id):
    try:
        quan_ly_id = session.get('current_user')['user_id']
        yc_out = phien_ban_service.xu_ly_chap_thuan_yeu_cau(quan_ly_id=quan_ly_id, yeu_cau_id=yeu_cau_id)
        return jsonify(yc_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/yeu-cau/<int:yeu_cau_id>/tu-choi', methods=['PUT'])
@login_required
@verification_required
@role_required('QUANLY')
def tu_choi_yeu_cau(yeu_cau_id):
    try:
        quan_ly_id = session.get('current_user')['user_id']
        yc_out = phien_ban_service.xu_ly_tu_choi_yeu_cau(quan_ly_id=quan_ly_id, yeu_cau_id=yeu_cau_id)
        return jsonify(yc_out), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


# ==========================================
# API CHO BÁO CÁO
# ==========================================
@api_bp.route('/api/v1/bao-cao/tong-quan', methods=['GET'])
@login_required
@verification_required
@role_required('QUANLY')
def api_bao_cao_tong_quan():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=7)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_tong_quan(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return jsonify(data), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/bao-cao/doanh-thu', methods=['GET'])
@login_required
@verification_required
@role_required('QUANLY')
def api_bao_cao_doanh_thu():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_bao_cao_doanh_thu(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return jsonify(data), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/bao-cao/nhan-vien', methods=['GET'])
@login_required
@verification_required
@role_required('QUANLY')
def api_bao_cao_nhan_vien():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_hieu_suat_nhan_vien(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return jsonify(data), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400


@api_bp.route('/api/v1/bao-cao/mon-an', methods=['GET'])
@login_required
@verification_required
@role_required('QUANLY')
def api_bao_cao_mon_an():
    try:
        quan_ly_id = session.get('current_user')['user_id']
        
        den_ngay_str = request.args.get('den_ngay', str(date.today()))
        tu_ngay_str = request.args.get('tu_ngay', str(date.today() - timedelta(days=30)))
        
        tu_ngay = date.fromisoformat(tu_ngay_str)
        den_ngay = date.fromisoformat(den_ngay_str)
        
        data = bao_cao_service.lay_thong_ke_mon_an(quan_ly_id=quan_ly_id, tu_ngay=tu_ngay, den_ngay=den_ngay)
        return jsonify(data), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

# ==========================================
# API CHO ADMIN - XÉT DUYỆT TÀI KHOẢN
# ==========================================
@api_bp.route('/api/v1/admin/tai-khoan/cho-xet-duyet', methods=['GET'])
@login_required
@verification_required
@role_required('ADMIN')
def lay_danh_sach_cho_xet_duyet():
    """Lấy danh sách tài khoản chờ Admin xét duyệt"""
    try:
        ds_tai_khoan = tai_khoan_service.lay_danh_sach_cho_xet_duyet()
        return jsonify(ds_tai_khoan), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

@api_bp.route('/api/v1/admin/tai-khoan/<int:tai_khoan_id>/duyet', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def duyet_tai_khoan(tai_khoan_id):
    """Admin duyệt tài khoản và gán vai trò"""
    try:
        admin_id = session.get('current_user')['user_id']
        data = request.get_json()
        vai_tro_ten = data.get('vai_tro')
        
        if not vai_tro_ten:
            return jsonify({'message': 'Vui lòng chọn vai trò'}), 400
        
        result = tai_khoan_service.xu_ly_duyet_tai_khoan(
            admin_id=admin_id,
            tai_khoan_id=tai_khoan_id,
            vai_tro_ten=vai_tro_ten
        )
        return jsonify(result), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

@api_bp.route('/api/v1/admin/tai-khoan/<int:tai_khoan_id>/tu-choi', methods=['PUT'])
@login_required
@verification_required
@role_required('ADMIN')
def tu_choi_tai_khoan(tai_khoan_id):
    """Admin từ chối tài khoản"""
    try:
        admin_id = session.get('current_user')['user_id']
        tai_khoan_service.xu_ly_tu_choi_tai_khoan(admin_id=admin_id, tai_khoan_id=tai_khoan_id)
        return jsonify({'message': 'Từ chối tài khoản thành công'}), 200
    except Exception as err:
        print(err)
        return jsonify({'message': str(err)}), 400

