import datetime

from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Table, Enum
from typing import Optional, List
import enum




class TrangThaiTaiKhoan(str, enum.Enum):
    MO = 'mo'
    KHOA = 'khoa'

class TrangThaiBan(str, enum.Enum):
    TRONG = 'trong' #Bàn trống
    COKHACH = 'cokhach' #Có khách
    GIUCHO = 'giucho' #Giữ chỗ

class TrangThai(str, enum.Enum):
    MO = 'mo' #Mở khi vẫn còn khung giờ cho bàn, tức là vẫn đang có phiên trong bàn
    DONG = 'dong' #Đóng khi khung giờ đã xử lý xong, tức là đã qua khung giờ đấy

class TenVaiTro(str, enum.Enum):
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

    vai_tro_id: Mapped[int] = mapped_column('vai_tro_id', ForeignKey('vai_tro.id'))

    vai_tro: Mapped['VaiTro'] = relationship(lazy='joined')

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

    tai_khoan_id: Mapped[int] = mapped_column('tai_khoan_id', ForeignKey('tai_khoan.id'))
    tai_khoan: Mapped['TaiKhoan'] = relationship(lazy='joined')

    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }


class PhucVu(NguoiDung):
    """
    Lớp chứa thông tin về nhân viên phục vụ (Người dùng) khách hàng trong nhà hàng.
    """
    __tablename__ = 'phuc_vu'
    is_nhom_truong: Mapped[bool] = mapped_column('is_nhom_truong')

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)

    khu_vuc_id: Mapped[int] = mapped_column('khu_vuc_id', ForeignKey('khu_vuc.id'))
    khu_vuc: Mapped['KhuVuc'] = relationship(lazy='joined', foreign_keys=[khu_vuc_id])

    ds_phan_cong_hien_tai: Mapped[List['PhanCong']] = relationship(lazy='selectin')

    @property
    def so_ban_dang_phuc_vu(self) -> int:
        """
        Trả về số bàn hiện tại đang phục vụ
        """
        count = 0
        for pc in self.ds_phan_cong_hien_tai:
            if pc.trang_thai == TrangThai.MO:
                count+=1
        return count

    __mapper_args__ = {
        "polymorphic_identity": "phuc_vu",
    }

class LeTan(NguoiDung):
    """
    Lớp chứa thông tin về Lễ Tân (Người dùng cũng là người điều phối khách hàng trong nhà hàng).
    """
    __tablename__ = 'le_tan'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "le_tan",
    }

    def tao_phien(self, tg_bat_dau: DateTime) -> PhienBan:
        phien = PhienBan(le_tan_id=self.id)
        phien.tao_khung_gio(tg_bat_dau=tg_bat_dau)
        return phien

class KhuVuc(Base):
    """
    Lớp chứa thông tin về khu vực mà các phục vụ và bàn được bố trí.
    """
    __tablename__ = 'khu_vuc'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)

    nhom_truong_id: Mapped[int] = mapped_column('nhom_truong_id', ForeignKey('phuc_vu.nguoi_dung_id', use_alter=True), nullable=True)
    nhom_truong: Mapped['PhucVu'] = relationship(lazy='joined', foreign_keys=[nhom_truong_id])




ban_khunggio_table = Table(
    'ban_khunggio',
    db.metadata,
    Column('ban.id', Integer, ForeignKey('ban.id'), primary_key=True),
    Column('khung_gio.id', Integer, ForeignKey('khung_gio.id'), primary_key=True)
)

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

    ds_khung_gio: Mapped[List['KhungGio']] = relationship(secondary=ban_khunggio_table, lazy='selectin')

    def them_khung_gio(self, khung_gio: KhungGio):
        self.ds_khung_gio.append(khung_gio)

    def kiem_tra_thoi_gian_hop_le(self, tg: DateTime) -> bool:
        """
        Dùng để kiểm tra xem thời gian khách ngồi vào bàn hiện tại có bị chồng chéo lịch so với danh sách thời gian của Bàn.
        """
        pass

    def kiem_tra_ban_trong(self):
        return self.trang_thai == TrangThaiBan.TRONG



class KhungGio(Base):
    """
    Lớp chứa thông tin về khoảng thời gian sử dụng của một bàn được chiếm.
    """
    __tablename__ = 'khung_gio'
    tg_bat_dau: Mapped[datetime.datetime] = mapped_column('tg_bat_dau', DateTime, nullable=False)
    tg_ket_thuc_du_kien: Mapped[datetime.datetime] = mapped_column('tg_ket_thuc_du_kien', DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))




class PhienBan(Base):
    """
    Lớp chứa thông tin phiên quản lý bàn cho việc phân công.
    """
    __tablename__ = 'phien_ban'
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    # Khóa ngoại: * PhienBan -> 1 LeTan
    le_tan_id: Mapped[int] = mapped_column('le_tan_id', ForeignKey('le_tan.nguoi_dung_id'))
    le_tan: Mapped['LeTan'] = relationship(lazy='joined')

    khung_gio: Mapped['KhungGio'] = relationship(lazy='joined')

    ds_phan_cong: Mapped[List['PhanCong']] = relationship(lazy='selectin')

    def phan_cong(self, phuc_vu: PhucVu, ban: Ban):
        pc = PhanCong(phuc_vu_id=phuc_vu.id, ban_id=ban.id)
        self.ds_phan_cong.append(pc)

    def tao_khung_gio(self, tg_bat_dau: DateTime) -> None:
        kg = KhungGio(tg_bat_dau=tg_bat_dau, tg_ket_thuc_du_kien=tg_bat_dau + datetime.timedelta(minutes=30))
        self.khung_gio = kg

class PhanCong(Base):
    """
    Lớp chứa thông tin phân công cho phục vụ - bàn - phiên tương ứng.
    VD: Bàn 1 - Phiên 1 - NV2 phục vụ
    """
    __tablename__ = 'phan_cong'

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    # Khóa ngoại: * PhanCong -> 1 PhucVu
    phuc_vu_id: Mapped[int] = mapped_column('phuc_vu_id', ForeignKey('phuc_vu.nguoi_dung_id'))

    # Khóa ngoại: * PhanCong -> 1 Ban
    ban_id: Mapped[int] = mapped_column('ban_id', ForeignKey('ban.id'))

    # Khóa ngoại: * PhanCong -> 1 PhienBan
    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))