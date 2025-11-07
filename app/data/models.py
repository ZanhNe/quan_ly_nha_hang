import datetime

from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Enum
from enum import Enum as RoleEnum




class VaiTro(db.Model):
    __tablename__ = 'vai_tro'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String(50), nullable=False, unique=True)


class TaiKhoan(db.Model):
    __tablename__= 'tai_khoan'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    tai_khoan: Mapped[str] = mapped_column('account_name', String(500), unique=True, nullable=False)
    mat_khau: Mapped[str] = mapped_column('password', String(1500), nullable=False)

class NguoiDung(db.Model):
    __tablename__ = 'nguoi_dung'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ho_ten: Mapped[str] = mapped_column(String(255), nullable=False)
    #Dùng cột type để phân biệt PhucVu và LeTan
    type: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }


class PhucVu(NguoiDung):
    __tablename__ = 'phuc_vu'
    soBanDangPhucVu: Mapped[int] = mapped_column(Integer, default=0)
    __mapper_args__ = {
        "polymorphic_identity": "phuc_vu",
    }

class LeTan(NguoiDung):
    __tablename__ = 'le_tan'
    __mapper_args__ = {
        "polymorphic_identity": "le_tan",
    }

class KhuVuc(db.Model):
    __tablename__ = 'khu_vuc'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ten: Mapped[str] = mapped_column(String(100), nullable=False)


class Ban(db.Model):
    __tablename__ = 'ban'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ten: Mapped[str] = mapped_column(String(100), nullable=False)
    so_ghe: Mapped[int] = mapped_column(Integer, default=0)
    trang_thai: Mapped[str] = mapped_column(String(100), default='Trống')

    #khoá ngoại: *Ban -> 1 KhuVuc
    khu_vuc_id: Mapped[int] = mapped_column(ForeignKey("khu_vuc.id"))

class KhungGio(db.Model):
    __tablename__ = 'khung_gio'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    tg_batdau: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    tg_ketthuc: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column(String(100), default="Chưa có khách")

    # Khóa ngoại: * KhungGio -> 1 Ban
    ban_id: Mapped[int] = mapped_column(ForeignKey("ban.id"))

class PhienBan(db.Model):
    __tablename__ = 'phien_ban'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ngay_tao: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.now)
    trangThai: Mapped[str] = mapped_column(String(100), default="Đang mở")

    # Khóa ngoại: * PhienBan -> 1 LeTan
    le_tan_id: Mapped[int] = mapped_column(ForeignKey("le_tan.id"))

class PhanCong(db.Model):
    __tablename__ = 'phan_cong'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)

    # Khóa ngoại: * PhanCong -> 1 PhucVu
    phuc_vu_id: Mapped[int] = mapped_column(ForeignKey("phuc_vu.id"))

    # Khóa ngoại: * PhanCong -> 1 Ban
    ban_id: Mapped[int] = mapped_column(ForeignKey("ban.id"))

    # Khóa ngoại: * PhanCong -> 1 PhienBan
    phien_ban_id: Mapped[int] = mapped_column(ForeignKey("phien_ban.id"))