import datetime

from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Enum
from typing import Optional, List
from enum import Enum as RoleEnum



class TrangThaiTaiKhoan(Enum):
    MO = 'mo'
    KHOA = 'khoa'

class TrangThaiBan(Enum):
    TRONG = 'trong' #Bàn trống
    COKHACH = 'cokhach' #Có khách
    GIUCHO = 'giucho' #Giữ chỗ

class TrangThai(Enum):
    MO = 'mo' #Mở khi vẫn còn khung giờ cho bàn, tức là vẫn đang có phiên trong bàn
    DONG = 'dong' #Đóng khi khung giờ đã xử lý xong, tức là đã qua khung giờ đấy

class TrangThaiKhungGio(TrangThai):
    pass

class TrangThaiPhien(TrangThai):
    pass

class TenVaiTro(Enum):
    ADMIN = 'admin'
    QUANLY = 'quanly'
    THUNGAN = 'thungan'
    LETAN = 'letan'
    PHUCVU = 'phucvu'




class Base(db.Model):
    """
    Lớp cơ sở trừu tượng chứa các trường chung.
    Sẽ không được tạo thành bảng trong CSDL.
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ngay_tao: Mapped[DateTime] = mapped_column('ngay_tao', DateTime, default=datetime.datetime.now)
    ngay_sua_doi: Mapped[Optional[DateTime]] = mapped_column('ngay_sua_doi', DateTime, nullable=True, onupdate=datetime.datetime.now)


class VaiTro(Base):
    """
    Lớp chứa các vai trò.
    """
    __tablename__ = 'vai_tro'
    vai_tro: Mapped[str] = mapped_column('vai_tro', Enum(TenVaiTro), nullable=False, unique=True)

    def xacThucVaiTro(self, vai_tro: str) -> bool:
        return self.vai_tro == vai_tro


class TaiKhoan(Base):
    """
    Lớp chứa thông tin tài khoản của người dùng.
    """
    __tablename__= 'tai_khoan'
    ten_tai_khoan: Mapped[str] = mapped_column('ten_tai_khoan', String(500), unique=True, nullable=False)
    mat_khau: Mapped[str] = mapped_column('mat_khau', String(1500), nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiTaiKhoan), default=TrangThaiTaiKhoan.MO, nullable=False)

    def xacThucTaiKhoan(self, tk: str, mk: str) -> bool:
        if self.tai_khoan == tk:
            return self.mat_khau == mk
        return False
    


class NguoiDung(Base):
    """
    Lớp chứa về thông tin của người dùng trong hệ thống.
    """
    __tablename__ = 'nguoi_dung'
    ho_ten: Mapped[str] = mapped_column('ho_ten', String(255), nullable=False)
    #Dùng cột type để phân biệt PhucVu và LeTan
    type: Mapped[str] = mapped_column('type', String(50))
    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }


class PhucVu(NguoiDung):
    """
    Lớp chứa thông tin về nhân viên phục vụ (Người dùng) khách hàng trong nhà hàng.
    """
    __tablename__ = 'phuc_vu'
    so_ban_dang_phuc_vu: Mapped[int] = mapped_column('so_ban_dang_phuc_vu', Integer, default=0)
    is_nhom_truong: Mapped[bool] = mapped_column('is_nhom_truong')
    __mapper_args__ = {
        "polymorphic_identity": "phuc_vu",
    }

class LeTan(NguoiDung):
    """
    Lớp chứa thông tin về Lễ Tân (Người dùng cũng là người điều phối khách hàng trong nhà hàng).
    """
    __tablename__ = 'le_tan'
    __mapper_args__ = {
        "polymorphic_identity": "le_tan",
    }

class KhuVuc(Base):
    """
    Lớp chứa thông tin về khu vực mà các phục vụ và bàn được bố trí.
    """
    __tablename__ = 'khu_vuc'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)

    nhom_truong_id: Mapped[int] = mapped_column('nhom_truong_id', ForeignKey('phuc_vu.id'))


class Ban(Base):
    """
    Lớp chứa thông tin về bàn cho việc phục vụ.
    """
    __tablename__ = 'ban'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)
    so_ghe: Mapped[int] = mapped_column('so_ghe', default=0)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiBan), default=TrangThaiBan.TRONG)

    #khoá ngoại: *Ban -> 1 KhuVuc
    khu_vuc_id: Mapped[int] = mapped_column('khu_vuc_id', ForeignKey('khu_vuc.id'))
    #Tí để list khung giờ ở đây (1-N) 1 chiều


    def kiem_tra_ban_trong(self):
        return self.trang_thai == TrangThaiBan.TRONG



class KhungGio(Base):
    """
    Lớp chứa thông tin về khoảng thời gian sử dụng của một bàn được chiếm.
    """
    __tablename__ = 'khung_gio'
    tg_bat_dau: Mapped[datetime.datetime] = mapped_column('tg_bat_dau', DateTime, nullable=False)
    tg_ket_thuc_du_kien: Mapped[datetime.datetime] = mapped_column('tg_ket_thuc_du_kien', DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiKhungGio), default=TrangThaiKhungGio.MO)



class PhienBan(Base):
    """
    Lớp chứa thông tin phiên quản lý bàn cho việc phân công.
    """
    __tablename__ = 'phien_ban'
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiPhien), default=TrangThaiPhien.MO)

    # Khóa ngoại: * PhienBan -> 1 LeTan
    le_tan_id: Mapped[int] = mapped_column('le_tan_id', ForeignKey('le_tan.id'))
    #Tí để khunggio ở đây (1-1) 1 chiều

class PhanCong(Base):
    """
    Lớp chứa thông tin phân công cho phục vụ - bàn - phiên tương ứng.
    VD: Bàn 1 - Phiên 1 - NV2 phục vụ
    """
    __tablename__ = 'phan_cong'


    # Khóa ngoại: * PhanCong -> 1 PhucVu
    phuc_vu_id: Mapped[int] = mapped_column('phuc_vu_id', ForeignKey('phuc_vu.id'))

    # Khóa ngoại: * PhanCong -> 1 Ban
    ban_id: Mapped[int] = mapped_column('ban_id', ForeignKey('ban.id'))

    # Khóa ngoại: * PhanCong -> 1 PhienBan
    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))