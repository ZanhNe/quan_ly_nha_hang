from typing import List, Optional
from abc import ABC, abstractmethod
from flask_sqlalchemy.session import Session
from app.data.models import KhuVuc, Ban, NguoiDung, PhucVu, LeTan, PhienBan, TaiKhoan, VaiTro

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

class IPhienBanDAO(ABC):
    @abstractmethod
    def save(self, session: Session, phien: PhienBan) -> None:
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


class INguoiDungDAO(ABC):
    @abstractmethod
    def find_by_id(self, session: Session, id: int) -> Optional[NguoiDung]:
        pass

    @abstractmethod
    def find_by_khuvuc_id(self, session: Session, khuvuc_id: int) -> List[NguoiDung]:
        pass

    

