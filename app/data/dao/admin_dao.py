# Admin DAO - Xử lý truy vấn DB cho các chức năng Admin
# Sử dụng SQLAlchemy Stmt cho performance
from sqlalchemy import select, func, and_
from typing import List, Optional
from flask_sqlalchemy.session import Session
from app.data.models import (
    TaiKhoan, NguoiDung, PhucVu, LeTan, DauBep, ThuNgan, QuanLy,
    KhuVuc, Ban, ThucDon, NhomMon, MoTaMon, NhomTuyChon, TuyChonMon,
    KhuyenMai, CauHinhThue, DoanhThuKhuyenMai,
    TrangThai, TrangThaiBan, TrangThaiTaiKhoan, PhanCong, PhienBan
)
from app.data.dao.interfaces.interfaces import (
    IAdminTaiKhoanDAO, IAdminNguoiDungDAO, IAdminKhuVucDAO, IAdminBanDAO,
    IAdminThucDonDAO, IAdminKhuyenMaiDAO, IAdminCauHinhThueDAO
)
from app.extentions.extentions import db


class AdminTaiKhoanDAO(IAdminTaiKhoanDAO):
    # Thao tác với bảng tài khoản
    
    def find_all(self, session: Session, page: int, per_page: int, filters: dict) -> tuple:
        stmt = select(TaiKhoan).order_by(TaiKhoan.ngay_tao.desc())
        
        if filters:
            if filters.get('trang_thai'):
                stmt = stmt.where(TaiKhoan.trang_thai == filters['trang_thai'])
            if filters.get('is_xac_thuc') is not None:
                stmt = stmt.where(TaiKhoan.is_xac_thuc == filters['is_xac_thuc'])
            if filters.get('search'):
                search = f"%{filters['search']}%"
                stmt = stmt.where(
                    (TaiKhoan.ten_tai_khoan.ilike(search)) | 
                    (TaiKhoan.email.ilike(search))
                )
        
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return list(pagination.items), pagination.total, pagination.has_next
    
    def find_by_id(self, session: Session, tai_khoan_id: int) -> Optional[TaiKhoan]:
        return session.get(TaiKhoan, ident=tai_khoan_id)
    
    def save(self, session: Session, tai_khoan: TaiKhoan) -> None:
        session.add(tai_khoan)
        session.flush()
    
    def delete(self, session: Session, tai_khoan: TaiKhoan) -> None:
        session.delete(tai_khoan)
        session.flush()
    
    def check_email_exists(self, session: Session, email: str, exclude_id: int = None) -> bool:
        stmt = select(func.count(TaiKhoan.id)).where(TaiKhoan.email == email)
        if exclude_id:
            stmt = stmt.where(TaiKhoan.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0
    
    def check_ten_tai_khoan_exists(self, session: Session, ten: str, exclude_id: int = None) -> bool:
        stmt = select(func.count(TaiKhoan.id)).where(TaiKhoan.ten_tai_khoan == ten)
        if exclude_id:
            stmt = stmt.where(TaiKhoan.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0

    def find_cho_xet_duyet(self, session: Session) -> List[TaiKhoan]:
        # Tìm các tài khoản đã xác thực email nhưng vai trò vẫn là VODANH
        from app.data.models import TenVaiTro, VaiTro
        stmt = (
            select(TaiKhoan)
            .join(VaiTro, TaiKhoan.vai_tro_id == VaiTro.id)
            .where(TaiKhoan.is_xac_thuc == True)
            .where(VaiTro.vai_tro == TenVaiTro.VODANH)
            .order_by(TaiKhoan.ngay_tao.desc())
        )
        return list(session.execute(stmt).scalars().all())


class AdminNguoiDungDAO(IAdminNguoiDungDAO):
    # Thao tác với thông tin nhân viên
    
    def find_all(self, session: Session, page: int, per_page: int, vai_tro: str = None) -> tuple:
        stmt = select(NguoiDung).order_by(NguoiDung.ngay_tao.desc())
        
        if vai_tro:
            stmt = stmt.where(NguoiDung.type == vai_tro)
        
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return list(pagination.items), pagination.total, pagination.has_next
    
    def find_by_id(self, session: Session, nguoi_dung_id: int) -> Optional[NguoiDung]:
        return session.get(NguoiDung, ident=nguoi_dung_id)
    
    def save(self, session: Session, nguoi_dung: NguoiDung) -> None:
        session.add(nguoi_dung)
        session.flush()
    
    def delete(self, session: Session, nguoi_dung: NguoiDung) -> None:
        session.delete(nguoi_dung)
        session.flush()
    
    def check_has_active_phien(self, session: Session, nguoi_dung_id: int) -> bool:
        # Đang có ca làm hoặc đang trong phiên bàn thì không cho đụng vào
        stmt = select(func.count(PhanCong.id)).where(
            and_(
                PhanCong.phuc_vu_id == nguoi_dung_id,
                PhanCong.trang_thai == TrangThai.MO
            )
        )
        count = session.execute(stmt).scalar()
        if count > 0:
            return True
        
        # Kiểm tra PhienBan đang active (với role LeTan)
        stmt = select(func.count(PhienBan.id)).where(
            and_(
                PhienBan.le_tan_id == nguoi_dung_id,
                PhienBan.trang_thai == TrangThai.MO
            )
        )
        count = session.execute(stmt).scalar()
        return count > 0

    def swap_nguoi_dung_subclass(self, session: Session, old_nguoi_dung: NguoiDung, new_nguoi_dung: NguoiDung) -> None:
        """Tráo đổi subclass: thêm model mới, xóa model cũ"""
        session.add(new_nguoi_dung)
        session.delete(old_nguoi_dung)
        session.flush()


class AdminKhuVucDAO(IAdminKhuVucDAO):
    # Quản lý mấy cái tầng, khu vực sân vườn...
    
    def find_all(self, session: Session) -> List[KhuVuc]:
        stmt = select(KhuVuc).order_by(KhuVuc.id)
        return list(session.execute(stmt).scalars().all())
    
    def find_by_id(self, session: Session, khu_vuc_id: int) -> Optional[KhuVuc]:
        return session.get(KhuVuc, ident=khu_vuc_id)
    
    def save(self, session: Session, khu_vuc: KhuVuc) -> None:
        session.add(khu_vuc)
        session.flush()
    
    def delete(self, session: Session, khu_vuc: KhuVuc) -> None:
        session.delete(khu_vuc)
        session.flush()
    
    def check_ten_exists(self, session: Session, ten: str, exclude_id: int = None) -> bool:
        stmt = select(func.count(KhuVuc.id)).where(KhuVuc.ten == ten)
        if exclude_id:
            stmt = stmt.where(KhuVuc.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0
    
    def count_ban(self, session: Session, khu_vuc_id: int) -> int:
        stmt = select(func.count(Ban.id)).where(Ban.khu_vuc_id == khu_vuc_id)
        return session.execute(stmt).scalar() or 0
    
    def count_nhan_vien(self, session: Session, khu_vuc_id: int) -> int:
        stmt = select(func.count(PhucVu.nguoi_dung_id)).where(PhucVu.khu_vuc_id == khu_vuc_id)
        return session.execute(stmt).scalar() or 0


class AdminBanDAO(IAdminBanDAO):
    # Thêm sửa xóa bàn ăn
    
    def find_all(self, session: Session, khu_vuc_id: int = None, trang_thai: str = None) -> List[Ban]:
        stmt = select(Ban).order_by(Ban.khu_vuc_id, Ban.id)
        
        if khu_vuc_id:
            stmt = stmt.where(Ban.khu_vuc_id == khu_vuc_id)
        if trang_thai:
            stmt = stmt.where(Ban.trang_thai == trang_thai)
        
        return list(session.execute(stmt).scalars().all())
    
    def find_by_id(self, session: Session, ban_id: int) -> Optional[Ban]:
        return session.get(Ban, ident=ban_id)
    
    def save(self, session: Session, ban: Ban) -> None:
        session.add(ban)
        session.flush()
    
    def delete(self, session: Session, ban: Ban) -> None:
        session.delete(ban)
        session.flush()

    def check_ten_exists(self, session: Session, ten: str, khu_vuc_id: int, exclude_id: int = None) -> bool:
        stmt = select(func.count(Ban.id)).where(
            and_(Ban.ten == ten, Ban.khu_vuc_id == khu_vuc_id)
        )
        if exclude_id:
            stmt = stmt.where(Ban.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0
    
    def check_has_active_phien(self, session: Session, ban_id: int) -> bool:
        stmt = select(func.count(PhanCong.id)).where(
            and_(
                PhanCong.ban_id == ban_id,
                PhanCong.trang_thai == TrangThai.MO
            )
        )
        count = session.execute(stmt).scalar()
        return count > 0


class AdminThucDonDAO(IAdminThucDonDAO):
    # Quản lý Menu, nhóm món, món ăn
    
    def find_thuc_don(self, session: Session) -> Optional[ThucDon]:
        stmt = select(ThucDon).limit(1)
        return session.execute(stmt).scalar()
    
    def find_all_nhom_mon(self, session: Session, thuc_don_id: int) -> List[NhomMon]:
        stmt = select(NhomMon).where(NhomMon.thuc_don_id == thuc_don_id).order_by(NhomMon.id)
        return list(session.execute(stmt).scalars().all())
    
    def find_nhom_mon_by_id(self, session: Session, nhom_mon_id: int) -> Optional[NhomMon]:
        return session.get(NhomMon, ident=nhom_mon_id)
    
    def save_nhom_mon(self, session: Session, nhom_mon: NhomMon) -> None:
        session.add(nhom_mon)
        session.flush()
    
    def delete_nhom_mon(self, session: Session, nhom_mon: NhomMon) -> None:
        session.delete(nhom_mon)
        session.flush()
    
    def find_all_mon(self, session: Session, nhom_mon_id: int = None) -> List[MoTaMon]:
        stmt = select(MoTaMon).order_by(MoTaMon.nhom_mon_id, MoTaMon.id)
        if nhom_mon_id:
            stmt = stmt.where(MoTaMon.nhom_mon_id == nhom_mon_id)
        return list(session.execute(stmt).scalars().all())
    
    def find_mon_by_id(self, session: Session, mon_id: int) -> Optional[MoTaMon]:
        return session.get(MoTaMon, ident=mon_id)
    
    def save_mon(self, session: Session, mon: MoTaMon) -> None:
        session.add(mon)
        session.flush()
    
    def check_ten_nhom_mon_exists(self, session: Session, ten: str, thuc_don_id: int, exclude_id: int = None) -> bool:
        stmt = select(func.count(NhomMon.id)).where(
            and_(NhomMon.ten == ten, NhomMon.thuc_don_id == thuc_don_id)
        )
        if exclude_id:
            stmt = stmt.where(NhomMon.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0
    
    def check_ten_mon_exists(self, session: Session, ten: str, exclude_id: int = None) -> bool:
        stmt = select(func.count(MoTaMon.id)).where(MoTaMon.ten == ten)
        if exclude_id:
            stmt = stmt.where(MoTaMon.id != exclude_id)
        count = session.execute(stmt).scalar()
        return count > 0
    
    def count_mon_in_nhom(self, session: Session, nhom_mon_id: int) -> int:
        stmt = select(func.count(MoTaMon.id)).where(MoTaMon.nhom_mon_id == nhom_mon_id)
        return session.execute(stmt).scalar() or 0


class AdminKhuyenMaiDAO(IAdminKhuyenMaiDAO):
    # Quản lý các mã giảm giá, chương trình KM
    
    def find_all(self, session: Session, hoat_dong: bool = None) -> List[KhuyenMai]:
        stmt = select(KhuyenMai).order_by(KhuyenMai.ngay_tao.desc())
        if hoat_dong is not None:
            stmt = stmt.where(KhuyenMai.hoat_dong == hoat_dong)
        return list(session.execute(stmt).scalars().all())
    
    def find_by_id(self, session: Session, khuyen_mai_id: int) -> Optional[KhuyenMai]:
        return session.get(KhuyenMai, ident=khuyen_mai_id)
    
    def save(self, session: Session, khuyen_mai: KhuyenMai) -> None:
        session.add(khuyen_mai)
        session.flush()
    
    def delete(self, session: Session, khuyen_mai: KhuyenMai) -> None:
        session.delete(khuyen_mai)
        session.flush()
    
    def check_has_doanhthu(self, session: Session, khuyen_mai_id: int) -> bool:
        stmt = select(func.count(DoanhThuKhuyenMai.doanh_thu_id)).where(
            DoanhThuKhuyenMai.khuyen_mai_id == khuyen_mai_id
        )
        count = session.execute(stmt).scalar()
        return count > 0


class AdminCauHinhThueDAO(IAdminCauHinhThueDAO):
    # Cấu hình VAT (thường là 8% hoặc 10%)
    
    def find_all(self, session: Session) -> List[CauHinhThue]:
        stmt = select(CauHinhThue).order_by(CauHinhThue.ngay_tao.desc())
        return list(session.execute(stmt).scalars().all())
    
    def find_by_id(self, session: Session, cau_hinh_id: int) -> Optional[CauHinhThue]:
        return session.get(CauHinhThue, ident=cau_hinh_id)
    
    def find_active(self, session: Session) -> Optional[CauHinhThue]:
        stmt = select(CauHinhThue).where(CauHinhThue.hoat_dong == True).limit(1)
        return session.execute(stmt).scalar()
    
    def save(self, session: Session, cau_hinh: CauHinhThue) -> None:
        session.add(cau_hinh)
        session.flush()
    
    def deactivate_all(self, session: Session) -> None:
        stmt = select(CauHinhThue).where(CauHinhThue.hoat_dong == True)
        configs = session.execute(stmt).scalars().all()
        for config in configs:
            config.hoat_dong = False
        session.flush()
