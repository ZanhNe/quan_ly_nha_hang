from typing import List, Optional
from abc import ABC, abstractmethod
from flask_sqlalchemy.session import Session
from app.data.models import (KhuVuc, Ban, NguoiDung, PhucVu, LeTan, ThongBao
                             , PhienBan, TaiKhoan, VaiTro, ThucDon, TuyChonMon, PhieuMon, MonGhi, KhuyenMai, CauHinhThue
                             , DoanhThu, YeuCau)

class IThongBaoReadDAO(ABC):
    @abstractmethod
    def find_by_nguoi_dung_id(self, session: Session, nguoi_dung_id: int, page: int, limit: int) -> List[ThongBao]:
        pass

    @abstractmethod
    def count_unread(self, session: Session, nguoi_dung_id: int) -> int:
        pass

class IKhuVucDAO(ABC):
    @abstractmethod
    def find_all(self, session: Session) -> List[KhuVuc]:
        pass

class IBanDAO(ABC):
    @abstractmethod
    def find_all(self, session: Session) -> List[Ban]:
        pass

    @abstractmethod
    def find_all_by_ids(self, session: Session, ids: list[int]) -> List[Ban]:
        pass

    @abstractmethod
    def save_all(self, session: Session, ds_ban: List[Ban]) -> None:
        pass

class IYeuCauReadDAO(ABC):
    @abstractmethod
    def find_all_by_pending(self, session: Session) -> List[YeuCau]:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, yeu_cau_id: int) -> YeuCau:
        pass

    @abstractmethod
    def save(self, session: Session, yeu_cau: YeuCau) -> None:
        pass

class IPhienBanDAO(ABC):

    @abstractmethod
    def save(self, session: Session, phien: PhienBan) -> None:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, phien_ban_id: int) -> PhienBan:
        pass

    @abstractmethod
    def find_by_mo(self, session: Session) -> List[PhienBan]:
        pass

    @abstractmethod
    def find_by_phucvu_id(self, session: Session, phucvu_id: int) -> List[PhienBan]:
        pass

    @abstractmethod
    def find_by_phieu_mon_id(self, session: Session, phieu_mon_id: int) -> PhienBan:
        pass

    @abstractmethod
    def find_by_mon_ghi_id(self, session: Session, mon_ghi_id: int) -> PhienBan:
        pass



class IPhieuMonReadDAO(ABC):
    @abstractmethod
    def find_by_trang_thai_mo(self, session: Session) -> List[PhieuMon]:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, phieu_mon_id: int) -> PhieuMon:
        pass
    
class IMonGhiReadDAO(ABC):
    @abstractmethod
    def find_by_id(self, session: Session, mon_ghi_id: int) -> MonGhi:
        pass

class ITuyChonMonReadDAO(ABC):
    @abstractmethod
    def find_by_ids(self, session: Session, tuy_chon_mon_ids: List[int]) -> List[TuyChonMon]:
        pass

class IThucDonDAO(ABC):
    @abstractmethod
    def find_first(self, session: Session) -> ThucDon:
        pass
    

class IVaiTroDAO(ABC):

    @abstractmethod
    def find_by_ten_vai_tro(self, session: Session, ten_vai_tro: str) -> VaiTro:
        pass



class ITaiKhoanDAO(ABC):
    @abstractmethod
    def find_by_ten_tai_khoan(self, session: Session, ten_tai_khoan: str) -> TaiKhoan:
        pass

    @abstractmethod
    def find_by_email(self, session: Session, email: str) -> TaiKhoan:
        pass

    @abstractmethod
    def save(self, session: Session, tai_khoan: TaiKhoan) -> None:
        pass

    @abstractmethod
    def find_by_xac_thuc_token(self, session: Session, token: str) -> TaiKhoan:
        pass
    
    @abstractmethod
    def find_by_id(self, session: Session, tai_khoan_id: int) -> Optional[TaiKhoan]:
        pass
    
    @abstractmethod
    def find_cho_xet_duyet(self, session: Session) -> List[TaiKhoan]:
        pass


class INguoiDungDAO(ABC):
    @abstractmethod
    def find_by_id(self, session: Session, id: int) -> Optional[NguoiDung]:
        pass

    @abstractmethod
    def find_by_khuvuc_id(self, session: Session, khuvuc_id: int) -> List[NguoiDung]:
        pass

    @abstractmethod
    def save(self, session: Session, nguoi_dung: NguoiDung):
        pass


class IDoanhThuDAO(ABC):
    @abstractmethod
    def find_by_phien_ban_id(self, session: Session, phien_ban_id: int) -> DoanhThu:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, doanh_thu_id: int) -> DoanhThu:
        pass

    @abstractmethod
    def save(self, session: Session, doanh_thu: DoanhThu):
        pass



class IKhuyenMaiDAO(ABC):
    @abstractmethod
    def find_by_hoat_dong_and_tu_dong_ap_dung(self, session: Session) -> List[KhuyenMai]:
        pass

    @abstractmethod
    def find_by_tuy_chon(self, session: Session) -> List[KhuyenMai]:
        pass

    @abstractmethod
    def find_by_ids(self, session: Session, khuyen_mai_ids: List[int]) -> List[KhuyenMai]:
        pass

class ICauHinhThueDAO(ABC):
    @abstractmethod
    def find_by_hoat_dong(self, session: Session) -> CauHinhThue:
        pass


class IBaoCaoDAO(ABC):
    
    @abstractmethod
    def thong_ke_tong_quan(self, session: Session, tu_ngay, den_ngay) -> dict:
        pass
    
    @abstractmethod
    def thong_ke_theo_ngay(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        pass
    
    @abstractmethod
    def top_mon_ban_chay(self, session: Session, tu_ngay, den_ngay, limit: int) -> List[dict]:
        pass
    
    @abstractmethod
    def hieu_suat_nhan_vien(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        pass
    
    @abstractmethod
    def thong_ke_theo_gio(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        pass

    @abstractmethod
    def thong_ke_theo_nhom_mon(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        pass



