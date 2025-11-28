import datetime

from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Table, Enum, and_
from typing import Optional, List
import enum



class BienChung:
    THOIGIANCODINH = 30


class TrangThaiTaiKhoan(str, enum.Enum):
    MO = 'mo'
    KHOA = 'khoa'

class TrangThaiBan(str, enum.Enum):
    TRONG = 'trong' #Bàn trống
    COKHACH = 'cokhach' #Có khách
    GIUCHO = 'giucho' #Giữ chỗ

class TrangThai(str, enum.Enum):
    MO = 'mo' #Mở khi vẫn còn khung giờ cho bàn, tức là vẫn đang có phiên trong bàn
    HOANTHANH = 'hoanthanh' #Hoàn thành khi khung giờ đã xử lý xong, tức là đã qua khung giờ đấy
    HUY = 'huy' #Hủy khi có vấn đề (ví dụ như khung giờ đặt bàn bị hủy)


class TenVaiTro(str, enum.Enum):
    ADMIN = 'admin'
    QUANLY = 'quanly'
    THUNGAN = 'thungan'
    LETAN = 'letan'
    PHUCVU = 'phucvu'
    VODANH = 'vodanh'




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
    email: Mapped[str] = mapped_column('email', String(255), unique=True, nullable=True)
    ten_tai_khoan: Mapped[str] = mapped_column('ten_tai_khoan', String(500), unique=True, nullable=False)
    mat_khau: Mapped[str] = mapped_column('mat_khau', String(255), nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiTaiKhoan), default=TrangThaiTaiKhoan.MO, nullable=False)
    is_xac_thuc: Mapped[bool] = mapped_column('is_xac_thuc', default=False, nullable=False)
    xac_thuc_token: Mapped[Optional[str]] = mapped_column('xac_thuc_token', String(1000), nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column('reset_token', String(1000), nullable=True)
    reset_token_exp: Mapped[Optional[DateTime]] = mapped_column('reset_token_exp', DateTime, nullable=True)
    security_stamp: Mapped[Optional[str]] = mapped_column('security_stamp', String(1000), nullable=True)

    vai_tro_id: Mapped[int] = mapped_column('vai_tro_id', ForeignKey('vai_tro.id'))
    vai_tro: Mapped['VaiTro'] = relationship(lazy='joined', uselist=False)

    nguoi_dung: Mapped['NguoiDung'] = relationship(lazy='joined', uselist=False, back_populates='tai_khoan')
    

    


class NguoiDung(Base):
    """
    Lớp chứa về thông tin của người dùng trong hệ thống.
    """
    __tablename__ = 'nguoi_dung'
    ho_ten: Mapped[str] = mapped_column('ho_ten', String(255), nullable=False)
    #Dùng cột type để phân biệt PhucVu và LeTan
    type: Mapped[str] = mapped_column('type', String(50), nullable=True)

    tai_khoan_id: Mapped[int] = mapped_column('tai_khoan_id', ForeignKey('tai_khoan.id'))
    tai_khoan: Mapped['TaiKhoan'] = relationship(lazy='joined', back_populates='nguoi_dung', uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }


class PhucVu(NguoiDung):
    """
    Lớp chứa thông tin về nhân viên phục vụ (Người dùng) khách hàng trong nhà hàng.
    """
    __tablename__ = 'phuc_vu'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)
    khu_vuc_id: Mapped[int] = mapped_column('khu_vuc_id', ForeignKey('khu_vuc.id'))

    ds_phan_cong_hien_tai: Mapped[List['PhanCong']] = relationship(lazy='selectin',\
        foreign_keys='PhanCong.phuc_vu_id',
        primaryjoin=lambda: and_(
            PhucVu.nguoi_dung_id == PhanCong.phuc_vu_id, PhanCong.trang_thai == TrangThai.MO
        ),\
        back_populates='phuc_vu',\
        order_by='PhanCong.ngay_tao')

    @property
    def so_ban_dang_phuc_vu(self) -> int:
        """
        Trả về số bàn hiện tại đang phục vụ
        """
        return len(self.ds_phan_cong_hien_tai)

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

    def tao_phien(self, tg_bat_dau: datetime.datetime) -> PhienBan:
        phien = PhienBan(le_tan_id=self.id)
        phien.tao_khung_gio(tg_bat_dau=tg_bat_dau)
        return phien

class KhuVuc(Base):
    """
    Lớp chứa thông tin về khu vực mà các phục vụ và bàn được bố trí.
    """
    __tablename__ = 'khu_vuc'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)

    ds_ban: Mapped[List['Ban']] = relationship(lazy='selectin')



ban_khunggio_table = Table(
    'ban_khunggio',
    db.metadata,
    Column('ban_id', Integer, ForeignKey('ban.id'), primary_key=True),
    Column('khung_gio_id', Integer, ForeignKey('khung_gio.id'), primary_key=True)
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
    
    # _all_khung_gio: Mapped[List['KhungGio']] = relationship(
    #     secondary=ban_khunggio_table,
    #     lazy='selectin',
    #     cascade="all, save-update" # Để khi add KhungGio vào Ban thì nó tự lưu
    # )

    ds_khung_gio: Mapped[List['KhungGio']] = relationship(\
        secondary=ban_khunggio_table, lazy='selectin', order_by='asc(KhungGio.tg_bat_dau)',\
        primaryjoin=lambda: (
            Ban.id == ban_khunggio_table.c.ban_id
        ),\
            secondaryjoin=lambda: and_(
            ban_khunggio_table.c.khung_gio_id == KhungGio.id,
            KhungGio.trang_thai == TrangThai.MO
        ))

    def them_khung_gio(self, khung_gio: KhungGio):
        self.ds_khung_gio.append(khung_gio)
        self.danh_dau_khach_an()

    def kiem_tra_thoi_gian_danh_dau(self, tg: datetime.datetime) -> bool:
        """
        Dùng để kiểm tra xem thời gian khách ngồi vào bàn hiện tại có bị chồng chéo lịch so với danh sách thời gian của Bàn.
        """
        for kg in self.ds_khung_gio:
            if kg.kiem_tra_thoi_gian(tg=tg):
                return True
            else: return False

        return True
                

    def kiem_tra_thoi_gian_dat_ban(self, tg: datetime.datetime) -> bool:
        pass

    def kiem_tra_ban_trong(self):
        return self.trang_thai == TrangThaiBan.TRONG

    def danh_dau_khach_an(self):
        self.trang_thai = TrangThaiBan.COKHACH

    def kiem_tra_thuoc_cung_khu_vuc(self, ban: Ban) -> bool:
        return self.khu_vuc_id == ban.khu_vuc_id



class KhungGio(Base):
    """
    Lớp chứa thông tin về khoảng thời gian sử dụng của một bàn được chiếm.
    """
    __tablename__ = 'khung_gio'
    tg_bat_dau: Mapped[datetime.datetime] = mapped_column('tg_bat_dau', DateTime, nullable=False)
    tg_ket_thuc_du_kien: Mapped[datetime.datetime] = mapped_column('tg_ket_thuc_du_kien', DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))

    type: Mapped[str] = mapped_column('type', String(50))

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio",
        "polymorphic_on": type,
    }

    def kiem_tra_thoi_gian(self, tg: datetime.datetime) -> bool:
        raise NotImplementedError('Chưa hiện thực phương thức.')

class KhungGioAn(KhungGio):
    __tablename__ = 'khung_gio_an'

    khung_gio_id: Mapped[int] = mapped_column('khung_gio_id', ForeignKey('khung_gio.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio_an",
    }

    def kiem_tra_thoi_gian(self, tg: datetime.datetime) -> bool:
        pass



class KhungGioDatBan(KhungGio):
    __tablename__ = 'khung_gio_dat_ban'

    khung_gio_id: Mapped[int] = mapped_column('khung_gio_id', ForeignKey('khung_gio.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio_dat_ban",
    }

    def kiem_tra_thoi_gian(self, tg: datetime.datetime) -> bool:
        duration = self.tg_bat_dau - tg
        return duration >= BienChung.THOIGIANCODINH
        
        





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

    ds_phan_cong: Mapped[List['PhanCong']] = relationship(back_populates='phien_ban', lazy='selectin')

    def phan_cong(self, phuc_vu: PhucVu, ban: Ban):
        pc = PhanCong(phuc_vu_id=phuc_vu.id, ban_id=ban.id)
        self.ds_phan_cong.append(pc)

    def tao_khung_gio(self, tg_bat_dau: DateTime) -> None:
        kg = KhungGioAn(tg_bat_dau=tg_bat_dau, tg_ket_thuc_du_kien=tg_bat_dau + datetime.timedelta(minutes=BienChung.THOIGIANCODINH))
        self.khung_gio = kg

class PhanCong(Base):
    """
    Lớp chứa thông tin phân công cho phục vụ - bàn - phiên tương ứng.
    VD: Bàn 1 - Phiên 1 - NV2 phục vụ
    """
    __tablename__ = 'phan_cong'

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)
    dam_nhan_ghi_mon: Mapped[bool] = mapped_column('dam_nhan_ghi_mon', default=False, nullable=False)

    # Khóa ngoại: * PhanCong -> 1 PhucVu
    phuc_vu_id: Mapped[int] = mapped_column('phuc_vu_id', ForeignKey('phuc_vu.nguoi_dung_id'))
    phuc_vu: Mapped['PhucVu'] = relationship(back_populates='ds_phan_cong_hien_tai', lazy='joined')


    # Khóa ngoại: * PhanCong -> 1 Ban
    ban_id: Mapped[int] = mapped_column('ban_id', ForeignKey('ban.id'))

    # Khóa ngoại: * PhanCong -> 1 PhienBan
    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))
    phien_ban: Mapped['PhienBan'] = relationship(back_populates='ds_phan_cong', lazy='joined')