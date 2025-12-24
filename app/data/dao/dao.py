from sqlalchemy import select, func, cast, Date, extract
from app.extentions.extentions import db
from typing import List, Optional
from flask_sqlalchemy.session import Session
from app.data.models import (KhuVuc, Ban, NguoiDung, PhucVu, PhienBan, TaiKhoan, VaiTro, PhanCong, TrangThai, ThucDon, PhieuMon
                             , TuyChonMon, TrangThaiPhieu, MonGhi, ThongBao, KhuyenMai, CauHinhThue, DoanhThu, YeuCau, TrangThaiYeuCau
                             , TrangThaiDoanhThu, TrangThaiMonGhi, MoTaMon, NhomMon)
from app.data.dao.interfaces.interfaces import (IBanDAO, IKhuVucDAO, INguoiDungDAO, IPhienBanDAO, ITaiKhoanDAO, IVaiTroDAO
                                                , IThucDonDAO, ITuyChonMonReadDAO, IPhieuMonReadDAO, IMonGhiReadDAO
                                                , IThongBaoReadDAO, IKhuyenMaiDAO, ICauHinhThueDAO, IDoanhThuDAO, IYeuCauReadDAO
                                                , IBaoCaoDAO)


class ThongBaoReadDAO(IThongBaoReadDAO):

    def find_by_nguoi_dung_id(self, session: Session, nguoi_dung_id: int, page: int, limit: int) -> List[ThongBao]:
        stmt = (select(ThongBao).where(ThongBao.nguoi_nhan_id == nguoi_dung_id).order_by(ThongBao.ngay_tao.desc()))
        pagination = db.paginate(stmt, page=page, per_page=limit, error_out=False)

        ds_tb = [tb for tb in pagination.items]
        return ds_tb, pagination.has_next
    
    def count_unread(self, session: Session, nguoi_dung_id: int) -> int:
        stmt = select(func.count(ThongBao.id)).where(ThongBao.nguoi_nhan_id == nguoi_dung_id).where(ThongBao.da_doc == False)
        count = session.execute(statement=stmt).scalar()
        return count

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
        

class YeuCauReadDAO(IYeuCauReadDAO):

    def find_all_by_pending(self, session: Session) -> List[YeuCau]:
        stmt = (select(YeuCau).where(YeuCau.trang_thai == TrangThaiYeuCau.CHODUYET).order_by(YeuCau.id.desc()))

        ds_yeu_cau = session.execute(statement=stmt).scalars().all()
        return ds_yeu_cau

    def find_by_id(self, session: Session, yeu_cau_id: int) -> YeuCau:
        yeu_cau = session.get(YeuCau, ident=yeu_cau_id)
        return yeu_cau

    def save(self, session: Session, yeu_cau: YeuCau) -> None:
        session.add(yeu_cau)
        session.flush()
    
class PhienBanDAO(IPhienBanDAO):

    def save(self, session: Session, phien: PhienBan) -> None:
        session.add(phien)
        session.flush()

    def find_by_mo(self, session: Session) -> List[PhienBan]:
        stmt = (select(PhienBan)
                .where(PhienBan.trang_thai == TrangThai.MO))
        ds_phien_ban = session.execute(statement=stmt).scalars().all()
        return ds_phien_ban

    def find_by_id(self, session: Session, phien_ban_id: int) -> PhienBan:
        phien_ban = session.get(PhienBan, phien_ban_id)
        return phien_ban
    
    def find_by_phucvu_id(self, session: Session, phucvu_id: int) -> List[PhienBan]:
        stmt = (select(PhienBan)
                .join(PhanCong, PhienBan.id == PhanCong.phien_ban_id)
                .join(PhucVu, PhanCong.phuc_vu_id == PhucVu.nguoi_dung_id)
                .where(PhucVu.nguoi_dung_id == phucvu_id)
                .where(PhienBan.trang_thai == TrangThai.MO)
                .distinct())
        ds_phien_ban = session.execute(statement=stmt).scalars().all()
        return ds_phien_ban
    
    def find_by_phieu_mon_id(self, session: Session, phieu_mon_id: int) -> PhienBan:
        stmt = (select(PhienBan)
                .join(PhieuMon, PhienBan.id == PhieuMon.phien_ban_id)
                .where(PhieuMon.id == phieu_mon_id))
        phien_ban = session.execute(statement=stmt).scalar_one_or_none()
        return phien_ban

    def find_by_mon_ghi_id(self, session: Session, mon_ghi_id: int) -> PhienBan:
        stmt = (select(PhienBan)
                .join(PhieuMon, PhienBan.id == PhieuMon.phien_ban_id)
                .join(MonGhi, PhieuMon.id == MonGhi.phieu_mon_id)
                .where((MonGhi.id == mon_ghi_id)))
        phien_ban = session.execute(statement=stmt).scalars().unique().first()
        return phien_ban
    

class PhieuMonReadDAO(IPhieuMonReadDAO):
    def find_by_trang_thai_mo(self, session: Session) -> List[PhieuMon]:
        stmt = (select(PhieuMon)
                .where(PhieuMon.trang_thai == TrangThaiPhieu.DAGUI)
                .order_by(PhieuMon.ngay_tao))
        ds_phieu_mon = session.execute(statement=stmt).scalars().all()
        return ds_phieu_mon
    
    def find_by_id(self, session: Session, phieu_mon_id: int) -> PhieuMon:
        phieu_mon = session.get(PhieuMon, ident=phieu_mon_id)
        return phieu_mon

class MonGhiReadDAO(IMonGhiReadDAO):
    def find_by_id(self, session: Session, mon_ghi_id: int) -> MonGhi:
        mon_ghi = session.get(MonGhi, ident=mon_ghi_id)
        return mon_ghi
        

class ThucDonDAO(IThucDonDAO):
    def find_first(self, session: Session) -> ThucDon:
        stmt = select(ThucDon)
        thuc_don = session.execute(statement=stmt).scalars().first()

        return thuc_don
class TuyChonMonReadDAO(ITuyChonMonReadDAO):
    def find_by_ids(self, session, tuy_chon_mon_ids: List[int]) -> List[TuyChonMon]:
        stmt = (select(TuyChonMon)
                .where(TuyChonMon.id.in_(tuy_chon_mon_ids)))
        ds_tuy_chon_mon = session.execute(statement=stmt).scalars().all()
        return ds_tuy_chon_mon

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
    
    def find_by_id(self, session: Session, tai_khoan_id: int) -> Optional[TaiKhoan]:
        tai_khoan = session.get(TaiKhoan, ident=tai_khoan_id)
        return tai_khoan
    
    def find_cho_xet_duyet(self, session: Session) -> List[TaiKhoan]:
        """Tìm tất cả tài khoản đã xác thực email nhưng chưa được Admin duyệt (vai trò VODANH)"""
        from app.data.models import TenVaiTro
        stmt = (
            select(TaiKhoan)
            .join(VaiTro, TaiKhoan.vai_tro_id == VaiTro.id)
            .where(TaiKhoan.is_xac_thuc == True)
            .where(VaiTro.vai_tro == TenVaiTro.VODANH)
            .order_by(TaiKhoan.ngay_tao.desc())
        )
        ds_tai_khoan = session.execute(statement=stmt).scalars().all()
        return ds_tai_khoan

    

        

class NguoiDungDAO(INguoiDungDAO):

    def find_by_id(self, session: Session, id: int) -> Optional[NguoiDung]:
        nguoi_dung = session.get(NguoiDung, id)
        return nguoi_dung
    
    def find_by_khuvuc_id(self, session: Session, khuvuc_id: int) -> List[NguoiDung]:
        stmt = select(NguoiDung).join(PhucVu).where(PhucVu.khu_vuc_id == khuvuc_id)
        ds_phuc_vu = session.scalars(statement=stmt).all()
        return ds_phuc_vu
    
    def save(self, session: Session, nguoi_dung: NguoiDung):
        session.add(nguoi_dung)
        session.flush()


class DoanhThuDAO(IDoanhThuDAO):
    def find_by_phien_ban_id(self, session: Session, phien_ban_id: int) -> DoanhThu:
        stmt = select(DoanhThu).where(DoanhThu.phien_ban_id == phien_ban_id)
        doanh_thu = session.execute(statement=stmt).scalar()
        return doanh_thu
    
    def find_by_id(self, session: Session, doanh_thu_id: int) -> DoanhThu:
        doanh_thu = session.get(DoanhThu, ident=doanh_thu_id)
        return doanh_thu
    
    def save(self, session: Session, doanh_thu: DoanhThu):
        session.add(doanh_thu)
        session.flush()
    
    

class KhuyenMaiDAO(IKhuyenMaiDAO):

    def find_by_hoat_dong_and_tu_dong_ap_dung(self, session: Session) -> List[KhuyenMai]:
        stmt = (select(KhuyenMai)
                .where(KhuyenMai.hoat_dong == True)
                .where(KhuyenMai.tu_dong_ap_dung == True))
        ds_khuyen_mai = session.execute(statement=stmt).scalars().all()
        return ds_khuyen_mai
    
    def find_by_tuy_chon(self, session: Session) -> List[KhuyenMai]:
        stmt = (select(KhuyenMai)
                .where(KhuyenMai.tu_dong_ap_dung == False))
        ds_khuyen_mai = session.execute(statement=stmt).scalars().all()
        return ds_khuyen_mai
    
    def find_by_ids(self, session: Session, khuyen_mai_ids: List[int]) -> List[KhuyenMai]:
        stmt = select(KhuyenMai).where(KhuyenMai.id.in_(khuyen_mai_ids)).order_by(KhuyenMai.thu_tu_uu_tien.desc())
        ds_khuyen_mai = session.execute(statement=stmt).scalars().all()
        return ds_khuyen_mai

class CauHinhThueDAO(ICauHinhThueDAO):

    def find_by_hoat_dong(self, session: Session) -> CauHinhThue:
        stmt = select(CauHinhThue).where(CauHinhThue.hoat_dong == True)
        cau_hinh_thue = session.execute(statement=stmt).scalars().all()
        for cht in cau_hinh_thue:
            return cht
        return None


class BaoCaoDAO(IBaoCaoDAO):

    def thong_ke_tong_quan(self, session: Session, tu_ngay, den_ngay) -> dict:
        stmt_doanh_thu = (
            select(
                func.count(DoanhThu.id).label('tong_don'),
                func.coalesce(func.sum(DoanhThu.tong_tien), 0).label('tong_doanh_thu'),
                func.coalesce(func.sum(DoanhThu.tien_giam_gia), 0).label('tong_giam_gia'),
                func.coalesce(func.sum(DoanhThu.tien_cuoi_cung), 0).label('thuc_thu')
            )
            .where(DoanhThu.trang_thai == TrangThaiDoanhThu.DAHOANTHANH)
            .where(cast(DoanhThu.ngay_tao, Date) >= tu_ngay)
            .where(cast(DoanhThu.ngay_tao, Date) <= den_ngay)
        )
        result_dt = session.execute(stmt_doanh_thu).first()

        # Đếm số phiên bàn (số lượt khách)
        stmt_khach = (
            select(func.count(PhienBan.id))
            .where(PhienBan.trang_thai == TrangThai.HOANTHANH)
            .where(cast(PhienBan.ngay_tao, Date) >= tu_ngay)
            .where(cast(PhienBan.ngay_tao, Date) <= den_ngay)
        )
        tong_khach = session.execute(stmt_khach).scalar() or 0

        # Đếm yêu cầu đang chờ
        stmt_yc = select(func.count(YeuCau.id)).where(YeuCau.trang_thai == TrangThaiYeuCau.CHODUYET)
        yeu_cau_cho = session.execute(stmt_yc).scalar() or 0

        return {
            'tong_don': result_dt.tong_don or 0,
            'tong_doanh_thu': int(result_dt.tong_doanh_thu or 0),
            'tong_giam_gia': int(result_dt.tong_giam_gia or 0),
            'thuc_thu': int(result_dt.thuc_thu or 0),
            'tong_khach': tong_khach,
            'yeu_cau_cho': yeu_cau_cho
        }

    def thong_ke_theo_ngay(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        stmt = (
            select(
                cast(DoanhThu.ngay_tao, Date).label('ngay'),
                func.count(DoanhThu.id).label('so_don'),
                func.coalesce(func.sum(DoanhThu.tien_cuoi_cung), 0).label('doanh_thu')
            )
            .where(DoanhThu.trang_thai == TrangThaiDoanhThu.DAHOANTHANH)
            .where(cast(DoanhThu.ngay_tao, Date) >= tu_ngay)
            .where(cast(DoanhThu.ngay_tao, Date) <= den_ngay)
            .group_by(cast(DoanhThu.ngay_tao, Date))
            .order_by(cast(DoanhThu.ngay_tao, Date))
        )
        results = session.execute(stmt).all()
        return [{'ngay': str(r.ngay), 'so_don': r.so_don, 'doanh_thu': int(r.doanh_thu)} for r in results]

    def top_mon_ban_chay(self, session: Session, tu_ngay, den_ngay, limit: int = 10) -> List[dict]:
        stmt = (
            select(
                MoTaMon.id,
                MoTaMon.ten,
                MoTaMon.hinh,
                MoTaMon.gia,
                func.coalesce(func.sum(MonGhi.so_luong), 0).label('so_luong'),
                func.coalesce(func.sum(MonGhi.so_luong * MoTaMon.gia), 0).label('doanh_thu')
            )
            .join(MonGhi, MonGhi.mo_ta_mon_id == MoTaMon.id)
            .where(MonGhi.trang_thai == TrangThaiMonGhi.HOANTHANH)
            .where(cast(MonGhi.ngay_tao, Date) >= tu_ngay)
            .where(cast(MonGhi.ngay_tao, Date) <= den_ngay)
            .group_by(MoTaMon.id)
            .order_by(func.sum(MonGhi.so_luong).desc())
            .limit(limit)
        )
        results = session.execute(stmt).all()
        return [{
            'id': r.id,
            'ten': r.ten, 
            'hinh': r.hinh,
            'gia': r.gia,
            'so_luong': int(r.so_luong), 
            'doanh_thu': int(r.doanh_thu)
        } for r in results]

    def hieu_suat_nhan_vien(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        # Thống kê theo phục vụ đảm nhận phiên
        stmt = (
            select(
                PhucVu.nguoi_dung_id.label('id'),
                NguoiDung.ho_ten,
                func.count(PhienBan.id).label('so_phien'),
                func.coalesce(func.sum(DoanhThu.tien_cuoi_cung), 0).label('doanh_thu')
            )
            .select_from(PhucVu)
            .join(PhienBan, PhienBan.nguoi_dam_nhan_id == PhucVu.nguoi_dung_id)
            .outerjoin(DoanhThu, DoanhThu.phien_ban_id == PhienBan.id)
            .where(PhienBan.trang_thai == TrangThai.HOANTHANH)
            .where(cast(PhienBan.ngay_tao, Date) >= tu_ngay)
            .where(cast(PhienBan.ngay_tao, Date) <= den_ngay)
            .group_by(PhucVu.nguoi_dung_id, NguoiDung.ho_ten)
            .order_by(func.sum(DoanhThu.tien_cuoi_cung).desc())
        )
        results = session.execute(stmt).all()
        return [{
            'id': r.id,
            'ho_ten': r.ho_ten,
            'so_phien': r.so_phien,
            'doanh_thu': int(r.doanh_thu or 0)
        } for r in results]

    def thong_ke_theo_gio(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        stmt = (
            select(
                extract('hour', DoanhThu.ngay_tao).label('gio'),
                func.count(DoanhThu.id).label('so_don'),
                func.coalesce(func.sum(DoanhThu.tien_cuoi_cung), 0).label('doanh_thu')
            )
            .where(DoanhThu.trang_thai == TrangThaiDoanhThu.DAHOANTHANH)
            .where(cast(DoanhThu.ngay_tao, Date) >= tu_ngay)
            .where(cast(DoanhThu.ngay_tao, Date) <= den_ngay)
            .group_by(extract('hour', DoanhThu.ngay_tao))
            .order_by(extract('hour', DoanhThu.ngay_tao))
        )
        results = session.execute(stmt).all()
        return [{'gio': int(r.gio), 'so_don': r.so_don, 'doanh_thu': int(r.doanh_thu)} for r in results]

    def thong_ke_theo_nhom_mon(self, session: Session, tu_ngay, den_ngay) -> List[dict]:
        stmt = (
            select(
                NhomMon.id,
                NhomMon.ten,
                func.coalesce(func.sum(MonGhi.so_luong), 0).label('so_luong'),
                func.coalesce(func.sum(MonGhi.so_luong * MoTaMon.gia), 0).label('doanh_thu')
            )
            .join(MoTaMon, MoTaMon.nhom_mon_id == NhomMon.id)
            .join(MonGhi, MonGhi.mo_ta_mon_id == MoTaMon.id)
            .where(MonGhi.trang_thai == TrangThaiMonGhi.HOANTHANH)
            .where(cast(MonGhi.ngay_tao, Date) >= tu_ngay)
            .where(cast(MonGhi.ngay_tao, Date) <= den_ngay)
            .group_by(NhomMon.id, NhomMon.ten)
            .order_by(func.sum(MonGhi.so_luong).desc())
        )
        results = session.execute(stmt).all()
        return [{
            'id': r.id,
            'ten': r.ten,
            'so_luong': int(r.so_luong),
            'doanh_thu': int(r.doanh_thu)
        } for r in results]