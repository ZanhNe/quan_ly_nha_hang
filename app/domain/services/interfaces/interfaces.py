from typing import List, Dict, Any
from app.schemas.schema import KhuVucOutSchema
from app.data.models import Ban, NguoiDung, PhucVu
from abc import ABC, abstractmethod



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
