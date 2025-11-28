# Dùng để get ra các instance từ DI
from injector import Module, singleton, Injector


# DAO
from app.data.dao.interfaces.interfaces import IKhuVucDAO, IBanDAO, INguoiDungDAO, IPhienBanDAO, ITaiKhoanDAO, IVaiTroDAO
from app.data.dao.dao import KhuVucDAO, BanDAO, PhienBanDAO, NguoiDungDAO, TaiKhoanDAO, VaiTroDAO

# Service
from app.domain.services.interfaces.interfaces import IKhuVucService, IBanService, IBoChonNhanVien, ITaiKhoanService
from app.domain.services.service import KhuVucService, BanService, BoChonNhanVien, TaiKhoanService

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

class ServiceModule(Module):
    def configure(self, binder):
        binder.bind(interface=IKhuVucService, to=KhuVucService, scope=singleton)
        binder.bind(interface=IBanService, to=BanService, scope=singleton)
        binder.bind(interface=IBoChonNhanVien, to=BoChonNhanVien, scope=singleton)
        binder.bind(interface=ITaiKhoanService, to=TaiKhoanService, scope=singleton)
        binder.bind(interface=IHelper, to=Helper, scope=singleton)

injector_instance = Injector([DAOModule(), ServiceModule()])





