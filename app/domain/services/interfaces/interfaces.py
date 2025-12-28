from typing import List, Dict, Any
from app.data.models import Ban, NguoiDung, PhucVu, PhienBan, PhieuMon, DoanhThu, KhuyenMai, CauHinhThue
from abc import ABC, abstractmethod



class INguoiDungService(ABC):

    @abstractmethod
    def xu_ly_lay_thong_bao_nguoi_dung(self, nguoi_dung_id: int, page: int, limit: int) -> List[Dict[str, Any]]:
        pass


#Interface cho pure service
class IBoChonNhanVien(ABC):
    @abstractmethod
    def chon_phuc_vu(self, ds_phucvu: List[PhucVu]) -> PhucVu:
        pass



#Interface cho service 
class IKhuVucService(ABC):
    @abstractmethod
    def get_all_khuvuc(self) -> List[Dict[str, Any]]:
        pass

class IBanService(ABC):
    
    @abstractmethod
    def get_ban_details(self, ban_schemas_in: List[Dict[str, Any]]) -> List[Ban]:
        pass

    @abstractmethod
    def xu_ly_chon_ban(self, letan_id: int, ban_schemas_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def xu_ly_dat_ban(self, letan_id: int, dat_ban_schemas_in: Dict[str, Any]) -> Dict[str, Any]:
        pass


class IPhienBanService(ABC):
    @abstractmethod
    def xu_ly_tao_yeu_cau_mon_ghi(self, phuc_vu_id: int, mon_ghi_id: int, yc_create) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_danh_sach_yeu_cau(self, quan_ly_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def xu_ly_chap_thuan_yeu_cau(self, quan_ly_id: int, yeu_cau_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_tu_choi_yeu_cau(self, quan_ly_id: int, yeu_cau_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_toan_bo_phieu_mon_da_gui_bep(self, dau_bep_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def lay_danh_sach_phien_cua_thu_ngan(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def lay_phien_ban_chi_tiet(self, phien_ban_id: int, user_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def lay_danh_sach_phien_cua_phuc_vu(self, phucvu_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def xu_ly_dam_nhan_phien_ban(self, phien_ban_id: int, phucvu_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_tao_phieu_mon(self, phien_ban_id: int, phucvu_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_chi_tiet_phieu_mon(self, phien_ban_id: int, phieu_mon_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_chi_tiet_phieu_mon_cho_bep(self, dau_bep_id: int, phieu_mon_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_them_mon_ghi_phieu_mon(self, phucvu_id: int, phieu_mon_id: int, mon_ghi_create_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_cap_nhat_trang_thai_mon(self, dau_bep_id: int, mon_ghi_id: int, mon_ghi_status_update: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IThemMonService(ABC):
    @abstractmethod
    def them_mon_ghi(self, phieu_mon: PhieuMon, mon_ghi_create_schemas: List[Dict[str, Any]]) -> PhieuMon:
        pass

class IThucDonService(ABC):
    @abstractmethod
    def lay_thuc_don(self) -> Dict[str, Any]:
        pass

class ITaiKhoanService(ABC):

    @abstractmethod
    def dang_ky_tai_khoan(self, tai_khoan_create: List[Dict[str, Any]]) -> bool:
        pass

    @abstractmethod
    def xac_thuc_tai_khoan(self, token: str) -> bool:
        pass

    @abstractmethod
    def dang_nhap_tai_khoan(self, tai_khoan_login: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def lay_danh_sach_cho_xet_duyet(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tài khoản chờ Admin xét duyệt"""
        pass
    
    @abstractmethod
    def xu_ly_duyet_tai_khoan(self, admin_id: int, tai_khoan_id: int, vai_tro_ten: str) -> Dict[str, Any]:
        """Admin duyệt tài khoản và gán vai trò"""
        pass
    
    @abstractmethod
    def xu_ly_tu_choi_tai_khoan(self, admin_id: int, tai_khoan_id: int) -> bool:
        """Admin từ chối tài khoản (có thể xóa hoặc khóa)"""
        pass

class IDoanhThuService(ABC):
    
    @abstractmethod
    def xu_ly_thanh_toan_online(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_doanh_thu_cua_phien_ban(self, thu_ngan_id: int, phien_ban_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_doanh_thu_chi_tiet(self, thu_ngan_id: int, doanh_thu_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def lay_doanh_thu_cua_thu_ngan(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def xu_ly_tam_tinh(self, thu_ngan_id: int, phien_ban_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_ap_dung_khuyen_mai(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_thanh_toan_tien_mat(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_hoan_thanh_online(self, payload, sig_header, endpoint_secret):
        pass

class IDoanhThuThanhToanService(ABC):

    @abstractmethod
    def tao_preview(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def xu_ly_thanh_toan_doanh_thu(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai_tu_dong: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None):
        pass

    @abstractmethod
    def xu_ly_thanh_toan_doanh_thu_online(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai_tu_dong: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None):
        pass

    @abstractmethod
    def xu_ly_hoan_thanh_thanh_toan_online(self, payload, sig_header, endpoint_secret) -> Dict[str, Any]:
        pass

class IKhuyenMaiService(ABC):

    @abstractmethod
    def lay_danh_sach_khuyen_mai_tuy_chon(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        pass


class IBaoCaoService(ABC):
    """Interface cho service báo cáo"""

    @abstractmethod
    def lay_tong_quan(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        """Lấy dữ liệu tổng quan dashboard"""
        pass

    @abstractmethod
    def lay_bao_cao_doanh_thu(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        """Lấy báo cáo doanh thu chi tiết"""
        pass

    @abstractmethod
    def lay_hieu_suat_nhan_vien(self, quan_ly_id: int, tu_ngay, den_ngay) -> List[Dict[str, Any]]:
        """Lấy hiệu suất nhân viên"""
        pass

    @abstractmethod
    def lay_thong_ke_mon_an(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        """Lấy thống kê món ăn"""
        pass


# ============================================================
# ADMIN SERVICE INTERFACES
# ============================================================

class IAdminTaiKhoanService(ABC):
    """Service interface cho quản lý tài khoản (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_cho_xet_duyet(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tài khoản chờ Admin xét duyệt"""
        pass

    @abstractmethod
    def xu_ly_duyet_tai_khoan(self, admin_id: int, tai_khoan_id: int, vai_tro_ten: str) -> Dict[str, Any]:
        """Admin duyệt tài khoản và gán vai trò"""
        pass

    @abstractmethod
    def xu_ly_tu_choi_tai_khoan(self, admin_id: int, tai_khoan_id: int) -> bool:
        """Admin từ chối tài khoản (có thể xóa hoặc khóa)"""
        pass

    @abstractmethod
    def lay_danh_sach_tai_khoan(self, page: int, per_page: int, filters: dict) -> Dict[str, Any]:
        """Lấy danh sách tài khoản với phân trang và filter"""
        pass
    
    @abstractmethod
    def lay_chi_tiet_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def tao_tai_khoan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo tài khoản mới - validate email/username unique, hash password"""
        pass
    
    @abstractmethod
    def cap_nhat_tai_khoan(self, tai_khoan_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật tài khoản"""
        pass
    
    @abstractmethod
    def xoa_tai_khoan(self, tai_khoan_id: int) -> bool:
        """Xóa tài khoản - check không có dữ liệu liên quan đang active"""
        pass
    
    @abstractmethod
    def khoa_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        """Khóa tài khoản"""
        pass
    
    @abstractmethod
    def mo_khoa_tai_khoan(self, tai_khoan_id: int) -> Dict[str, Any]:
        """Mở khóa tài khoản"""
        pass


class IAdminNguoiDungService(ABC):
    """Service interface cho quản lý người dùng (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_nhan_vien(self, page: int, per_page: int, vai_tro: str = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def tao_nhan_vien(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo nhân viên mới với tài khoản theo vai trò"""
        pass
    
    @abstractmethod
    def cap_nhat_nhan_vien(self, nguoi_dung_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật thông tin nhân viên"""
        pass
    
    @abstractmethod
    def xoa_nhan_vien(self, nguoi_dung_id: int) -> bool:
        """Xóa nhân viên - check không có phân công đang active"""
        pass


class IAdminKhuVucService(ABC):
    """Service interface cho quản lý khu vực (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_khuvuc(self) -> List[Dict[str, Any]]:
        """Lấy danh sách khu vực với số bàn, số nhân viên"""
        pass
    
    @abstractmethod
    def tao_khuvuc(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo khu vực - validate tên không trùng"""
        pass
    
    @abstractmethod
    def cap_nhat_khuvuc(self, khu_vuc_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def xoa_khuvuc(self, khu_vuc_id: int) -> bool:
        """Xóa khu vực - check không có bàn/nhân viên"""
        pass


class IAdminBanService(ABC):
    """Service interface cho quản lý bàn (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_ban(self, khu_vuc_id: int = None, trang_thai: str = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def tao_ban(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo bàn - validate khu_vuc tồn tại"""
        pass
    
    @abstractmethod
    def cap_nhat_ban(self, ban_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật bàn - không cho đổi khu vực nếu đang có khách"""
        pass
    
    @abstractmethod
    def xoa_ban(self, ban_id: int) -> bool:
        """Xóa bàn - check không có phiên đang mở"""
        pass
    
    @abstractmethod
    def reset_trang_thai_ban(self, ban_id: int) -> Dict[str, Any]:
        """Force reset bàn về trạng thái TRONG"""
        pass


class IAdminThucDonService(ABC):
    """Service interface cho quản lý thực đơn (Admin)"""
    
    @abstractmethod
    def lay_thuc_don_chi_tiet(self) -> Dict[str, Any]:
        """Lấy thực đơn với tất cả nhóm món và món"""
        pass
    
    @abstractmethod
    def tao_nhom_mon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo nhóm món - validate tên không trùng"""
        pass
    
    @abstractmethod
    def cap_nhat_nhom_mon(self, nhom_mon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def xoa_nhom_mon(self, nhom_mon_id: int) -> bool:
        """Xóa nhóm món - check không có món trong nhóm"""
        pass
    
    @abstractmethod
    def tao_mon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo món mới - validate nhóm tồn tại, tên không trùng"""
        pass
    
    @abstractmethod
    def cap_nhat_mon(self, mon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def xoa_mon(self, mon_id: int) -> bool:
        """Soft delete món (đổi trạng thái KHONGBAN)"""
        pass
    
    @abstractmethod
    def cap_nhat_trang_thai_mon(self, mon_id: int, trang_thai: str) -> Dict[str, Any]:
        """Toggle trạng thái MOBAN/KHONGBAN"""
        pass


class IAdminKhuyenMaiService(ABC):
    """Service interface cho quản lý khuyến mãi (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_khuyen_mai(self, hoat_dong: bool = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def tao_khuyen_mai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo khuyến mãi - validate ngày, giá trị"""
        pass
    
    @abstractmethod
    def cap_nhat_khuyen_mai(self, khuyen_mai_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cập nhật khuyến mãi - không cho sửa nếu đã có doanhthu áp dụng"""
        pass
    
    @abstractmethod
    def xoa_khuyen_mai(self, khuyen_mai_id: int) -> bool:
        """Soft delete khuyến mãi"""
        pass
    
    @abstractmethod
    def kich_hoat_khuyen_mai(self, khuyen_mai_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def vo_hieu_hoa_khuyen_mai(self, khuyen_mai_id: int) -> Dict[str, Any]:
        pass


class IAdminCauHinhThueService(ABC):
    """Service interface cho quản lý cấu hình thuế (Admin)"""
    
    @abstractmethod
    def lay_danh_sach_cau_hinh_thue(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def lay_cau_hinh_thue_hien_tai(self) -> Dict[str, Any]:
        """Lấy cấu hình đang hoạt động"""
        pass
    
    @abstractmethod
    def tao_cau_hinh_thue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo cấu hình thuế - validate tỷ lệ 0-1"""
        pass
    
    @abstractmethod
    def cap_nhat_cau_hinh_thue(self, cau_hinh_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def kich_hoat_cau_hinh_thue(self, cau_hinh_id: int) -> Dict[str, Any]:
        """Kích hoạt cấu hình - chỉ có 1 cấu hình hoạt động"""
        pass
