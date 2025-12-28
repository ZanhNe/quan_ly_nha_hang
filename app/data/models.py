import datetime

from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Table, Enum, and_
from typing import Optional, List
from functools import singledispatchmethod
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

class TrangThaiPhieu(enum.Enum):
    DANGGHI = 'dangghi'
    DAGUI = 'dagui'
    HOANTHANH = 'hoanthanh'
    HUY = 'huy'
    DONG = 'dong'

class TrangThaiMonGhi(enum.Enum):
    CHUANAU = 'chuanau'
    HOANTHANH = 'hoanthanh'
    HUY = 'huy'
    HAOTON = 'haoton'
    TAMNGUNG = 'tamngung'

class TrangThaiMon(enum.Enum):
    MOBAN = 'moban'
    KHONGBAN = 'khongban'

class LoaiNhomTuyChon(enum.Enum):
    SINGLE = 'single'
    MULTI = 'multi'


class TenVaiTro(str, enum.Enum):
    ADMIN = 'admin'
    QUANLY = 'quanly'
    DAUBEP = 'daubep'
    THUNGAN = 'thungan'
    LETAN = 'letan'
    PHUCVU = 'phucvu'
    VODANH = 'vodanh'

class PhanLoaiThongBao(enum.Enum):
    HOANTHANHPHIEU = 'hoanthanhphieu'
    PHANCONG = 'phancong'
    DAGUIPHIEU = 'daguiphieu'


class HoanThanhMon:
    pass

class HuyMon:
    pass

class HaoTon:
    pass


class Base(db.Model):
# Base model chứa mấy trường chung like ID, ngày tạo...
    __abstract__ = True

    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    ngay_tao: Mapped[DateTime] = mapped_column('ngay_tao', DateTime, default=datetime.datetime.now)
    ngay_sua_doi: Mapped[Optional[DateTime]] = mapped_column('ngay_sua_doi', DateTime, nullable=True, onupdate=datetime.datetime.now)


class VaiTro(Base):
    # Bảng phân quyền (Admin, Quản lý, Phục vụ...)
    __tablename__ = 'vai_tro'
    vai_tro: Mapped[str] = mapped_column('vai_tro', Enum(TenVaiTro), nullable=False, unique=True)

    def xacThucVaiTro(self, vai_tro: str) -> bool:
        return self.vai_tro == vai_tro
    
    def __repr__(self):
        return self.vai_tro.value if hasattr(self.vai_tro, 'value') else str(self.vai_tro)


class TaiKhoan(Base):
    # Thông tin đăng nhập, token xác thực/reset pass
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
    
    def khoa(self):
        self.trang_thai = TrangThaiTaiKhoan.KHOA

    def mo_khoa(self):
        self.trang_thai = TrangThaiTaiKhoan.MO

    def cap_nhat_thong_tin(self, email: str = None, mat_khau: str = None, is_xac_thuc: bool = None):
        if email:
            self.email = email
        if mat_khau:
            self.mat_khau = mat_khau
        if is_xac_thuc is not None:
            self.is_xac_thuc = is_xac_thuc

    def kien_tra_cho_duyet(self):
        if not self.is_xac_thuc:
            raise Exception('Tài khoản chưa xác thực email.')
        if self.vai_tro.vai_tro != TenVaiTro.VODANH:
            raise Exception('Tài khoản này đã được duyệt hoặc không ở trạng thái chờ duyệt.')
    
    def __repr__(self):
        email_str = f" ({self.email})" if self.email else ""
        return f"{self.ten_tai_khoan}{email_str}"


class NguoiDung(Base):
    # Thông tin cá nhân nhân viên, có link tới tài khoản
    __tablename__ = 'nguoi_dung'
    ho_ten: Mapped[str] = mapped_column('ho_ten', String(255), nullable=False)
    #Dùng cột type để phân biệt PhucVu và LeTan
    type: Mapped[str] = mapped_column('type', String(50), nullable=True)

    tai_khoan_id: Mapped[int] = mapped_column('tai_khoan_id', ForeignKey('tai_khoan.id'))
    tai_khoan: Mapped['TaiKhoan'] = relationship(lazy='joined', back_populates='nguoi_dung', uselist=False)

    ds_thong_bao: Mapped[List['ThongBao']] = relationship(lazy='selectin', order_by='desc(ThongBao.ngay_tao)')

    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }
    
    def __repr__(self):
        return self.ho_ten

    def cap_nhat_ho_ten(self, ho_ten: str):
        self.ho_ten = ho_ten

    @classmethod
    def create_by_role(cls, vai_tro_ten: str, ho_ten: str, tai_khoan_id: int, **kwargs) -> 'NguoiDung':
        if vai_tro_ten == 'PHUCVU':
            return PhucVu(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id, khu_vuc_id=kwargs.get('khu_vuc_id'))
        elif vai_tro_ten == 'LETAN':
            return LeTan(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'DAUBEP':
            return DauBep(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'THUNGAN':
            return ThuNgan(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'QUANLY':
            return QuanLy(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        else:
            return NguoiDung(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)

    @singledispatchmethod
    def them_thong_bao(self, status, tieu_de, noi_dung, link):
        raise NotImplementedError('')
    
    @them_thong_bao.register(HoanThanhMon)
    def _(self, status: HoanThanhMon, tieu_de, noi_dung, link):
        tb = ThongBao(tieu_de=tieu_de, noi_dung=noi_dung, phan_loai=PhanLoaiThongBao.HOANTHANHPHIEU, nguoi_nhan_id=self.id, link=link)
        self.ds_thong_bao.append(tb)
        return tb
    




class PhucVu(NguoiDung):
    # Subclass cho nhân viên chạy bàn
    __tablename__ = 'phuc_vu'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)
    khu_vuc_id: Mapped[int] = mapped_column('khu_vuc_id', ForeignKey('khu_vuc.id'))
    
    # Relationship với KhuVuc
    khu_vuc: Mapped['KhuVuc'] = relationship(lazy='joined', back_populates='ds_phuc_vu')

    ds_phan_cong_hien_tai: Mapped[List['PhanCong']] = relationship(lazy='selectin',\
        foreign_keys='PhanCong.phuc_vu_id',
        primaryjoin=lambda: and_(
            PhucVu.nguoi_dung_id == PhanCong.phuc_vu_id, PhanCong.trang_thai == TrangThai.MO
        ),\
        back_populates='phuc_vu',\
        order_by='PhanCong.ngay_tao')

    ds_phien_dam_nhan_dang_co: Mapped[List['PhienBan']] = relationship(back_populates='nguoi_dam_nhan', lazy='selectin',
        primaryjoin='and_(PhienBan.nguoi_dam_nhan_id == PhucVu.nguoi_dung_id, PhienBan.trang_thai == "MO")',
        foreign_keys='PhienBan.nguoi_dam_nhan_id'
        )

    @property
    def so_ban_dang_phuc_vu(self) -> int:
        """
        Trả về số bàn hiện tại đang phục vụ
        """
        return len(self.ds_phan_cong_hien_tai)
    
    def kiem_tra_chua_dam_nhan_phien_nao(self) -> bool:
        for phien in self.ds_phien_dam_nhan_dang_co:
            if phien.trang_thai == TrangThai.MO:
                print(phien)
        return len(self.ds_phien_dam_nhan_dang_co) == 0

    __mapper_args__ = {
        "polymorphic_identity": "phuc_vu",
    }
    
    def __repr__(self):
        return self.ho_ten


class LeTan(NguoiDung):
    # Phụ trách check-in, gán bàn, đặt chỗ
    __tablename__ = 'le_tan'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "le_tan",
    }
    
    def __repr__(self):
        return self.ho_ten

    def tao_phien(self, tg_bat_dau: datetime.datetime) -> PhienBan:
        phien = PhienBan(le_tan_id=self.id)
        phien.tao_khung_gio(tg_bat_dau=tg_bat_dau)
        return phien
    
    def dat_ban(self, tg_den: datetime.datetime, ten_khach: str, sdt: str, so_luong: int, ds_ban: List[Ban]) -> DatBan:
        db = DatBan(ten_khach=ten_khach, sdt=sdt, so_luong=so_luong, ds_ban_dat=ds_ban, le_tan=self)
        db.tao_khung_gio_dat_ban(tg_den=tg_den, ds_ban=ds_ban)
        return db


class DauBep(NguoiDung):
    """
    Lớp chứa thông tin về Đầu bếp
    """
    __tablename__ = 'dau_bep'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "dau_bep",
    }
    
    def __repr__(self):
        return self.ho_ten


class ThuNgan(NguoiDung):
    # Nhân viên thu ngân, xử lý hóa đơn
    __tablename__ = 'thu_ngan'

    ds_doanh_thu_chua_hoan_thanh: Mapped[List['DoanhThu']] = relationship(lazy='selectin'\
                            , primaryjoin='and_(DoanhThu.thu_ngan_id == ThuNgan.nguoi_dung_id, DoanhThu.trang_thai == "CHUAHOANTHANH")')
    
    # Relationship với tất cả DoanhThu (không chỉ chưa hoàn thành)
    ds_doanh_thu: Mapped[List['DoanhThu']] = relationship(
        lazy='selectin', 
        foreign_keys='DoanhThu.thu_ngan_id', 
        back_populates='thu_ngan',
        overlaps='ds_doanh_thu_chua_hoan_thanh'  # Thêm để tránh warning
    )

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "thu_ngan",
    }
    
    def __repr__(self):
        return self.ho_ten
    
    def tao_doanh_thu(self, phien_ban_id: int) -> DoanhThu:
        dt = DoanhThu(phien_ban_id=phien_ban_id)
        self.ds_doanh_thu_chua_hoan_thanh.append(dt)
        return dt

    def lay_doanh_thu_ton_tai(self, phien_ban_id: int) -> DoanhThu:
        for dt in self.ds_doanh_thu_chua_hoan_thanh:
            if dt.phien_ban_id == phien_ban_id:
                return dt
        return None

    
class QuanLy(NguoiDung):
    # Cấp quản lý, có quyền duyệt yêu cầu từ nhân viên
    __tablename__ = 'quan_ly'

    nguoi_dung_id: Mapped[int] = mapped_column('nguoi_dung_id', ForeignKey('nguoi_dung.id'), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "quan_ly",
    }
    
    def __repr__(self):
        return self.ho_ten


class TrangThaiYeuCau(enum.Enum):
    CHODUYET = 'choduyet'
    CHAPTHUAN = 'chapthuan'
    TUCHOI = 'tuchoi'

class YeuCau(Base):
    """
    Lớp chứa thông tin về yêu cầu duyệt
    """
    __tablename__ = 'yeu_cau'

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiYeuCau), default=TrangThaiYeuCau.CHODUYET, nullable=False)
    ly_do: Mapped[str] = mapped_column('ly_do', String(500), nullable=False)
    type: Mapped[str] = mapped_column('type', String(50), nullable=True)
    quan_ly_duyet_id: Mapped[Optional[int]] = mapped_column('quan_ly_duyet_id', ForeignKey('quan_ly.nguoi_dung_id'), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "nguoi_dung",
        "polymorphic_on": type,
    }
    
    def __repr__(self):
        return f"YC #{self.id}: {self.ly_do[:30]}..." if len(self.ly_do) > 30 else f"YC #{self.id}: {self.ly_do}"

    def chap_thuan(self, quan_ly_duyet_id: int):
        raise NotImplementedError("")
    
    def tu_choi(self, quan_ly_duyet_id: int):
        raise NotImplementedError("")
    



class YCMonGhi(YeuCau):
    """
    Lớp chứa thông tin về yêu cầu duyệt riêng cho món ghi
    """
    __tablename__ = 'yc_mon_ghi'
    yc_id: Mapped[int] = mapped_column('yc_id', ForeignKey('yeu_cau.id'), primary_key=True)

    trang_thai_truoc: Mapped[str] = mapped_column('trang_thai_truoc', Enum(TrangThaiMonGhi), nullable=False)

    mon_ghi_id: Mapped[int] = mapped_column('mon_ghi_id', ForeignKey('mon_ghi.id'))
    mon_ghi: Mapped['MonGhi'] = relationship(lazy='joined', back_populates='ds_yeu_cau')

    __mapper_args__ = {
        "polymorphic_identity": "yc_mon_ghi",
    }
    
    def __repr__(self):
        mon_ten = self.mon_ghi.mo_ta_mon.ten if self.mon_ghi and self.mon_ghi.mo_ta_mon else 'N/A'
        return f"YC Món ghi #{self.yc_id}: {mon_ten}"

    def chap_thuan(self, quan_ly_duyet_id: int):
        if self.trang_thai_truoc == TrangThaiMonGhi.CHUANAU:
            self.mon_ghi.huy_mon()
        elif self.trang_thai_truoc == TrangThaiMonGhi.HOANTHANH:
            self.mon_ghi.hao_ton()
        self.trang_thai = TrangThaiYeuCau.CHAPTHUAN
        self.quan_ly_duyet_id = quan_ly_duyet_id

    def tu_choi(self, quan_ly_duyet_id: int):
        if self.trang_thai_truoc == TrangThaiMonGhi.CHUANAU:
            self.mon_ghi.chua_nau()
        elif self.trang_thai_truoc == TrangThaiMonGhi.HOANTHANH:
            self.mon_ghi.hoan_thanh()

        self.trang_thai = TrangThaiYeuCau.TUCHOI
        self.quan_ly_duyet_id = quan_ly_duyet_id
        

class YCPhieuMon(YeuCau):
    """
    Lớp chứa thông tin về yêu cầu duyệt riêng cho Phiếu Món
    """
    __tablename__ = 'yc_phieu_mon'
    yc_id: Mapped[int] = mapped_column('yc_id', ForeignKey('yeu_cau.id'), primary_key=True)

    phieu_mon_id: Mapped[int] = mapped_column('mon_ghi_id', ForeignKey('mon_ghi.id'))

    __mapper_args__ = {
        "polymorphic_identity": "yc_phieu_mon",
    }
    
    def __repr__(self):
        return f"YC Phiếu món #{self.yc_id}"



class ThongBao(Base):
    # Thông báo nội bộ cho nhân viên (Hoàn thành món, Phân công ca...)
    __tablename__ = 'thong_bao'
    nguoi_nhan_id: Mapped[int] = mapped_column('nguoi_nhan_id', ForeignKey('nguoi_dung.id'), nullable=False)
    tieu_de: Mapped[str] = mapped_column('tieu_de', String(100), nullable=True)
    noi_dung: Mapped[str] = mapped_column('noi_dung', String(500), nullable=False)

    da_doc: Mapped[bool] = mapped_column('da_doc', default=False, index=True)
    phan_loai: Mapped[str] = mapped_column('phan_loai', Enum(PhanLoaiThongBao), nullable=False)
    link: Mapped[str] = mapped_column('link', String(255), nullable=True)




class KhuVuc(Base):
    # Khu vực like Tầng 1, Tầng 2, Ngoài trời...
    __tablename__ = 'khu_vuc'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)

    ds_ban: Mapped[List['Ban']] = relationship(lazy='selectin', back_populates='khu_vuc')
    ds_phuc_vu: Mapped[List['PhucVu']] = relationship(lazy='selectin', back_populates='khu_vuc')
    
    def __repr__(self):
        return self.ten

    def cap_nhat_ten(self, ten: str):
        self.ten = ten


ban_khunggio_table = Table(
    'ban_khunggio',
    db.metadata,
    Column('ban_id', Integer, ForeignKey('ban.id'), primary_key=True),
    Column('khung_gio_id', Integer, ForeignKey('khung_gio.id'), primary_key=True)
)


ban_datban_table = Table(
    'ban_datban',
    db.metadata,
    Column('ban_id', Integer, ForeignKey('ban.id'), primary_key=True),
    Column('dat_ban_id', Integer, ForeignKey('dat_ban.id'), primary_key=True)
)

class Ban(Base):
    # Thông tin từng bàn ăn cụ thể
    __tablename__ = 'ban'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)
    so_ghe: Mapped[int] = mapped_column('so_ghe', default=0)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiBan), default=TrangThaiBan.TRONG)

    #khoá ngoại: *Ban -> 1 KhuVuc
    khu_vuc_id: Mapped[int] = mapped_column('khu_vuc_id', ForeignKey('khu_vuc.id'))
    
    # Relationship với KhuVuc
    khu_vuc: Mapped['KhuVuc'] = relationship(lazy='joined', back_populates='ds_ban')
    
    # Relationship với PhanCong
    ds_phan_cong: Mapped[List['PhanCong']] = relationship(lazy='selectin', back_populates='ban')
    

    def hoan_thanh(self) -> None:
        self.trang_thai = TrangThaiBan.TRONG
        

    ds_khung_gio: Mapped[List['KhungGio']] = relationship(\
        secondary=ban_khunggio_table, lazy='selectin', order_by='asc(KhungGio.tg_bat_dau)',\
        primaryjoin=lambda: (
            Ban.id == ban_khunggio_table.c.ban_id
        ),\
            secondaryjoin=lambda: and_(
            ban_khunggio_table.c.khung_gio_id == KhungGio.id,
            KhungGio.trang_thai == TrangThai.MO
        ), back_populates='ds_ban')

    def them_khung_gio(self, khung_gio: KhungGio):
        self.ds_khung_gio.append(khung_gio)
        self.danh_dau_khach_an()

    def kiem_tra_thoi_gian_danh_dau(self, tg: datetime.datetime) -> bool:
        """
        # Kiểm tra xem giờ khách vào có bị đè lên lịch đặt trước không
        """
        for kg in self.ds_khung_gio:
            if not kg.thoi_gian_hop_le(tg=tg):
                return False
            
        return True

    def kiem_tra_ban_trong(self):
        return self.trang_thai == TrangThaiBan.TRONG

    def danh_dau_khach_an(self):
        self.trang_thai = TrangThaiBan.COKHACH

    def kiem_tra_thuoc_cung_khu_vuc(self, ban: Ban) -> bool:
        return self.khu_vuc_id == ban.khu_vuc_id
    
    def __repr__(self):
        khu_vuc_ten = self.khu_vuc.ten if self.khu_vuc else 'N/A'
        return f"{self.ten} (Khu: {khu_vuc_ten})"

    def cap_nhat_thong_tin(self, ten: str = None, so_ghe: int = None, khu_vuc_id: int = None):
        if ten:
            self.ten = ten
        if so_ghe is not None:
            self.so_ghe = so_ghe
        if khu_vuc_id:
            self.khu_vuc_id = khu_vuc_id


class DatBan(Base):
    __tablename__ = 'dat_ban'

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO, nullable=False)
    ten_khach: Mapped[str] = mapped_column('ten_khach', String(500), nullable=False)
    sdt: Mapped[str] = mapped_column('sdt', String(11), nullable=False)
    so_luong: Mapped[int] = mapped_column('so_luong', nullable=False)

    khung_gio_id: Mapped[int] = mapped_column('khung_gio_id', ForeignKey('khung_gio.id'))
    khung_gio: Mapped['KhungGio'] = relationship(lazy='joined')

    ds_ban_dat: Mapped[List['Ban']] = relationship(secondary=ban_datban_table, lazy='selectin')

    le_tan_id: Mapped[int] = mapped_column('le_tan_id', ForeignKey('le_tan.nguoi_dung_id'))
    le_tan: Mapped['LeTan'] = relationship(lazy='joined')

    def tao_khung_gio_dat_ban(self, tg_den: datetime.datetime, ds_ban: List[Ban]):
        kg_db = KhungGioDatBan(tg_bat_dau=tg_den, tg_ket_thuc_du_kien=(tg_den + datetime.timedelta(minutes=BienChung.THOIGIANCODINH)), ds_ban=ds_ban)
        self.khung_gio = kg_db


class KhungGio(Base):
    """
    Lớp chứa thông tin về khoảng thời gian sử dụng của một bàn được chiếm.
    """
    __tablename__ = 'khung_gio'
    tg_bat_dau: Mapped[datetime.datetime] = mapped_column('tg_bat_dau', DateTime, nullable=False)
    tg_ket_thuc_du_kien: Mapped[datetime.datetime] = mapped_column('tg_ket_thuc_du_kien', DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'), nullable=True)

    type: Mapped[str] = mapped_column('type', String(50))

    ds_ban: Mapped[List['Ban']] = relationship(secondary=ban_khunggio_table, lazy='selectin', back_populates='ds_khung_gio')

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio",
        "polymorphic_on": type,
    }
    def hoan_thanh(self) -> None:
        self.trang_thai = TrangThai.HOANTHANH

    def thoi_gian_hop_le(self, tg: datetime.datetime) -> bool:
        tg_ket_thuc_du_kien_khach_moi = tg + datetime.timedelta(minutes=BienChung.THOIGIANCODINH)
        flag = tg < self.tg_ket_thuc_du_kien and tg_ket_thuc_du_kien_khach_moi > self.tg_bat_dau
        return not flag
    
    def __repr__(self):
        if self.tg_bat_dau and self.tg_ket_thuc_du_kien:
            return f"{self.tg_bat_dau.strftime('%H:%M')} - {self.tg_ket_thuc_du_kien.strftime('%H:%M')}"
        return f"Khung giờ #{self.id}"

class KhungGioAn(KhungGio):
    __tablename__ = 'khung_gio_an'

    khung_gio_id: Mapped[int] = mapped_column('khung_gio_id', ForeignKey('khung_gio.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio_an",
    }




class KhungGioDatBan(KhungGio):
    __tablename__ = 'khung_gio_dat_ban'

    khung_gio_id: Mapped[int] = mapped_column('khung_gio_id', ForeignKey('khung_gio.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khung_gio_dat_ban",
    }
        
        





class PhienBan(Base):
    # Một phiên (Session) của bàn, từ lúc khách vào đến lúc tính tiền
    __tablename__ = 'phien_ban'
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)

    # Khóa ngoại: * PhienBan -> 1 LeTan
    le_tan_id: Mapped[int] = mapped_column('le_tan_id', ForeignKey('le_tan.nguoi_dung_id'))
    le_tan: Mapped['LeTan'] = relationship(lazy='joined')

    nguoi_dam_nhan_id: Mapped[int] = mapped_column('nguoi_dam_nhan_id', ForeignKey('phuc_vu.nguoi_dung_id'), nullable=True)
    nguoi_dam_nhan: Mapped[Optional['PhucVu']] = relationship(lazy='joined', back_populates='ds_phien_dam_nhan_dang_co')

    khung_gio: Mapped['KhungGio'] = relationship(lazy='joined')

    ds_phan_cong: Mapped[List['PhanCong']] = relationship(back_populates='phien_ban', lazy='selectin')
    ds_phieu_mon: Mapped[List['PhieuMon']] = relationship(lazy='selectin', order_by='PhieuMon.id', back_populates='phien_ban')
    doanh_thu: Mapped[Optional['DoanhThu']] = relationship(lazy='joined', back_populates='phien_ban')

    def tao_doanh_thu(self) -> None:
        dt = DoanhThu()
        self.doanh_thu = dt
    
    def is_doanh_thu(self) -> bool:
        return self.doanh_thu != None

    def khong_co_phieu_mon_dang_nau(self) -> bool:
        for pm in self.ds_phieu_mon:
            if not pm.is_hoan_thanh():
                return False
        
        return True
    
    def chua_ton_tai_doanh_thu(self) -> bool:
        if not self.doanh_thu:
            return True
        return False

    def hoan_thanh(self) -> None:
        self.trang_thai = TrangThai.HOANTHANH
        self.khung_gio.hoan_thanh()

        for pc in self.ds_phan_cong:
            pc.hoan_thanh()
        
        

    def tinh_tong_tien(self) -> int:
        tong_tien = 0
        for phieu in self.ds_phieu_mon:
            tong_tien += phieu.tinh_tien()
        
        return tong_tien

    def phan_cong(self, phuc_vu: PhucVu, ban: Ban):
        pc = PhanCong(phuc_vu_id=phuc_vu.id, ban_id=ban.id)
        self.ds_phan_cong.append(pc)
        phuc_vu.ds_phan_cong_hien_tai.append(pc)
        

    def tao_khung_gio(self, tg_bat_dau: DateTime) -> None:
        kg = KhungGioAn(tg_bat_dau=tg_bat_dau, tg_ket_thuc_du_kien=tg_bat_dau + datetime.timedelta(minutes=BienChung.THOIGIANCODINH))
        self.khung_gio = kg
    
    def kiem_tra_co_nguoi_dam_nhan(self) -> bool:
        return self.nguoi_dam_nhan_id != None
    
    def kiem_tra_nguoi_dam_nhan(self, phucvu_id: int) -> bool:
        return self.nguoi_dam_nhan_id == phucvu_id
    
    def kiem_tra_phien_dang_hoat_dong(self) -> bool:
        return self.trang_thai == TrangThai.MO
    
    def chon_phuc_vu_dam_nhan(self, phuc_vu: PhucVu):
        self.nguoi_dam_nhan = phuc_vu

    def thuoc_phien_ban(self, user_id: int) -> bool:
        if self.le_tan_id == user_id:
            return True
        for pc in self.ds_phan_cong:
            if pc.phuc_vu_id == user_id:
                return True

        return False 
    
    def __repr__(self):
        return f"Phiên #{self.id}"
    
    def lay_phieu_mon(self, phieu_mon_id: int) -> PhieuMon:
        for phieu in self.ds_phieu_mon:
            if phieu.id == phieu_mon_id:
                return phieu
        
        return None

    def dang_co_phieu_mo(self) -> bool:
        for phieu in self.ds_phieu_mon:
            if phieu.is_phieu_mo():
                return True
        return False
    
    def tao_phieu_mon(self) -> None:
        phieu_mon = PhieuMon()
        self.ds_phieu_mon.append(phieu_mon)
    
    def cap_nhat_mon_ghi(self, status,  mon_ghi_id: int) -> bool:
        for phieu in self.ds_phieu_mon:
            mon_ghi = phieu.lay_mon_ghi(mon_ghi_id=mon_ghi_id)
            if mon_ghi:
                if not phieu.is_gui_bep():
                    raise Exception('Phiếu này đã hoàn thành hoặc đã hủy nên không thể cập nhật món trong phiếu.')
                phieu.cap_nhat_trang_thai_mon_ghi(status, mon_ghi_id=mon_ghi_id)
                if phieu.is_hoan_thanh_cac_mon():
                    phieu.cap_nhat_hoan_thanh_phieu()
                    return True
                else:
                    return False
            
        raise Exception('Không tồn tại món ghi trong phiếu để cập nhật.')
            
    

    
                

            

class PhanCong(Base):
    # Mapping bàn - phục vụ - phiên
    __tablename__ = 'phan_cong'

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThai), default=TrangThai.MO)
    dam_nhan_ghi_mon: Mapped[bool] = mapped_column('dam_nhan_ghi_mon', default=False, nullable=False)

    # Khóa ngoại: * PhanCong -> 1 PhucVu
    phuc_vu_id: Mapped[int] = mapped_column('phuc_vu_id', ForeignKey('phuc_vu.nguoi_dung_id'))
    phuc_vu: Mapped['PhucVu'] = relationship(back_populates='ds_phan_cong_hien_tai', lazy='joined')


    # Khóa ngoại: * PhanCong -> 1 Ban
    ban_id: Mapped[int] = mapped_column('ban_id', ForeignKey('ban.id'))
    ban: Mapped['Ban'] = relationship(lazy='joined', back_populates='ds_phan_cong')

    # Khóa ngoại: * PhanCong -> 1 PhienBan
    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))
    phien_ban: Mapped['PhienBan'] = relationship(back_populates='ds_phan_cong', lazy='joined')

    def hoan_thanh(self) -> None:
        self.trang_thai = TrangThai.HOANTHANH
        self.ban.hoan_thanh()
        

    def thuoc_phan_cong(self, phuc_vu_id: int) -> bool:
        return self.phuc_vu_id == phuc_vu_id
    
    def __repr__(self):
        ban_ten = self.ban.ten if self.ban else 'N/A'
        phuc_vu_ten = self.phuc_vu.ho_ten if self.phuc_vu else 'N/A'
        return f"PC #{self.id}: {ban_ten} - {phuc_vu_ten}"

class PhieuMon(Base):
    __tablename__ = 'phieu_mon'
    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))
    phien_ban: Mapped['PhienBan'] = relationship(lazy='joined', back_populates='ds_phieu_mon')

    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiPhieu), default=TrangThaiPhieu.DANGGHI)
    ly_do: Mapped[Optional[str]] = mapped_column('ly_do', String(500), nullable=True)
    ds_mon_ghi: Mapped[List['MonGhi']] = relationship(lazy='selectin', back_populates='phieu_mon')



    def hoan_thanh(self) -> None:
        self.trang_thai = TrangThaiPhieu.HOANTHANH

    def is_thanh_toan(self) -> bool:
        for mon in self.ds_mon_ghi:
            if mon.is_tam_ngung():
                return False
        
        return True

    def tinh_tien(self) -> int:
        tien = 0
        for mon in self.ds_mon_ghi:
            if mon.is_hoan_thanh():
                tien += mon.mo_ta_mon.gia * mon.so_luong
        return tien

    def is_phieu_mo(self) -> bool:
        return self.trang_thai == TrangThaiPhieu.DANGGHI
    
    def is_hoan_thanh(self) -> bool:
        return self.trang_thai == TrangThaiPhieu.HOANTHANH
    
    def is_gui_bep(self) -> bool:
        return self.trang_thai == TrangThaiPhieu.DAGUI
    
    def gui_phieu(self) -> None:
        self.trang_thai = TrangThaiPhieu.DAGUI

    def them_mon_ghi(self, so_luong: int, ghi_chu: str, mo_ta_mon: MoTaMon, ds_tuy_chon: List[TuyChonMon]):
        mon_ghi = MonGhi(so_luong=so_luong, ghi_chu=ghi_chu, mo_ta_mon=mo_ta_mon, ds_tuy_chon=ds_tuy_chon)

        self.ds_mon_ghi.append(mon_ghi)

    def lay_mon_ghi(self, mon_ghi_id: int) -> MonGhi:
        for mon in self.ds_mon_ghi:
            if mon.id == mon_ghi_id:
                return mon
        
        return None
    
    
    def cap_nhat_trang_thai_mon_ghi(self, status, mon_ghi_id: int):
        mon_ghi = self.lay_mon_ghi(mon_ghi_id=mon_ghi_id)
        if not mon_ghi:
            raise Exception('Không tồn tại món ghi này trong phiếu.')
        
        mon_ghi.cap_nhat_trang_thai(status)
    

    def cap_nhat_hoan_thanh_phieu(self):
        self.trang_thai = TrangThaiPhieu.HOANTHANH
    
    
    def is_hoan_thanh_cac_mon(self) -> bool:
        for mon in self.ds_mon_ghi:
            if mon.is_chua_nau():
                return False
        return True
    
    def __repr__(self):
        return f"Phiếu #{self.id}"

        
        



    

    

mon_nhom_tuychon_table = Table(
    'mon_nhom_tuychon',
    db.metadata,
    Column('mo_ta_mon_id', Integer, ForeignKey('mo_ta_mon.id'), primary_key=True),
    Column('nhom_tuy_chon_id', Integer, ForeignKey('nhom_tuy_chon.id'), primary_key=True)
)

monghi_tuychon_table = Table(
    'monghi_tuychon',
    db.metadata,
    Column('mon_ghi_id', Integer, ForeignKey('mon_ghi.id'), primary_key=True),
    Column('tuy_chon_id', Integer, ForeignKey('tuy_chon_mon.id'), primary_key=True)
)

class ThucDon(Base):
    # Danh sách Menu tổng của nhà hàng
    __tablename__ = 'thuc_don'
    
    ds_nhom_mon: Mapped[List['NhomMon']] = relationship(lazy='selectin')
    
    def __repr__(self):
        return f"Thực đơn #{self.id}"

    def lay_mo_ta_mon(self, mo_ta_mon_id: int) -> MoTaMon:
        for nhom in self.ds_nhom_mon:
            for mon in nhom.ds_mo_ta_mon:
                if mon.id == mo_ta_mon_id:
                    return mon
        
        return None

    

class NhomMon(Base):
    __tablename__ = 'nhom_mon'
    ten: Mapped[str] = mapped_column('ten', String(500), nullable=False)
    thuc_don_id: Mapped[int] = mapped_column('thuc_don_id', ForeignKey('thuc_don.id'))
    
    # Relationship với ThucDon
    thuc_don: Mapped['ThucDon'] = relationship(lazy='joined', back_populates='ds_nhom_mon')

    ds_mo_ta_mon: Mapped[List['MoTaMon']] = relationship(lazy='selectin', back_populates='nhom_mon')
    
    def __repr__(self):
        return self.ten

    def cap_nhat_ten(self, ten: str):
        self.ten = ten


class MoTaMon(Base):
    __tablename__ = 'mo_ta_mon'

    ten: Mapped[str] = mapped_column('ten', String(500), nullable=False)
    hinh: Mapped[Optional[str]] = mapped_column('hinh', String(1000), nullable=True)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiMon), default=TrangThaiMon.MOBAN)
    gia: Mapped[int] = mapped_column('gia', Integer, nullable=False)
    nhom_mon_id: Mapped[int] = mapped_column('nhom_mon_id', ForeignKey('nhom_mon.id'))
    
    # Relationship với NhomMon
    nhom_mon: Mapped['NhomMon'] = relationship(lazy='joined', back_populates='ds_mo_ta_mon')

    ds_nhom_tuy_chon: Mapped[List['NhomTuyChon']] = relationship(secondary=mon_nhom_tuychon_table, lazy='selectin')
    
    def __repr__(self):
        return f"{self.ten} ({self.gia:,} đ)"

    def cap_nhat_thong_tin(self, ten: str = None, hinh: str = None, gia: int = None, nhom_mon_id: int = None, trang_thai: str = None):
        if ten:
            self.ten = ten
        if hinh:
            self.hinh = hinh
        if gia is not None:
            self.gia = gia
        if nhom_mon_id:
            self.nhom_mon_id = nhom_mon_id
        if trang_thai:
            self.trang_thai = trang_thai
    
class NhomTuyChon(Base):
    __tablename__ = 'nhom_tuy_chon'
    ten: Mapped[str] = mapped_column('ten', String(500), nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiMon), default=TrangThaiMon.MOBAN)
    loai: Mapped[str] = mapped_column('loai', Enum(LoaiNhomTuyChon), nullable=False)

    ds_tuy_chon: Mapped[List['TuyChonMon']] = relationship(lazy='selectin', back_populates='nhom_tuy_chon')
    
    def __repr__(self):
        return self.ten

class TuyChonMon(Base):
    __tablename__ = 'tuy_chon_mon'
    ten: Mapped[str] = mapped_column('ten', String(500), nullable=False)
    gia: Mapped[int] = mapped_column('gia', Integer, nullable=False)
    hinh: Mapped[Optional[str]] = mapped_column('hinh', String(1000), nullable=True)

    nhom_tuy_chon_id: Mapped[int] = mapped_column('nhom_tuy_chon_id', ForeignKey('nhom_tuy_chon.id'))
    nhom_tuy_chon: Mapped['NhomTuyChon'] = relationship(lazy='joined', back_populates='ds_tuy_chon')

class MonGhi(Base):
    __tablename__ = 'mon_ghi'
    so_luong: Mapped[int] = mapped_column('so_luong', nullable=False)
    ghi_chu: Mapped[Optional[str]] = mapped_column('ghi_chu', String(500), nullable=True)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiMonGhi), nullable=False, default=TrangThaiMonGhi.CHUANAU)

    phieu_mon_id: Mapped[int] = mapped_column('phieu_mon_id', ForeignKey('phieu_mon.id'))
    phieu_mon: Mapped['PhieuMon'] = relationship(lazy='joined', back_populates='ds_mon_ghi')

    mo_ta_mon_id: Mapped[int] = mapped_column('mo_ta_mon_id', ForeignKey('mo_ta_mon.id'))
    mo_ta_mon: Mapped['MoTaMon'] = relationship(lazy='joined')

    ds_tuy_chon: Mapped[List['TuyChonMon']] = relationship(secondary=monghi_tuychon_table, lazy='selectin')
    ds_yeu_cau: Mapped[List['YCMonGhi']] = relationship(lazy='selectin', back_populates='mon_ghi')

    def kiem_tra_phuc_vu(self, phuc_vu_id: int) -> bool:
        return self.phieu_mon.phien_ban.kiem_tra_nguoi_dam_nhan(phucvu_id=phuc_vu_id)

    def tao_yeu_cau(self, ly_do: str):  
        if self.is_tam_ngung():
            raise Exception("Món ghi hiện tại đang có yêu cầu chưa được xử lý.")
        yc = YCMonGhi(ly_do=ly_do, trang_thai_truoc=self.trang_thai)
        self.ds_yeu_cau.append(yc)
        self.trang_thai = TrangThaiMonGhi.TAMNGUNG

        return yc

    def is_tam_ngung(self) -> bool:
        return self.trang_thai == TrangThaiMonGhi.TAMNGUNG

    def tinh_tien(self) -> int:
        tien = 0
        tien += self.mo_ta_mon.gia * self.so_luong
        for tc in self.ds_tuy_chon:
            tien += tc.gia
        
        return tien

    def huy_mon(self):
        self.cap_nhat_trang_thai(HuyMon())
    
    def hao_ton(self):
        self.cap_nhat_trang_thai(HaoTon())
    
    def chua_nau(self):
        self.trang_thai = TrangThaiMonGhi.CHUANAU

    def hoan_thanh(self):
        self.cap_nhat_trang_thai(HoanThanhMon())

    def is_chua_nau(self) -> bool:
        return self.trang_thai == TrangThaiMonGhi.CHUANAU
    
    def is_hoan_thanh(self) -> bool:
        return self.trang_thai == TrangThaiMonGhi.HOANTHANH
    
    def __repr__(self):
        mon_ten = self.mo_ta_mon.ten if self.mo_ta_mon else 'N/A'
        return f"Món ghi #{self.id}: {mon_ten}"

    @singledispatchmethod
    def cap_nhat_trang_thai(self, status):
        raise NotImplementedError('')

    @cap_nhat_trang_thai.register(HoanThanhMon)
    def _(self, status: HoanThanhMon):
        if self.trang_thai == TrangThaiMonGhi.HOANTHANH or self.trang_thai == TrangThaiMonGhi.HUY:
            raise Exception('Món ăn này đã hoàn thành hoặc đã hủy trước đó. Không thể đánh dấu hoàn thành.')
        
        self.trang_thai = TrangThaiMonGhi.HOANTHANH

    @cap_nhat_trang_thai.register(HaoTon)
    def _(self, status: HaoTon):
        if self.trang_thai == TrangThaiMonGhi.HAOTON or self.trang_thai == TrangThaiMonGhi.HUY:
            raise Exception('Món ăn này đã hao tổn hoặc đã hủy trước đó. Không thể đánh dấu hao tổn.')
        
        self.trang_thai = TrangThaiMonGhi.HAOTON
    
    @cap_nhat_trang_thai.register(HuyMon)
    def _(self, status: HuyMon):
        if self.trang_thai == TrangThaiMonGhi.HOANTHANH or self.trang_thai == TrangThaiMonGhi.HUY:
            raise Exception('Món ăn này đã hoàn thành hoặc hủy trước đó. Không thể đánh dấu hủy')
        
        self.trang_thai = TrangThaiMonGhi.HUY


class TrangThaiDoanhThu(enum.Enum):
    CHUAHOANTHANH = 'chuahoanthanh'
    DAHOANTHANH = 'dahoanthanh'
    DAHUY = 'dahuy'

class TrangThaiThanhToan(enum.Enum):
    DANGXULY = 'dangxuly'
    THANHCONG = 'thanhcong'
    THATBAI = 'thatbai'

class PhuongThucThanhToan(enum.Enum):
    TIENMAT = 'tienmat'
    STRIPE = 'stripe'

class CauHinhThue(Base):
    __tablename__ = 'cau_hinh_thue'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)
    ti_le: Mapped[float] = mapped_column('ti_le', nullable=False)
    hoat_dong: Mapped[bool] = mapped_column('hoat_dong', default=True, nullable=False)


    def tinh_gia_tri(self, tien: int) -> int:
        return tien * self.ti_le

class DoanhThuKhuyenMai(db.Model):
    __tablename__ = 'doanhthu_khuyenmai'

    doanh_thu_id: Mapped[int] = mapped_column('doanh_thu_id', ForeignKey('doanh_thu.id'), primary_key=True)

    khuyen_mai_id: Mapped[int] = mapped_column('khuyen_mai_id', ForeignKey('khuyen_mai.id'), primary_key=True)
    khuyen_mai: Mapped['KhuyenMai'] = relationship(lazy='joined')


    so_tien_giam: Mapped[int] = mapped_column('so_tien_giam', nullable=False)



class TienMat:
    pass
class Stripe:
    pass

class DoanhThu(Base):
    __tablename__ = 'doanh_thu'
    tong_tien: Mapped[int] = mapped_column('tong_tien', Integer, default=0, nullable=False)
    tien_giam_gia: Mapped[int] = mapped_column('tien_giam_gia', Integer, default=0, nullable=False)
    tien_cuoi_cung: Mapped[int] = mapped_column('tien_cuoi_cung', default=0, nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiDoanhThu), default=TrangThaiDoanhThu.CHUAHOANTHANH, nullable=False)
    
    ten_thue: Mapped[str] = mapped_column('ten_thue', String(100), nullable=True)
    ti_le_thue: Mapped[float] = mapped_column('ti_le_thue', nullable=True)
    tien_thue: Mapped[int] = mapped_column('tien_thue', nullable=True)
    thu_ngan_id: Mapped[int] = mapped_column('thu_ngan_id', ForeignKey('thu_ngan.nguoi_dung_id'))
    
    # Relationship với ThuNgan
    thu_ngan: Mapped['ThuNgan'] = relationship(
        lazy='joined', 
        back_populates='ds_doanh_thu',
        overlaps='ds_doanh_thu_chua_hoan_thanh'  # Thêm để tránh warning
    )

    phien_ban_id: Mapped[int] = mapped_column('phien_ban_id', ForeignKey('phien_ban.id'))
    phien_ban: Mapped['PhienBan'] = relationship(lazy='joined', back_populates='doanh_thu')

    
    ds_khuyen_mai: Mapped[List['DoanhThuKhuyenMai']] = relationship(lazy='selectin')
    ds_thanh_toan: Mapped[List['ThanhToan']] = relationship(lazy='selectin')
    
    def __repr__(self):
        return f"Doanh thu #{self.id} - {self.tien_cuoi_cung:,} đ"


    def hoan_thanh(self):
        self.trang_thai = TrangThaiDoanhThu.DAHOANTHANH
        self.phien_ban.hoan_thanh()

    def is_hoan_thanh(self) -> bool:
        tong = 0
        for tt in self.ds_thanh_toan:
            if tt.is_hoan_thanh():
                tong += tt.so_tien
        return tong == self.tien_cuoi_cung

    def lay_phien_thanh_toan(self):
        if not len(self.ds_thanh_toan):
            raise Exception("Chưa có phiên thanh toán nào trong doanh thu.")
        return self.ds_thanh_toan[-1]

    def cap_nhat(self, thue: CauHinhThue, ds_khuyen_mai_tu_dong: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None) -> None:
        tong_tien = self.phien_ban.tinh_tong_tien()
        tien_giam_gia = 0
        for km in ds_khuyen_mai_tu_dong: #Lấy 1 tự động áp dụng
            if km.co_the_su_dung(tong_tien):
                so_tien_giam = km.tinh_so_tien_duoc_giam(tong_tien)
                tien_giam_gia = so_tien_giam + tien_giam_gia
                dt_km = DoanhThuKhuyenMai(doanh_thu_id=self.id, khuyen_mai_id=km.id, so_tien_giam=so_tien_giam)

                self.ds_khuyen_mai.append(dt_km)
                break

        if ds_khuyen_mai_tuy_chon:
            for km in ds_khuyen_mai_tuy_chon:
                if km.co_the_su_dung(tong_tien):
                    so_tien_giam = km.tinh_so_tien_duoc_giam(tong_tien)
                    tien_giam_gia = so_tien_giam + tien_giam_gia
                    dt_km = DoanhThuKhuyenMai(doanh_thu_id=self.id, khuyen_mai_id=km.id, so_tien_giam=so_tien_giam)
                    self.ds_khuyen_mai.append(dt_km)
                    break
                else:
                    raise Exception("Không đủ điều kiện để sử dụng")

        tien_sau = (tong_tien - tien_giam_gia) if (tong_tien - tien_giam_gia >= 0) else 0
        
        tien_cuoi_cung = tien_sau - thue.tinh_gia_tri(tien=tien_sau)

        self.tong_tien = tong_tien
        self.tien_giam_gia = tien_giam_gia
        self.tien_cuoi_cung = tien_cuoi_cung
        self.ten_thue = thue.ten
        self.ti_le_thue = thue.ti_le
        self.tien_thue = thue.tinh_gia_tri(tien=tien_sau)
    
    @singledispatchmethod
    def xu_ly_thanh_toan(self, loai):
        raise NotImplementedError("Chưa implement phương thức thanh toán")
    
    @xu_ly_thanh_toan.register(TienMat)
    def _(self, loai: TienMat):
        tt = ThanhToan(so_tien=self.tien_cuoi_cung, phuong_thuc=PhuongThucThanhToan.TIENMAT, trang_thai=TrangThaiThanhToan.DANGXULY)
        self.ds_thanh_toan.append(tt)
    
    @xu_ly_thanh_toan.register(Stripe)
    def _(self, loai: Stripe):
        tt = ThanhToan(so_tien=self.tien_cuoi_cung, phuong_thuc=PhuongThucThanhToan.STRIPE, trang_thai=TrangThaiThanhToan.DANGXULY)
        self.ds_thanh_toan.append(tt)


    def hoan_tat_thanh_toan(self, thanh_toan_id: int = None):
        if not thanh_toan_id: #Không có tức là thanh toán bằng tiền mặt
            self.ds_thanh_toan[-1].hoan_thanh()
        else:
            for tt in self.ds_thanh_toan:
                if tt.id == thanh_toan_id:
                    tt.hoan_thanh()
                    break

        if not self.is_hoan_thanh():
            return False
        else:
            self.hoan_thanh()
            return True

    def thanh_toan_tien_mat(self):
        self.xu_ly_thanh_toan(TienMat())
        self.hoan_tat_thanh_toan()

    
    def thanh_toan_online(self):
        self.xu_ly_thanh_toan(Stripe())











        

    
    





class ThanhToan(Base):
    __tablename__ = 'thanh_toan'
    so_tien: Mapped[int] = mapped_column('so_tien', Integer, nullable=False)
    phuong_thuc: Mapped[str] = mapped_column('phuong_thuc', Enum(PhuongThucThanhToan), nullable=False)
    trang_thai: Mapped[str] = mapped_column('trang_thai', Enum(TrangThaiThanhToan), default=TrangThaiThanhToan.DANGXULY, nullable=False)

    doanh_thu_id: Mapped[int] = mapped_column('doanh_thu_id', ForeignKey('doanh_thu.id'))

    def hoan_thanh(self):
        self.trang_thai = TrangThaiThanhToan.THANHCONG

        print("Vào được hoàn thành method của thanh toán id: ", self.id)

    def is_hoan_thanh(self):
        return self.trang_thai == TrangThaiThanhToan.THANHCONG

    def that_bai(self):
        self.trang_thai = TrangThaiThanhToan.THATBAI
    
    def __repr__(self):
        return f"Thanh toán #{self.id} - {self.so_tien:,} đ"

class KhuyenMai(Base):
    # Base cho các chương trình giảm giá
    __tablename__ = 'khuyen_mai'
    ten: Mapped[str] = mapped_column('ten', String(100), nullable=False)
    mo_ta: Mapped[str] = mapped_column('mo_ta', String(500), nullable=False)
    hoat_dong: Mapped[bool] = mapped_column('hoat_dong', default=True, nullable=False)

    gia_tri_don_hang_toi_thieu: Mapped[int] = mapped_column('gia_tri_don_hang_toi_thieu', nullable=False)
    gioi_han: Mapped[Optional[int]] = mapped_column('gioi_han', nullable=True)

    ngay_bat_dau: Mapped[DateTime] = mapped_column('ngay_bat_dau', DateTime, default=datetime.datetime.now, nullable=False)
    ngay_het_han: Mapped[Optional[DateTime]] = mapped_column('ngay_het_han', DateTime, nullable=True)
    tu_dong_ap_dung: Mapped[bool] = mapped_column('tu_dong_ap_dung', default=True, nullable=False)
    thu_tu_uu_tien: Mapped[int] = mapped_column('thu_tu_uu_tien', nullable=False)


    type: Mapped[str] = mapped_column('type', String(100), nullable=True)
    __mapper_args__ = {
        "polymorphic_identity": "khuyen_mai",
        "polymorphic_on": type,
    }

    def co_the_su_dung(self, gia_tri: int) -> bool:
        raise NotImplementedError('Chưa implement')

    def tinh_so_tien_duoc_giam(self, tien: int) -> int:
        raise NotImplementedError('Chưa implement')
    
    def __repr__(self):
        return self.ten

    def cap_nhat_thong_tin(self, **kwargs):
        if 'ten' in kwargs:
            self.ten = kwargs['ten']
        if 'mo_ta' in kwargs:
            self.mo_ta = kwargs['mo_ta']
        if 'hoat_dong' in kwargs:
            self.hoat_dong = kwargs['hoat_dong']
        if 'gia_tri_don_hang_toi_thieu' in kwargs:
            self.gia_tri_don_hang_toi_thieu = kwargs['gia_tri_don_hang_toi_thieu']
        if 'gioi_han' in kwargs:
            self.gioi_han = kwargs['gioi_han']
        if 'ngay_bat_dau' in kwargs:
            self.ngay_bat_dau = kwargs['ngay_bat_dau']
        if 'ngay_het_han' in kwargs:
            self.ngay_het_han = kwargs['ngay_het_han']
        if 'tu_dong_ap_dung' in kwargs:
            self.tu_dong_ap_dung = kwargs['tu_dong_ap_dung']
        if 'thu_tu_uu_tien' in kwargs:
            self.thu_tu_uu_tien = kwargs['thu_tu_uu_tien']

class KhuyenMaiTheoPhanTram(KhuyenMai):
    __tablename__ = 'khuyen_mai_theo_phan_tram'

    phan_tram: Mapped[int] = mapped_column('phan_tram', nullable=False)

    khuyen_mai_id: Mapped[int] = mapped_column('khuyen_mai_id', ForeignKey('khuyen_mai.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khuyen_mai_theo_phan_tram",
    }

    def tinh_so_tien_duoc_giam(self, tien: int) -> int:
        return tien * (self.phan_tram / 100)
    
    def co_the_su_dung(self, gia_tri: int) -> bool:
        return self.gia_tri_don_hang_toi_thieu <= gia_tri
    
    def cap_nhat_thong_tin(self, **kwargs):
        super().cap_nhat_thong_tin(**kwargs)
        if 'ti_le' in kwargs and kwargs['ti_le'] is not None:
            self.phan_tram = kwargs['ti_le']
    

class KhuyenMaiCung(KhuyenMai):
    __tablename__ = 'khuyen_mai_cung'

    so_tien_tru: Mapped[int] = mapped_column('so_tien_tru', nullable=False)

    khuyen_mai_id: Mapped[int] = mapped_column('khuyen_mai_id', ForeignKey('khuyen_mai.id'), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "khuyen_mai_cung",
    }

    def co_the_su_dung(self, gia_tri: int) -> bool:
        if self.gia_tri_don_hang_toi_thieu <= gia_tri:
            return True
        raise Exception("Bạn không đủ điều kiện để sử dụng loại khuyến mãi này")

    def tinh_so_tien_duoc_giam(self, tien: int) -> int:
        return self.so_tien_tru

    def cap_nhat_thong_tin(self, **kwargs):
        super().cap_nhat_thong_tin(**kwargs)
        if 'so_tien_giam' in kwargs and kwargs['so_tien_giam'] is not None:
            self.so_tien_tru = kwargs['so_tien_giam']
        