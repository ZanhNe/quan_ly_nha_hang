from sqlalchemy import select
from typing import List, Optional
from flask_sqlalchemy.session import Session
from app.data.models import KhuVuc, Ban, NguoiDung, PhucVu, PhienBan, TaiKhoan, VaiTro
from app.data.dao.interfaces.interfaces import (IBanDAO, IKhuVucDAO, INguoiDungDAO, IPhienBanDAO, ITaiKhoanDAO, IVaiTroDAO)


class KhuVucDAO(IKhuVucDAO):
    
    def find_all(self, session: Session) -> List[KhuVuc]:
        stmt = select(KhuVuc).order_by(KhuVuc.id)
        ds_khuvuc = session.execute(statement=stmt).scalars().all()

        return ds_khuvuc

class BanDAO(IBanDAO):

    def find_all(self, session: Session) -> List[Ban]:
        stmt = select(Ban).order_by(Ban.id)
        ds_ban = session.execute(statement=stmt).scalars().all()
        
        return ds_ban
    
    def find_all_by_ids(self, session: Session, ids: list[int]) -> List[Ban]:
        stmt = select(Ban).where(Ban.id.in_(ids))
        ds_ban = session.execute(statement=stmt).scalars().all()

        return ds_ban
    
    def save_all(self, session: Session, ds_ban: List[Ban]) -> None:
        session.add_all(ds_ban)
        session.flush()
        

    
class PhienBanDAO(IPhienBanDAO):

    def save(self, session: Session, phien: PhienBan) -> None:
        session.add(phien)
        session.flush()


class VaiTroDAO(IVaiTroDAO):

    def find_by_ten_vai_tro(self, session: Session, ten_vai_tro: str) -> VaiTro:
        stmt = select(VaiTro).where(VaiTro.vai_tro == ten_vai_tro)
        vai_tro = session.execute(statement=stmt).scalar()
        return vai_tro

class TaiKhoanDAO(ITaiKhoanDAO):

    def find_by_ten_tai_khoan(self, session: Session, ten_tai_khoan: str) -> TaiKhoan:
        stmt = select(TaiKhoan).where(TaiKhoan.ten_tai_khoan == ten_tai_khoan)
        
        tai_khoan = session.execute(statement=stmt).scalar()
        return tai_khoan
    
    def find_by_email(self, session: Session, email: str) -> TaiKhoan:
        stmt = select(TaiKhoan).where(TaiKhoan.email == email)

        tai_khoan = session.execute(statement=stmt).scalar()
        return tai_khoan
    
    def save(self, session: Session, tai_khoan: TaiKhoan) -> None:
        session.add(tai_khoan)
        session.flush()

    def find_by_xac_thuc_token(self, session: Session, token: str) -> TaiKhoan:
        stmt = select(TaiKhoan).where(TaiKhoan.xac_thuc_token == token)
        tai_khoan = session.execute(statement=stmt).scalar()

        return tai_khoan

    

        

class NguoiDungDAO(INguoiDungDAO):

    def find_by_id(self, session: Session, id: int) -> Optional[NguoiDung]:
        nguoi_dung = session.get(NguoiDung, id)
        return nguoi_dung
    
    def find_by_khuvuc_id(self, session: Session, khuvuc_id: int) -> List[NguoiDung]:
        stmt = select(NguoiDung).join(PhucVu).where(PhucVu.khu_vuc_id == khuvuc_id)
        ds_phuc_vu = session.scalars(statement=stmt).all()
        return ds_phuc_vu