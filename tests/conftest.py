"""
Pytest configuration and fixtures
"""
import pytest
from datetime import datetime, timedelta
from app.data.models import (
    VaiTro, TaiKhoan, NguoiDung, PhucVu, LeTan,
    KhuVuc, Ban, KhungGio, PhienBan, PhanCong,
    TenVaiTro, TrangThaiTaiKhoan, TrangThaiBan, TrangThai
)


# ==================== Sample Data Fixtures ====================

@pytest.fixture
def sample_vai_tro_data():
    """Valid VaiTro data for testing"""
    return {
        "vai_tro": "admin"
    }


@pytest.fixture
def sample_tai_khoan_data():
    """Valid TaiKhoan data for testing"""
    return {
        "ten_tai_khoan": "user123",
        "mat_khau": "password123",
        "vai_tro_id": 1,
        "trang_thai": "mo"
    }


@pytest.fixture
def sample_login_data():
    """Valid login data"""
    return {
        "ten_tai_khoan": "user123",
        "mat_khau": "password123"
    }


@pytest.fixture
def sample_nguoi_dung_data():
    """Valid NguoiDung data for testing"""
    return {
        "ho_ten": "Nguyễn Văn A",
        "tai_khoan_id": 1
    }


@pytest.fixture
def sample_phuc_vu_data():
    """Valid PhucVu data for testing"""
    return {
        "ho_ten": "Nguyễn Văn B",
        "tai_khoan_id": 2,
        "is_nhom_truong": True,
        "khu_vuc_id": 1
    }


@pytest.fixture
def sample_le_tan_data():
    """Valid LeTan data for testing"""
    return {
        "ho_ten": "Trần Thị C",
        "tai_khoan_id": 3
    }


@pytest.fixture
def sample_khu_vuc_data():
    """Valid KhuVuc data for testing"""
    return {
        "ten": "Tầng 1",
        "nhom_truong_id": None
    }


@pytest.fixture
def sample_ban_data():
    """Valid Ban data for testing"""
    return {
        "ten": "Bàn 1",
        "so_ghe": 4,
        "khu_vuc_id": 1,
        "trang_thai": "trong"
    }


@pytest.fixture
def sample_khung_gio_data():
    """Valid KhungGio data for testing"""
    now = datetime.now()
    return {
        "tg_bat_dau": now.isoformat(),
        "tg_ket_thuc_du_kien": (now + timedelta(minutes=30)).isoformat(),
        "phien_ban_id": 1,
        "trang_thai": "mo"
    }


@pytest.fixture
def sample_phien_ban_data():
    """Valid PhienBan data for testing"""
    return {
        "le_tan_id": 1,
        "trang_thai": "mo",
        "tg_bat_dau": datetime.now().isoformat()
    }


@pytest.fixture
def sample_phan_cong_data():
    """Valid PhanCong data for testing"""
    return {
        "phuc_vu_id": 1,
        "ban_id": 1,
        "phien_ban_id": 1,
        "trang_thai": "mo"
    }


# ==================== Mock Model Fixtures ====================

@pytest.fixture
def mock_vai_tro():
    """Mock VaiTro model instance"""
    vai_tro = VaiTro()
    vai_tro.id = 1
    vai_tro.vai_tro = TenVaiTro.ADMIN  # Use enum
    vai_tro.ngay_tao = datetime.now()
    vai_tro.ngay_sua_doi = None
    return vai_tro


@pytest.fixture
def mock_tai_khoan(mock_vai_tro):
    """Mock TaiKhoan model instance"""
    tai_khoan = TaiKhoan()
    tai_khoan.id = 1
    tai_khoan.ten_tai_khoan = "user123"
    tai_khoan.mat_khau = "hashed_password"
    tai_khoan.trang_thai = TrangThaiTaiKhoan.MO  # Use enum
    tai_khoan.vai_tro_id = 1
    tai_khoan.vai_tro = mock_vai_tro
    tai_khoan.ngay_tao = datetime.now()
    tai_khoan.ngay_sua_doi = None
    return tai_khoan


@pytest.fixture
def mock_nguoi_dung(mock_tai_khoan):
    """Mock NguoiDung model instance"""
    nguoi_dung = NguoiDung()
    nguoi_dung.id = 1
    nguoi_dung.ho_ten = "Nguyễn Văn A"
    nguoi_dung.type = "nguoi_dung"
    nguoi_dung.tai_khoan_id = 1
    nguoi_dung.tai_khoan = mock_tai_khoan
    nguoi_dung.ngay_tao = datetime.now()
    nguoi_dung.ngay_sua_doi = None
    return nguoi_dung


@pytest.fixture
def mock_khu_vuc():
    """Mock KhuVuc model instance"""
    khu_vuc = KhuVuc()
    khu_vuc.id = 1
    khu_vuc.ten = "Tầng 1"
    khu_vuc.nhom_truong_id = None
    khu_vuc.nhom_truong = None
    khu_vuc.ds_ban = []
    khu_vuc.ngay_tao = datetime.now()
    khu_vuc.ngay_sua_doi = None
    return khu_vuc


@pytest.fixture
def mock_phuc_vu(mock_tai_khoan, mock_khu_vuc):
    """Mock PhucVu model instance"""
    phuc_vu = PhucVu()
    phuc_vu.id = 1
    phuc_vu.nguoi_dung_id = 1
    phuc_vu.ho_ten = "Nguyễn Văn B"
    phuc_vu.type = "phuc_vu"
    phuc_vu.is_nhom_truong = True
    phuc_vu.tai_khoan_id = 2
    phuc_vu.tai_khoan = mock_tai_khoan
    phuc_vu.khu_vuc_id = 1
    phuc_vu.khu_vuc = mock_khu_vuc
    phuc_vu.ds_phan_cong_hien_tai = []
    phuc_vu.ngay_tao = datetime.now()
    phuc_vu.ngay_sua_doi = None
    return phuc_vu


@pytest.fixture
def mock_ban(mock_khu_vuc):
    """Mock Ban model instance"""
    ban = Ban()
    ban.id = 1
    ban.ten = "Bàn 1"
    ban.so_ghe = 4
    ban.trang_thai = TrangThaiBan.TRONG  # Use enum
    ban.khu_vuc_id = 1
    ban.ds_khung_gio = []
    ban.ngay_tao = datetime.now()
    ban.ngay_sua_doi = None
    return ban

