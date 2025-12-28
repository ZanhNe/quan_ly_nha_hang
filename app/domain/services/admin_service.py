# Admin Service - Xử lý logic cho Admin
# Chạy transaction qua TransactionManager, data trả về bọc qua Schema
from typing import List, Dict, Any
from injector import inject
from app.domain.services.interfaces.interfaces import (
    IAdminTaiKhoanService, IAdminNguoiDungService, IAdminKhuVucService,
    IAdminBanService, IAdminThucDonService, IAdminKhuyenMaiService, IAdminCauHinhThueService
)
from app.data.dao.interfaces.interfaces import (
    IAdminTaiKhoanDAO, IAdminNguoiDungDAO, IAdminKhuVucDAO, IAdminBanDAO,
    IAdminThucDonDAO, IAdminKhuyenMaiDAO, IAdminCauHinhThueDAO, IVaiTroDAO
)
from app.data.models import (
    TaiKhoan, NguoiDung, PhucVu, LeTan, DauBep, ThuNgan, QuanLy,
    KhuVuc, Ban, NhomMon, MoTaMon, KhuyenMai, KhuyenMaiTheoPhanTram, KhuyenMaiCung, CauHinhThue,
    TrangThaiTaiKhoan, TrangThaiBan, TrangThaiMon, TenVaiTro
)
from app.domain.services.transaction_manager import transaction_manager
from app.utils.helper import Helper
from app.schemas.schema import (
    AdminTaiKhoanOutSchema, AdminNhanVienOutSchema, AdminKhuVucOutSchema,
    AdminBanOutSchema, AdminMonOutSchema, AdminNhomMonOutSchema, 
    AdminKhuyenMaiOutSchema, AdminCauHinhThueOutSchema, AdminThucDonOutSchema
)

from app.schemas.init_schema import (
    admin_thuc_don_out_schema
)


class AdminTaiKhoanService(IAdminTaiKhoanService):
    # Quản lý tài khoản (Admin dùng)
    
    @inject
    def __init__(self, tai_khoan_dao: IAdminTaiKhoanDAO, vai_tro_dao: IVaiTroDAO, nguoi_dung_dao: IAdminNguoiDungDAO):
        self.tai_khoan_dao = tai_khoan_dao
        self.vai_tro_dao = vai_tro_dao
        self.nguoi_dung_dao = nguoi_dung_dao
        self.helper = Helper()
        self._out_schema = AdminTaiKhoanOutSchema()
    
    def lay_danh_sach_tai_khoan(self, page: int, per_page: int, filters: dict) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách tài khoản") as session:
            ds_tai_khoan, total, has_next = self.tai_khoan_dao.find_all(session, page, per_page, filters)
            return {
                'items': self._out_schema.dump(ds_tai_khoan, many=True),
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_next': has_next
            }
    
    def lay_chi_tiet_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy chi tiết tài khoản") as session:
            tai_khoan = self.tai_khoan_dao.find_by_id(session, tai_khoan_id)
            if not tai_khoan:
                raise Exception("Tài khoản không tồn tại")
            return self._out_schema.dump(tai_khoan)
    
    def tao_tai_khoan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo tài khoản") as session:
            if self.tai_khoan_dao.check_email_exists(session, data['email']):
                raise Exception("Email đã được sử dụng")
            
            if self.tai_khoan_dao.check_ten_tai_khoan_exists(session, data['ten_tai_khoan']):
                raise Exception("Tên tài khoản đã tồn tại")
            
            vai_tro = self.vai_tro_dao.find_by_ten_vai_tro(session, data.get('vai_tro', 'VODANH'))
            if not vai_tro:
                raise Exception("Vai trò không hợp lệ")
            
            tai_khoan = TaiKhoan(
                ten_tai_khoan=data['ten_tai_khoan'],
                email=data['email'],
                mat_khau=self.helper.hass_pass(data['mat_khau']),
                vai_tro_id=vai_tro.id,
                trang_thai=TrangThaiTaiKhoan.MO,
                is_xac_thuc=data.get('is_xac_thuc', False)
            )
            
            self.tai_khoan_dao.save(session, tai_khoan)
            return self._out_schema.dump(tai_khoan)
    
    def cap_nhat_tai_khoan(self, tai_khoan_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật tài khoản") as session:
            tai_khoan = self.tai_khoan_dao.find_by_id(session, tai_khoan_id)
            if not tai_khoan:
                raise Exception("Tài khoản không tồn tại")
            
            if 'email' in data and data['email'] != tai_khoan.email:
                if self.tai_khoan_dao.check_email_exists(session, data['email'], tai_khoan_id):
                    raise Exception("Email đã được sử dụng")

            mat_khau = self.helper.hass_pass(data['mat_khau']) if data.get('mat_khau') else None
            tai_khoan.cap_nhat_thong_tin(
                email=data.get('email'),
                mat_khau=mat_khau,
                is_xac_thuc=data.get('is_xac_thuc')
            )
            
            self.tai_khoan_dao.save(session, tai_khoan)
            return self._out_schema.dump(tai_khoan)
    
    def xoa_tai_khoan(self, tai_khoan_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa tài khoản") as session:
            tai_khoan = self.tai_khoan_dao.find_by_id(session, tai_khoan_id)
            if not tai_khoan:
                raise Exception("Tài khoản không tồn tại")
            
            # Nếu tài khoản đã gắn với info người dùng thì không cho xóa
            if tai_khoan.nguoi_dung:
                raise Exception("Không thể xóa tài khoản đã có thông tin người dùng")
            
            self.tai_khoan_dao.delete(session, tai_khoan)
            return True
    
    def khoa_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi khóa tài khoản") as session:
            tai_khoan = self.tai_khoan_dao.find_by_id(session, tai_khoan_id)
            if not tai_khoan:
                raise Exception("Tài khoản không tồn tại")
            
            tai_khoan.khoa()
            self.tai_khoan_dao.save(session, tai_khoan)
            return self._out_schema.dump(tai_khoan)
    
    def mo_khoa_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi mở khóa tài khoản") as session:
            tai_khoan = self.tai_khoan_dao.find_by_id(session, tai_khoan_id)
            if not tai_khoan:
                raise Exception("Tài khoản không tồn tại")
            
            tai_khoan.mo_khoa()
            self.tai_khoan_dao.save(session, tai_khoan)
            return self._out_schema.dump(tai_khoan)
    
    def lay_danh_sach_cho_xet_duyet(self) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi lấy danh sách tài khoản chờ xét duyệt') as session:
            ds_tai_khoan = self.tai_khoan_dao.find_cho_xet_duyet(session=session)
            return self._out_schema.dump(ds_tai_khoan, many=True)
    
    def xu_ly_duyet_tai_khoan(self, admin_id: int, tai_khoan_id: int, vai_tro_ten: str) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi duyệt tài khoản') as session:
            admin = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=admin_id)
            if not admin or admin.vai_tro.vai_tro != TenVaiTro.ADMIN:
                raise Exception('Bạn không có quyền duyệt tài khoản.')
            
            tai_khoan = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=tai_khoan_id)
            if not tai_khoan:
                raise Exception('Tài khoản không tồn tại.')
            
            tai_khoan.kien_tra_cho_duyet()
            
            vai_tro_moi = self.vai_tro_dao.find_by_ten_vai_tro(session=session, ten_vai_tro=vai_tro_ten)
            if not vai_tro_moi or vai_tro_ten == 'VODANH':
                raise Exception(f'Vai trò {vai_tro_ten} không hợp lệ.')
            
            tai_khoan.vai_tro = vai_tro_moi
            
            old_nguoi_dung = tai_khoan.nguoi_dung
            if not old_nguoi_dung:
                raise Exception('Người dùng không tồn tại.')
            
            new_nguoi_dung = NguoiDung.create_by_role(vai_tro_ten, old_nguoi_dung.ho_ten, tai_khoan.id)
            tai_khoan.nguoi_dung = new_nguoi_dung

            self.nguoi_dung_dao.swap_nguoi_dung_subclass(session, old_nguoi_dung, new_nguoi_dung)
            
            
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)
            
            result = self._out_schema.dump(tai_khoan)
            result['message'] = 'Duyệt tài khoản thành công.'
            return result
    
    def xu_ly_tu_choi_tai_khoan(self, admin_id: int, tai_khoan_id: int) -> bool:
        with transaction_manager.transaction('Lỗi khi từ chối tài khoản') as session:
            admin = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=admin_id)
            if not admin or admin.vai_tro.vai_tro != TenVaiTro.ADMIN:
                raise Exception('Bạn không có quyền từ chối tài khoản.')
            
            tai_khoan = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=tai_khoan_id)
            if not tai_khoan:
                raise Exception('Tài khoản không tồn tại.')
            
            tai_khoan.khoa()
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)
            return True

class AdminNguoiDungService(IAdminNguoiDungService):
    # Quản lý nhân viên/người dùng trong hệ thống
    
    @inject
    def __init__(self, nguoi_dung_dao: IAdminNguoiDungDAO, tai_khoan_dao: IAdminTaiKhoanDAO, 
                 khu_vuc_dao: IAdminKhuVucDAO, vai_tro_dao: IVaiTroDAO):
        self.nguoi_dung_dao = nguoi_dung_dao
        self.tai_khoan_dao = tai_khoan_dao
        self.khu_vuc_dao = khu_vuc_dao
        self.vai_tro_dao = vai_tro_dao
        self.helper = Helper()
        self._out_schema = AdminNhanVienOutSchema()
    
    def lay_danh_sach_nhan_vien(self, page: int, per_page: int, vai_tro: str = None) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách nhân viên") as session:
            ds_nguoi_dung, total, has_next = self.nguoi_dung_dao.find_all(session, page, per_page, vai_tro)
            return {
                'items': [self._serialize(nd) for nd in ds_nguoi_dung],
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_next': has_next
            }
    
    def tao_nhan_vien(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo nhân viên") as session:
            vai_tro_ten = data.get('vai_tro', 'PHUCVU')
            
            # Check trùng email
            if self.tai_khoan_dao.check_email_exists(session, data['email']):
                raise Exception("Email đã được sử dụng")
            
            # Validate username unique
            if self.tai_khoan_dao.check_ten_tai_khoan_exists(session, data['ten_tai_khoan']):
                raise Exception("Tên tài khoản đã tồn tại")
            
            # Get vai tro
            vai_tro = self.vai_tro_dao.find_by_ten_vai_tro(session, vai_tro_ten)
            if not vai_tro:
                raise Exception("Vai trò không hợp lệ")
            
            # Create account
            tai_khoan = TaiKhoan(
                ten_tai_khoan=data['ten_tai_khoan'],
                email=data['email'],
                mat_khau=self.helper.hass_pass(data['mat_khau']),
                vai_tro_id=vai_tro.id,
                trang_thai=TrangThaiTaiKhoan.MO,
                is_xac_thuc=True
            )
            self.tai_khoan_dao.save(session, tai_khoan)
            
            nguoi_dung = NguoiDung.create_by_role(vai_tro_ten, data['ho_ten'], tai_khoan.id, khu_vuc_id=data.get('khu_vuc_id'))
            self.nguoi_dung_dao.save(session, nguoi_dung)
            return self._out_schema.dump(nguoi_dung)
    
    def cap_nhat_nhan_vien(self, nguoi_dung_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật nhân viên") as session:
            nguoi_dung = self.nguoi_dung_dao.find_by_id(session, nguoi_dung_id)
            if not nguoi_dung:
                raise Exception("Nhân viên không tồn tại")
            
            if 'ho_ten' in data:
                nguoi_dung.cap_nhat_ho_ten(data['ho_ten'])
            
            if isinstance(nguoi_dung, PhucVu) and 'khu_vuc_id' in data:
                if self.nguoi_dung_dao.check_has_active_phien(session, nguoi_dung_id):
                    raise Exception("Không thể đổi khu vực khi đang có phân công phục vụ")
                
                khu_vuc = self.khu_vuc_dao.find_by_id(session, data['khu_vuc_id'])
                if not khu_vuc:
                    raise Exception("Khu vực không tồn tại")
                nguoi_dung.khu_vuc_id = data['khu_vuc_id']
            
            self.nguoi_dung_dao.save(session, nguoi_dung)
            return self._out_schema.dump(nguoi_dung)
    
    def xoa_nhan_vien(self, nguoi_dung_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa nhân viên") as session:
            nguoi_dung = self.nguoi_dung_dao.find_by_id(session, nguoi_dung_id)
            if not nguoi_dung:
                raise Exception("Nhân viên không tồn tại")
            
            if self.nguoi_dung_dao.check_has_active_phien(session, nguoi_dung_id):
                raise Exception("Không thể xóa nhân viên đang có phân công phục vụ")
            
            self.nguoi_dung_dao.delete(session, nguoi_dung)
            return True


class AdminKhuVucService(IAdminKhuVucService):
    # Quản lý các tầng/phòng trong nhà hàng
    
    @inject
    def __init__(self, khu_vuc_dao: IAdminKhuVucDAO):
        self.khu_vuc_dao = khu_vuc_dao
        self._out_schema = AdminKhuVucOutSchema()
    
    def lay_danh_sach_khuvuc(self) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách khu vực") as session:
            ds_khuvuc = self.khu_vuc_dao.find_all(session)
            return self._out_schema.dump(ds_khuvuc, many=True)
    
    def tao_khuvuc(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo khu vực") as session:
            if self.khu_vuc_dao.check_ten_exists(session, data['ten']):
                raise Exception("Tên khu vực đã tồn tại")
            
            khu_vuc = KhuVuc(ten=data['ten'])
            self.khu_vuc_dao.save(session, khu_vuc)
            return self._out_schema.dump(khu_vuc)
    
    def cap_nhat_khuvuc(self, khu_vuc_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật khu vực") as session:
            khu_vuc = self.khu_vuc_dao.find_by_id(session, khu_vuc_id)
            if not khu_vuc:
                raise Exception("Khu vực không tồn tại")
            
            if 'ten' in data and data['ten'] != khu_vuc.ten:
                if self.khu_vuc_dao.check_ten_exists(session, data['ten'], khu_vuc_id):
                    raise Exception("Tên khu vực đã tồn tại")
                khu_vuc.cap_nhat_ten(data['ten'])
            
            self.khu_vuc_dao.save(session, khu_vuc)
            return self._out_schema.dump(khu_vuc)
    
    def xoa_khuvuc(self, khu_vuc_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa khu vực") as session:
            khu_vuc = self.khu_vuc_dao.find_by_id(session, khu_vuc_id)
            if not khu_vuc:
                raise Exception("Khu vực không tồn tại")
            
            # Check có bàn không
            if self.khu_vuc_dao.count_ban(session, khu_vuc_id) > 0:
                raise Exception("Không thể xóa khu vực có bàn")
            
            # Check có nhân viên không
            if self.khu_vuc_dao.count_nhan_vien(session, khu_vuc_id) > 0:
                raise Exception("Không thể xóa khu vực có nhân viên")
            
            self.khu_vuc_dao.delete(session, khu_vuc)
            return True
    
    def _serialize(self, khu_vuc: KhuVuc, session) -> Dict[str, Any]:
        """Serialize using schema output format"""
        return {
            'id': khu_vuc.id,
            'ten': khu_vuc.ten,
            'so_ban': self.khu_vuc_dao.count_ban(session, khu_vuc.id),
            'so_nhan_vien': self.khu_vuc_dao.count_nhan_vien(session, khu_vuc.id),
            'ngay_tao': khu_vuc.ngay_tao.isoformat() if khu_vuc.ngay_tao else None
        }


class AdminBanService(IAdminBanService):
    # Xử lý logic liên quan đến bàn ăn
    
    @inject
    def __init__(self, ban_dao: IAdminBanDAO, khu_vuc_dao: IAdminKhuVucDAO):
        self.ban_dao = ban_dao
        self.khu_vuc_dao = khu_vuc_dao
        self._out_schema = AdminBanOutSchema()
    
    def lay_danh_sach_ban(self, khu_vuc_id: int = None, trang_thai: str = None) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách bàn") as session:
            ds_ban = self.ban_dao.find_all(session, khu_vuc_id, trang_thai)
            return self._out_schema.dump(ds_ban, many=True)
    
    def tao_ban(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo bàn") as session:
            if self.ban_dao.check_ten_exists(session, data['ten'], data['khu_vuc_id']):
                raise Exception("Tên bàn đã tồn tại trong khu vực")
            
            ban = Ban(ten=data['ten'], khu_vuc_id=data['khu_vuc_id'], so_ghe=data.get('so_ghe', 4), trang_thai=TrangThaiBan.TRONG)
            self.ban_dao.save(session, ban)
            return self._out_schema.dump(ban)
    
    def cap_nhat_ban(self, ban_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật bàn") as session:
            ban = self.ban_dao.find_by_id(session, ban_id)
            if not ban:
                raise Exception("Bàn không tồn tại")
            
            if 'ten' in data or 'khu_vuc_id' in data:
                new_ten = data.get('ten', ban.ten)
                new_khu_vuc_id = data.get('khu_vuc_id', ban.khu_vuc_id)
                if self.ban_dao.check_ten_exists(session, new_ten, new_khu_vuc_id, ban_id):
                    raise Exception("Tên bàn đã tồn tại trong khu vực")
            
            ban.cap_nhat_thong_tin(ten=data.get('ten'), so_ghe=data.get('so_ghe'), khu_vuc_id=data.get('khu_vuc_id'))
            self.ban_dao.save(session, ban)
            return self._out_schema.dump(ban)
    
    def xoa_ban(self, ban_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa bàn") as session:
            ban = self.ban_dao.find_by_id(session, ban_id)
            if not ban:
                raise Exception("Bàn không tồn tại")
            
            if not ban.kiem_tra_ban_trong():
                raise Exception("Không thể xóa bàn đang có khách hoặc đang sử dụng")
            
            self.ban_dao.delete(session, ban)
            return True
    
    def reset_trang_thai_ban(self, ban_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi reset trạng thái bàn") as session:
            ban = self.ban_dao.find_by_id(session, ban_id)
            if not ban:
                raise Exception("Bàn không tồn tại")
            
            ban.hoan_thanh()
            self.ban_dao.save(session, ban)
            return self._out_schema.dump(ban)


class AdminThucDonService(IAdminThucDonService):
    # Quản lý Menu/Thực đơn (Món ăn, Tùy chọn)
    
    @inject
    def __init__(self, thuc_don_dao: IAdminThucDonDAO):
        self.thuc_don_dao = thuc_don_dao
        self._mon_schema = AdminMonOutSchema()
        self._nhom_mon_schema = AdminNhomMonOutSchema()
    
    def lay_thuc_don_chi_tiet(self) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy thực đơn") as session:
            thuc_don = self.thuc_don_dao.find_thuc_don(session)
            if not thuc_don:
                raise Exception("Thực đơn không tồn tại")
            
            thuc_don = admin_thuc_don_out_schema.dump(thuc_don)

            return thuc_don
    
    def tao_nhom_mon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo nhóm món") as session:
            thuc_don = self.thuc_don_dao.find_thuc_don(session)
            if not thuc_don:
                raise Exception("Thực đơn không tồn tại")
            
            if self.thuc_don_dao.check_ten_nhom_mon_exists(session, data['ten'], thuc_don.id):
                raise Exception("Tên nhóm món đã tồn tại")
            
            nhom_mon = NhomMon(ten=data['ten'], thuc_don_id=thuc_don.id)
            self.thuc_don_dao.save_nhom_mon(session, nhom_mon)
            return self._nhom_mon_schema.dump(nhom_mon)
    
    def cap_nhat_nhom_mon(self, nhom_mon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật nhóm món") as session:
            nhom_mon = self.thuc_don_dao.find_nhom_mon_by_id(session, nhom_mon_id)
            if not nhom_mon:
                raise Exception("Nhóm món không tồn tại")
            
            if 'ten' in data and data['ten'] != nhom_mon.ten:
                if self.thuc_don_dao.check_ten_nhom_mon_exists(session, data['ten'], nhom_mon.thuc_don_id, nhom_mon_id):
                    raise Exception("Tên nhóm món đã tồn tại")
                nhom_mon.cap_nhat_ten(data['ten'])
            
            self.thuc_don_dao.save_nhom_mon(session, nhom_mon)
            return self._nhom_mon_schema.dump(nhom_mon)
    
    def xoa_nhom_mon(self, nhom_mon_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa nhóm món") as session:
            nhom_mon = self.thuc_don_dao.find_nhom_mon_by_id(session, nhom_mon_id)
            if not nhom_mon:
                raise Exception("Nhóm món không tồn tại")
            
            if self.thuc_don_dao.count_mon_in_nhom(session, nhom_mon_id) > 0:
                raise Exception("Không thể xóa nhóm món có món ăn")
            
            self.thuc_don_dao.delete_nhom_mon(session, nhom_mon)
            return True
    
    def tao_mon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo món") as session:
            nhom_mon = self.thuc_don_dao.find_nhom_mon_by_id(session, data['nhom_mon_id'])
            if not nhom_mon:
                raise Exception("Nhóm món không tồn tại")
            
            if self.thuc_don_dao.check_ten_mon_exists(session, data['ten']):
                raise Exception("Tên món đã tồn tại")
            
            mon = MoTaMon(
                ten=data['ten'],
                gia=data['gia'],
                nhom_mon_id=data['nhom_mon_id'],
                hinh=data.get('hinh'),
                trang_thai=TrangThaiMon.MOBAN
            )
            self.thuc_don_dao.save_mon(session, mon)
            return self._mon_schema.dump(mon)
    
    def cap_nhat_mon(self, mon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật món") as session:
            mon = self.thuc_don_dao.find_mon_by_id(session, mon_id)
            if not mon:
                raise Exception("Món không tồn tại")
            
            if 'ten' in data and data['ten'] != mon.ten:
                if self.thuc_don_dao.check_ten_mon_exists(session, data['ten'], mon_id):
                    raise Exception("Tên món đã tồn tại")
            
            mon.cap_nhat_thong_tin(
                ten=data.get('ten'),
                gia=data.get('gia'),
                hinh=data.get('hinh'),
                trang_thai=data.get('trang_thai')
            )
            
            self.thuc_don_dao.save_mon(session, mon)
            return self._mon_schema.dump(mon)
    
    def xoa_mon(self, mon_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa món") as session:
            mon = self.thuc_don_dao.find_mon_by_id(session, mon_id)
            if not mon:
                raise Exception("Món không tồn tại")
            
            mon.cap_nhat_thong_tin(trang_thai=TrangThaiMon.KHONGBAN)
            self.thuc_don_dao.save_mon(session, mon)
            return True
    
    def cap_nhat_trang_thai_mon(self, mon_id: int, trang_thai: str) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật trạng thái món") as session:
            mon = self.thuc_don_dao.find_mon_by_id(session, mon_id)
            if not mon:
                raise Exception("Món không tồn tại")
            
            if trang_thai not in [t.name for t in TrangThaiMon]:
                raise Exception("Trạng thái không hợp lệ")
            
            mon.cap_nhat_thong_tin(trang_thai=TrangThaiMon[trang_thai])
            self.thuc_don_dao.save_mon(session, mon)
            return self._mon_schema.dump(mon)
    


class AdminKhuyenMaiService(IAdminKhuyenMaiService):
    # Quản lý các chương trình giảm giá
    
    @inject
    def __init__(self, khuyen_mai_dao: IAdminKhuyenMaiDAO):
        self.khuyen_mai_dao = khuyen_mai_dao
        self._out_schema = AdminKhuyenMaiOutSchema()
    
    def lay_danh_sach_khuyen_mai(self, hoat_dong: bool = None) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách khuyến mãi") as session:
            ds_khuyen_mai = self.khuyen_mai_dao.find_all(session, hoat_dong)
            return self._out_schema.dump(ds_khuyen_mai, many=True)
    
    def tao_khuyen_mai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo khuyến mãi") as session:
            loai = data.get('loai', 'phan_tram')
            if loai == 'phan_tram':
                ti_le = data.get('ti_le', 0)
                if ti_le <= 0 or ti_le > 100:
                    raise Exception("Tỷ lệ phần trăm phải từ 1-100")
                khuyen_mai = KhuyenMaiTheoPhanTram(
                    ten=data['ten'],
                    mo_ta=data.get('mo_ta', ''),
                    gia_tri_don_hang_toi_thieu=data.get('gia_tri_don_hang_toi_thieu', 0),
                    gioi_han=data.get('gioi_han'),
                    phan_tram=ti_le,
                    hoat_dong=data.get('hoat_dong', True),
                    tu_dong_ap_dung=data.get('tu_dong_ap_dung', False),
                    thu_tu_uu_tien=data.get('thu_tu_uu_tien', 0)
                )
            else:
                so_tien_giam = data.get('so_tien_giam', 0)
                if so_tien_giam <= 0:
                    raise Exception("Số tiền giảm phải lớn hơn 0")
                khuyen_mai = KhuyenMaiCung(
                    ten=data['ten'],
                    mo_ta=data.get('mo_ta', ''),
                    gia_tri_don_hang_toi_thieu=data.get('gia_tri_don_hang_toi_thieu', 0),
                    gioi_han=data.get('gioi_han'),
                    so_tien_tru=so_tien_giam,
                    hoat_dong=data.get('hoat_dong', True),
                    tu_dong_ap_dung=data.get('tu_dong_ap_dung', False),
                    thu_tu_uu_tien=data.get('thu_tu_uu_tien', 0)
                )
            
            self.khuyen_mai_dao.save(session, khuyen_mai)
            return self._out_schema.dump(khuyen_mai)
    
    def cap_nhat_khuyen_mai(self, khuyen_mai_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật khuyến mãi") as session:
            khuyen_mai = self.khuyen_mai_dao.find_by_id(session, khuyen_mai_id)
            if not khuyen_mai:
                raise Exception("Khuyến mãi không tồn tại")
            
            # Check if already used
            if self.khuyen_mai_dao.check_has_doanhthu(session, khuyen_mai_id):
                raise Exception("Không thể sửa khuyến mãi đã được áp dụng")
            
            khuyen_mai.cap_nhat_thong_tin(**data)
            
            self.khuyen_mai_dao.save(session, khuyen_mai)
            return self._out_schema.dump(khuyen_mai)
    
    def xoa_khuyen_mai(self, khuyen_mai_id: int) -> bool:
        with transaction_manager.transaction("Lỗi khi xóa khuyến mãi") as session:
            khuyen_mai = self.khuyen_mai_dao.find_by_id(session, khuyen_mai_id)
            if not khuyen_mai:
                raise Exception("Khuyến mãi không tồn tại")
            
            khuyen_mai.cap_nhat_thong_tin(hoat_dong=False)
            self.khuyen_mai_dao.save(session, khuyen_mai)
            return True
    
    def kich_hoat_khuyen_mai(self, khuyen_mai_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi kích hoạt khuyến mãi") as session:
            khuyen_mai = self.khuyen_mai_dao.find_by_id(session, khuyen_mai_id)
            if not khuyen_mai:
                raise Exception("Khuyến mãi không tồn tại")
            
            khuyen_mai.cap_nhat_thong_tin(hoat_dong=True)
            self.khuyen_mai_dao.save(session, khuyen_mai)
            return self._out_schema.dump(khuyen_mai)
    
    def vo_hieu_hoa_khuyen_mai(self, khuyen_mai_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi vô hiệu hóa khuyến mãi") as session:
            khuyen_mai = self.khuyen_mai_dao.find_by_id(session, khuyen_mai_id)
            if not khuyen_mai:
                raise Exception("Khuyến mãi không tồn tại")
            
            khuyen_mai.cap_nhat_thong_tin(hoat_dong=False)
            self.khuyen_mai_dao.save(session, khuyen_mai)
            return self._out_schema.dump(khuyen_mai)


class AdminCauHinhThueService(IAdminCauHinhThueService):
    # Quản lý mấy cái cấu hình thuế VAT, phí dịch vụ...
    
    @inject
    def __init__(self, cau_hinh_thue_dao: IAdminCauHinhThueDAO):
        self.cau_hinh_thue_dao = cau_hinh_thue_dao
        self._out_schema = AdminCauHinhThueOutSchema()
    
    def lay_danh_sach_cau_hinh_thue(self) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách cấu hình thuế") as session:
            ds_cau_hinh = self.cau_hinh_thue_dao.find_all(session)
            return self._out_schema.dump(ds_cau_hinh, many=True)
    
    def lay_cau_hinh_thue_hien_tai(self) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy cấu hình thuế hiện tại") as session:
            cau_hinh = self.cau_hinh_thue_dao.find_active(session)
            if not cau_hinh:
                return None
            return self._out_schema.dump(cau_hinh)
    
    def tao_cau_hinh_thue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi tạo cấu hình thuế") as session:
            cau_hinh = CauHinhThue(
                ten=data['ten'],
                ti_le=data['ti_le'],
                hoat_dong=data.get('hoat_dong', False)
            )
            
            if cau_hinh.hoat_dong:
                self.cau_hinh_thue_dao.deactivate_all(session)
            
            self.cau_hinh_thue_dao.save(session, cau_hinh)
            return self._out_schema.dump(cau_hinh)
    
    def cap_nhat_cau_hinh_thue(self, cau_hinh_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi cập nhật cấu hình thuế") as session:
            cau_hinh = self.cau_hinh_thue_dao.find_by_id(session, cau_hinh_id)
            if not cau_hinh:
                raise Exception("Cấu hình thuế không tồn tại")
            
            if 'ten' in data:
                cau_hinh.ten = data['ten']
            if 'ti_le' in data:
                cau_hinh.ti_le = data['ti_le']
            
            self.cau_hinh_thue_dao.save(session, cau_hinh)
            return self._out_schema.dump(cau_hinh)
    
    def kich_hoat_cau_hinh_thue(self, cau_hinh_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi kích hoạt cấu hình thuế") as session:
            cau_hinh = self.cau_hinh_thue_dao.find_by_id(session, cau_hinh_id)
            if not cau_hinh:
                raise Exception("Cấu hình thuế không tồn tại")
            
            self.cau_hinh_thue_dao.deactivate_all(session)
            
            cau_hinh.hoat_dong = True
            self.cau_hinh_thue_dao.save(session, cau_hinh)
            return self._out_schema.dump(cau_hinh)
