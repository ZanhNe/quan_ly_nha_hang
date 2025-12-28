# Dùng để get ra các instance từ DI
from injector import Module, singleton, Injector


# DAO
from app.data.dao.interfaces.interfaces import (IKhuVucDAO, IBanDAO, INguoiDungDAO, IPhienBanDAO
                                                , ITaiKhoanDAO, IVaiTroDAO, IThucDonDAO
                                                , ITuyChonMonReadDAO, IPhieuMonReadDAO, IMonGhiReadDAO, IThongBaoReadDAO
                                                , IKhuyenMaiDAO, ICauHinhThueDAO, IDoanhThuDAO, IYeuCauReadDAO, IBaoCaoDAO
                                                , IDatBanDAO
                                                # Admin DAOs
                                                , IAdminTaiKhoanDAO, IAdminNguoiDungDAO, IAdminKhuVucDAO, IAdminBanDAO
                                                , IAdminThucDonDAO, IAdminKhuyenMaiDAO, IAdminCauHinhThueDAO)
from app.data.dao.dao import (KhuVucDAO, BanDAO, PhienBanDAO, NguoiDungDAO, TaiKhoanDAO, VaiTroDAO
                              , ThucDonDAO, TuyChonMonReadDAO, PhieuMonReadDAO, MonGhiReadDAO, ThongBaoReadDAO, DoanhThuDAO
                              , KhuyenMaiDAO, CauHinhThueDAO, YeuCauReadDAO, BaoCaoDAO, DatBanDAO)
from app.data.dao.admin_dao import (AdminTaiKhoanDAO, AdminNguoiDungDAO, AdminKhuVucDAO, AdminBanDAO
                                    , AdminThucDonDAO, AdminKhuyenMaiDAO, AdminCauHinhThueDAO)

# Service
from app.domain.services.interfaces.interfaces import (IKhuVucService, IBanService, IBoChonNhanVien
                                                       , ITaiKhoanService, IPhienBanService, IThucDonService
                                                       , IThemMonService, INguoiDungService, IDoanhThuService
                                                       , IKhuyenMaiService, IDoanhThuThanhToanService, IBaoCaoService
                                                       # Admin Services
                                                       , IAdminTaiKhoanService, IAdminNguoiDungService, IAdminKhuVucService
                                                       , IAdminBanService, IAdminThucDonService, IAdminKhuyenMaiService
                                                       , IAdminCauHinhThueService)
from app.domain.services.service import (KhuVucService, BanService, BoChonNhanVien
                                         , TaiKhoanService, PhienBanService, ThucDonService, ThemMonService, NguoiDungService, DoanhThuService
                                         , KhuyenMaiService, DoanhThuThanhToanService, BaoCaoService)
from app.domain.services.admin_service import (AdminTaiKhoanService, AdminNguoiDungService, AdminKhuVucService
                                               , AdminBanService, AdminThucDonService, AdminKhuyenMaiService
                                               , AdminCauHinhThueService)
from app.payment.interface import ThanhToanOnline
from app.payment.payment import Stripe

#utils
from app.utils.helper import IHelper, Helper

class DAOModule(Module):
    def configure(self, binder):
        binder.bind(interface=IKhuVucDAO, to=KhuVucDAO, scope=singleton)
        binder.bind(interface=IBanDAO, to=BanDAO, scope=singleton)
        binder.bind(interface=INguoiDungDAO, to=NguoiDungDAO, scope=singleton)
        binder.bind(interface=IPhienBanDAO, to=PhienBanDAO, scope=singleton)
        binder.bind(interface=ITaiKhoanDAO, to=TaiKhoanDAO, scope=singleton)
        binder.bind(interface=IVaiTroDAO, to=VaiTroDAO, scope=singleton)
        binder.bind(interface=IThucDonDAO, to=ThucDonDAO, scope=singleton)
        binder.bind(interface=ITuyChonMonReadDAO, to=TuyChonMonReadDAO, scope=singleton)
        binder.bind(interface=IPhieuMonReadDAO, to=PhieuMonReadDAO, scope=singleton)
        binder.bind(interface=IMonGhiReadDAO, to=MonGhiReadDAO, scope=singleton)
        binder.bind(interface=IThongBaoReadDAO, to=ThongBaoReadDAO, scope=singleton)
        binder.bind(interface=IKhuyenMaiDAO, to=KhuyenMaiDAO, scope=singleton)
        binder.bind(interface=ICauHinhThueDAO, to=CauHinhThueDAO, scope=singleton)
        binder.bind(interface=IDoanhThuDAO, to=DoanhThuDAO, scope=singleton)
        binder.bind(interface=IYeuCauReadDAO, to=YeuCauReadDAO, scope=singleton)
        binder.bind(interface=IBaoCaoDAO, to=BaoCaoDAO, scope=singleton)
        binder.bind(interface=IDatBanDAO, to=DatBanDAO, scope=singleton)
        # Admin DAOs
        binder.bind(interface=IAdminTaiKhoanDAO, to=AdminTaiKhoanDAO, scope=singleton)
        binder.bind(interface=IAdminNguoiDungDAO, to=AdminNguoiDungDAO, scope=singleton)
        binder.bind(interface=IAdminKhuVucDAO, to=AdminKhuVucDAO, scope=singleton)
        binder.bind(interface=IAdminBanDAO, to=AdminBanDAO, scope=singleton)
        binder.bind(interface=IAdminThucDonDAO, to=AdminThucDonDAO, scope=singleton)
        binder.bind(interface=IAdminKhuyenMaiDAO, to=AdminKhuyenMaiDAO, scope=singleton)
        binder.bind(interface=IAdminCauHinhThueDAO, to=AdminCauHinhThueDAO, scope=singleton)

class ServiceModule(Module):
    def configure(self, binder):
        binder.bind(interface=IKhuVucService, to=KhuVucService, scope=singleton)
        binder.bind(interface=IBanService, to=BanService, scope=singleton)
        binder.bind(interface=IBoChonNhanVien, to=BoChonNhanVien, scope=singleton)
        binder.bind(interface=ITaiKhoanService, to=TaiKhoanService, scope=singleton)
        binder.bind(interface=IPhienBanService, to=PhienBanService, scope=singleton)
        binder.bind(interface=IThucDonService, to=ThucDonService, scope=singleton)
        binder.bind(interface=IThemMonService, to=ThemMonService, scope=singleton)
        binder.bind(interface=INguoiDungService, to=NguoiDungService, scope=singleton)
        binder.bind(interface=IHelper, to=Helper, scope=singleton)
        binder.bind(interface=IDoanhThuService, to=DoanhThuService, scope=singleton)
        binder.bind(interface=IDoanhThuThanhToanService, to=DoanhThuThanhToanService, scope=singleton)
        binder.bind(interface=IKhuyenMaiService, to=KhuyenMaiService, scope=singleton)
        binder.bind(interface=ThanhToanOnline, to=Stripe, scope=singleton)
        binder.bind(interface=IBaoCaoService, to=BaoCaoService, scope=singleton)
        # Admin Services
        binder.bind(interface=IAdminTaiKhoanService, to=AdminTaiKhoanService, scope=singleton)
        binder.bind(interface=IAdminNguoiDungService, to=AdminNguoiDungService, scope=singleton)
        binder.bind(interface=IAdminKhuVucService, to=AdminKhuVucService, scope=singleton)
        binder.bind(interface=IAdminBanService, to=AdminBanService, scope=singleton)
        binder.bind(interface=IAdminThucDonService, to=AdminThucDonService, scope=singleton)
        binder.bind(interface=IAdminKhuyenMaiService, to=AdminKhuyenMaiService, scope=singleton)
        binder.bind(interface=IAdminCauHinhThueService, to=AdminCauHinhThueService, scope=singleton)

injector_instance = Injector([DAOModule(), ServiceModule()])

