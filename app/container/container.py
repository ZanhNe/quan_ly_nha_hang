# Dùng để get ra các instance từ DI
from injector import Module, singleton, Injector


# DAO
from app.data.dao.interfaces.interfaces import (IKhuVucDAO, IBanDAO, INguoiDungDAO, IPhienBanDAO
                                                , ITaiKhoanDAO, IVaiTroDAO, IThucDonDAO
                                                , ITuyChonMonReadDAO, IPhieuMonReadDAO, IMonGhiReadDAO, IThongBaoReadDAO
                                                , IKhuyenMaiDAO, ICauHinhThueDAO, IDoanhThuDAO, IYeuCauReadDAO, IBaoCaoDAO)
from app.data.dao.dao import (KhuVucDAO, BanDAO, PhienBanDAO, NguoiDungDAO, TaiKhoanDAO, VaiTroDAO
                              , ThucDonDAO, TuyChonMonReadDAO, PhieuMonReadDAO, MonGhiReadDAO, ThongBaoReadDAO, DoanhThuDAO
                              , KhuyenMaiDAO, CauHinhThueDAO, YeuCauReadDAO, BaoCaoDAO)

# Service
from app.domain.services.interfaces.interfaces import (IKhuVucService, IBanService, IBoChonNhanVien
                                                       , ITaiKhoanService, IPhienBanService, IThucDonService
                                                       , IThemMonService, INguoiDungService, IDoanhThuService
                                                       , IKhuyenMaiService, IDoanhThuThanhToanService, IBaoCaoService)
from app.domain.services.service import (KhuVucService, BanService, BoChonNhanVien
                                         , TaiKhoanService, PhienBanService, ThucDonService, ThemMonService, NguoiDungService, DoanhThuService
                                         , KhuyenMaiService, DoanhThuThanhToanService, BaoCaoService)
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

injector_instance = Injector([DAOModule(), ServiceModule()])





