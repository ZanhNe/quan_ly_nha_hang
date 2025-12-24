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
    # @abstractmethod
    # def chon_ban(self):
    #     pass
    
    @abstractmethod
    def get_ban_details(self, ban_schemas_in: List[Dict[str, Any]]) -> List[Ban]:
        pass

    @abstractmethod
    def xu_ly_chon_ban(self, letan_id: int, ban_schemas_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
