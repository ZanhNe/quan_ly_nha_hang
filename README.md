# Hệ Thống Quản Lý Nhà Hàng

## Team Members

| Họ Tên  | Mã Số Sinh Viên |
| ------------- |:-------------:|
| **Diệp Bảo Doanh**      | **2251050018**     |
| **Nguyễn Cao Phú**      | **2251012111**    |

## Tổng Quan

Đây là hệ thống quản lý nhà hàng được xây dựng bằng Flask framework, áp dụng kiến trúc 3-Tier với Dependency Injection pattern, phục vụ cho bài tập lớn môn học.

## Công Nghệ Sử Dụng

### Core Framework
- **Flask 3.1.2** - Web framework chính
- **Python 3.14** - Ngôn ngữ lập trình

### Database & ORM
- **SQLAlchemy 2.0.44** - ORM (Object-Relational Mapping)
- **Flask-SQLAlchemy 3.1.1** - SQLAlchemy integration cho Flask
- **PyMySQL 1.1.2** - MySQL database connector
- **Alembic 1.17.1** - Database migration tool
- **Flask-Migrate 4.1.0** - Alembic wrapper cho Flask

### Authentication & Security
- **itsdangerous 2.2.0** - Cryptographic signing
- **Werkzeug 3.1.3** - WSGI utilities và security helpers

### Serialization & Validation
- **Marshmallow 4.0.1** - Object serialization/deserialization
- **Flask-Marshmallow 1.3.0** - Flask integration cho Marshmallow
- **WTForms 3.2.1** - Form validation và rendering

### Admin Panel
- **Flask-Admin 2.0.0** - Admin interface tự động

### Real-time Communication
- **Flask-SocketIO 5.5.1** - WebSocket support cho Flask
- **python-socketio 5.14.3** - Socket.IO server implementation
- **python-engineio 4.12.3** - Engine.IO server
- **simple-websocket 1.1.0** - WebSocket server và client
- **wsproto 1.2.0** - WebSocket protocol implementation
- **h11 0.16.0** - HTTP/1.1 protocol implementation

### Dependency Injection
- **injector 0.22.0** - Dependency injection framework

### API & CORS
- **flask-cors 6.0.1** - Cross-Origin Resource Sharing support

### Utilities
- **python-dotenv 1.2.1** - Environment variables management
- **click 8.3.0** - Command-line interface creation
- **Jinja2 3.1.6** - Template engine
- **Mako 1.3.10** - Template library (dùng bởi Alembic)
- **blinker 1.9.0** - Signal/event dispatching
- **colorama 0.4.6** - Terminal colored output (Windows support)
- **bidict 0.23.1** - Bidirectional mapping
- **greenlet 3.2.4** - Lightweight concurrent programming
- **MarkupSafe 3.0.3** - Safe string handling
- **typing_extensions 4.15.0** - Backported type hints

## Kiến Trúc Hệ Thống

Project áp dụng **Clean Architecture** với cấu trúc phân tầng rõ ràng:

```
BTL/
├── app/                          # Application core
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   │
│   ├── data/                    # Data Layer (Infrastructure)
│   │   ├── dao/                 # Data Access Objects
│   │   │   └── interfaces/      # DAO interfaces
│   │   └── models.py            # Database models (SQLAlchemy)
│   │
│   ├── domain/                  # Domain Layer (Business Logic)
│   │   └── services/            # Business services
│   │       ├── interfaces/      # Service interfaces
│   │       └── test.py          # Service implementations
│   │
│   ├── presentation/            # Presentation Layer
│   │   └── web/                 # Web interface
│   │       ├── routes/          # Flask blueprints & routes
│   │       │   └── test.py
│   │       ├── static/          # Static files (CSS, JS, images)
│   │       └── templates/       # Jinja2 HTML templates
│   │           └── test.html
│   │
│   ├── api/                     # RESTful API endpoints (dự kiến)
│   ├── socket/                  # WebSocket handlers (dự kiến)
│   │
│   ├── container/               # Dependency Injection
│   │   └── container.py         # DI container configuration
│   │
│   ├── schemas/                 # Data Transfer Objects (DTOs)
│   │   └── schema.py            # Marshmallow schemas
│   │
│   ├── extentions/              # Flask extensions
│   │   └── extentions.py        # Instance library
│   │
│   └── utils/                   # Utility functions & helpers
│
├── tests/                       # Test suites
├── entry.py                     # Application entry point
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── venv/                        # Virtual environment
```

### Giải Thích Các Tầng

#### 1. **Data Layer** (`app/data/`)
- **Trách nhiệm**: Quản lý truy xuất dữ liệu, database operations
- **Thành phần**:
  - `models.py`: SQLAlchemy models định nghĩa database schema
  - `dao/`: Data Access Objects - abstraction layer cho database queries
  - `dao/interfaces/`: Interfaces cho DAOs (Dependency Inversion Principle)

#### 2. **Domain Layer** (`app/domain/`)
- **Trách nhiệm**: Business logic, domain rules, use cases
- **Thành phần**:
  - `services/`: Business services chứa application logic
  - `services/interfaces/`: Service interfaces (Dependency Inversion Principle)
- **Nguyên tắc**: Không phụ thuộc vào framework hay infrastructure

#### 3. **Presentation Layer** (`app/presentation/`)
- **Trách nhiệm**: User interface, request/response handling
- **Thành phần**:
  - `web/routes/`: Flask blueprints định nghĩa HTTP endpoints
  - `web/templates/`: Jinja2 templates cho server-side rendering
  - `web/static/`: Static assets (CSS, JavaScript, images)

#### 4. **API Layer** (`app/api/`)
- **Trách nhiệm**: RESTful API endpoints cho mobile/external clients

#### 5. **Socket Layer** (`app/socket/`)
- **Trách nhiệm**: Real-time communication qua WebSocket (đặt bàn, cập nhật đơn hàng)

#### 6. **Dependency Injection** (`app/container/`)
- **Trách nhiệm**: Quản lý dependencies, loosely coupled components
- **Framework**: `injector` - Python dependency injection framework

#### 7. **Schemas** (`app/schemas/`)
- **Trách nhiệm**: Data validation, serialization/deserialization
- **Framework**: Marshmallow schemas (DTOs pattern)

#### 8. **Extensions** (`app/extentions/`)
- **Trách nhiệm**: Khởi tạo và cấu hình Flask extensions
- **Hiện có**:
  - `db`: SQLAlchemy instance
  - `ma`: Marshmallow instance
  - `Base`: SQLAlchemy DeclarativeBase

## Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.14+
- MySQL/MariaDB database
- pip package manager

### Các Bước Cài Đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd BTL
```

2. **Tạo virtual environment**
```bash
python -m venv venv
```

3. **Kích hoạt virtual environment**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
.\venv\Scripts\activate.bat
```

Linux/macOS:
```bash
source venv/bin/activate
```

4. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

5. **Cấu hình environment variables**

Tạo file `.env` trong thư mục root:
```env
# Flask Configuration
FLASK_APP=entry.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/restaurant_db
SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost:3306/restaurant_db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# SocketIO Configuration
SOCKETIO_MESSAGE_QUEUE=redis://localhost:6379/0  # Optional
```

6. **Khởi tạo database**
```bash
# Tạo database trong MySQL
mysql -u root -p
CREATE DATABASE restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Chạy migrations
flask db init     # Lần đầu tiên
flask db migrate -m "Initial migration"
flask db upgrade
```

## Chạy Ứng Dụng

### Development Mode
```bash
python entry.py
```

Hoặc dùng Flask CLI:
```bash
flask run
```

Application sẽ chạy tại: `http://127.0.0.1:5000`

### Production Mode
Sử dụng WSGI server như Gunicorn hoặc uWSGI:

```bash
# Cài đặt Gunicorn
pip install gunicorn

# Chạy với Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## Database Migration

### Tạo Migration Mới
```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations
```bash
flask db upgrade
```

### Rollback Migration
```bash
flask db downgrade
```

### Xem Lịch Sử Migration
```bash
flask db history
```

## Cấu Trúc Database

### Entity Relationship Overview

Hệ thống database được thiết kế với các bảng chính sau:

#### 1. **Vai Trò (vai_tro)**
Quản lý các vai trò trong hệ thống nhà hàng.

**Columns:**
- `id` (PK) - ID vai trò
- `vai_tro` (Enum) - Loại vai trò: admin, quanly, thungan, letan, phucvu
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Schemas:**
- `VaiTroCreateSchema` - Tạo vai trò mới
- `VaiTroUpdateSchema` - Cập nhật vai trò
- `VaiTroOutSchema` - Trả về thông tin vai trò

---

#### 2. **Tài Khoản (tai_khoan)**
Quản lý thông tin đăng nhập của người dùng.

**Columns:**
- `id` (PK) - ID tài khoản
- `ten_tai_khoan` (Unique) - Tên đăng nhập (5-500 ký tự)
- `mat_khau` - Mật khẩu đã hash (min 8 ký tự)
- `trang_thai` (Enum) - Trạng thái: mo (mở), khoa (khóa)
- `vai_tro_id` (FK) - Liên kết với bảng vai_tro
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `VaiTro`

**Schemas:**
- `TaiKhoanCreateSchema` - Tạo tài khoản mới (bao gồm mật khẩu)
- `TaiKhoanUpdateSchema` - Cập nhật tài khoản
- `TaiKhoanLoginSchema` - Schema cho đăng nhập
- `TaiKhoanOutSchema` - Trả về thông tin (không bao gồm mật khẩu)

---

#### 3. **Người Dùng (nguoi_dung)** - Base Class
Lớp cơ sở chứa thông tin chung của người dùng trong hệ thống.

**Columns:**
- `id` (PK) - ID người dùng
- `ho_ten` - Họ tên (2-255 ký tự)
- `type` - Discriminator cho Polymorphic (phuc_vu, le_tan)
- `tai_khoan_id` (FK) - Liên kết với bảng tai_khoan
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Inheritance:**
- `PhucVu` - Nhân viên phục vụ
- `LeTan` - Nhân viên lễ tân

**Relationships:**
- Many-to-One với `TaiKhoan`

**Schemas:**
- `NguoiDungCreateSchema` - Tạo người dùng
- `NguoiDungUpdateSchema` - Cập nhật người dùng
- `NguoiDungOutSchema` - Trả về thông tin người dùng

---

#### 4. **Phục Vụ (phuc_vu)** - Extends NguoiDung
Quản lý thông tin nhân viên phục vụ.

**Additional Columns:**
- `nguoi_dung_id` (PK, FK) - Liên kết với nguoi_dung
- `is_nhom_truong` (Boolean) - Có phải nhóm trưởng không
- `khu_vuc_id` (FK) - Khu vực được phân công

**Relationships:**
- Inherits from `NguoiDung`
- Many-to-One với `KhuVuc`
- One-to-Many với `PhanCong`

**Computed Properties:**
- `so_ban_dang_phuc_vu` - Số bàn hiện đang phục vụ

**Schemas:**
- `PhucVuCreateSchema` - Tạo nhân viên phục vụ
- `PhucVuUpdateSchema` - Cập nhật thông tin
- `PhucVuOutSchema` - Trả về thông tin (bao gồm số bàn đang phục vụ)

---

#### 5. **Lễ Tân (le_tan)** - Extends NguoiDung
Quản lý thông tin nhân viên lễ tân.

**Additional Columns:**
- `nguoi_dung_id` (PK, FK) - Liên kết với nguoi_dung

**Relationships:**
- Inherits from `NguoiDung`
- One-to-Many với `PhienBan`

**Business Methods:**
- `tao_phien()` - Tạo phiên bàn mới

**Schemas:**
- `LeTanCreateSchema` - Tạo lễ tân
- `LeTanUpdateSchema` - Cập nhật thông tin
- `LeTanOutSchema` - Trả về thông tin

---

#### 6. **Khu Vực (khu_vuc)**
Quản lý các khu vực trong nhà hàng (VD: tầng 1, tầng 2, khu VIP).

**Columns:**
- `id` (PK) - ID khu vực
- `ten` - Tên khu vực (2-100 ký tự)
- `nhom_truong_id` (FK, nullable) - Nhóm trưởng phụ trách
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `PhucVu` (nhóm trưởng)
- One-to-Many với `Ban`

**Schemas:**
- `KhuVucCreateSchema` - Tạo khu vực
- `KhuVucUpdateSchema` - Cập nhật khu vực
- `KhuVucOutSchema` - Trả về thông tin cơ bản
- `KhuVucDetailOutSchema` - Trả về thông tin chi tiết (bao gồm danh sách bàn)

---

#### 7. **Bàn (ban)**
Quản lý thông tin các bàn ăn.

**Columns:**
- `id` (PK) - ID bàn
- `ten` - Tên/số bàn (1-100 ký tự)
- `so_ghe` - Số ghế (1-50)
- `trang_thai` (Enum) - Trạng thái: trong, cokhach, giucho
- `khu_vuc_id` (FK) - Thuộc khu vực nào
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `KhuVuc`
- Many-to-Many với `KhungGio` (qua bảng trung gian `ban_khunggio`)

**Business Methods:**
- `them_khung_gio()` - Thêm khung giờ cho bàn
- `kiem_tra_thoi_gian_hop_le()` - Kiểm tra thời gian có bị trùng không
- `kiem_tra_ban_trong()` - Kiểm tra bàn có trống không

**Schemas:**
- `BanCreateSchema` - Tạo bàn mới (validate số ghế 1-50)
- `BanUpdateSchema` - Cập nhật thông tin bàn
- `BanOutSchema` - Trả về thông tin bàn

---

#### 8. **Khung Giờ (khung_gio)**
Quản lý khoảng thời gian sử dụng của bàn.

**Columns:**
- `id` (PK) - ID khung giờ
- `tg_bat_dau` (DateTime) - Thời gian bắt đầu
- `tg_ket_thuc_du_kien` (DateTime) - Thời gian kết thúc dự kiến
- `trang_thai` (Enum) - Trạng thái: mo (mở), dong (đóng)
- `phien_ban_id` (FK) - Thuộc phiên bàn nào
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `PhienBan`
- Many-to-Many với `Ban`

**Validation:**
- Thời gian kết thúc phải sau thời gian bắt đầu

**Schemas:**
- `KhungGioCreateSchema` - Tạo khung giờ (validate thời gian)
- `KhungGioUpdateSchema` - Cập nhật khung giờ
- `KhungGioOutSchema` - Trả về thông tin khung giờ

---

#### 9. **Phiên Bàn (phien_ban)**
Quản lý phiên làm việc của lễ tân (quản lý bàn theo ca).

**Columns:**
- `id` (PK) - ID phiên
- `trang_thai` (Enum) - Trạng thái: mo, dong
- `le_tan_id` (FK) - Lễ tân phụ trách
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `LeTan`
- One-to-One với `KhungGio`
- One-to-Many với `PhanCong`

**Business Methods:**
- `phan_cong()` - Phân công phục vụ cho bàn
- `tao_khung_gio()` - Tạo khung giờ cho phiên (mặc định 30 phút)

**Schemas:**
- `PhienBanCreateSchema` - Tạo phiên bàn (có thể bao gồm thời gian bắt đầu)
- `PhienBanUpdateSchema` - Cập nhật phiên bàn
- `PhienBanOutSchema` - Trả về thông tin cơ bản
- `PhienBanDetailOutSchema` - Trả về thông tin chi tiết (bao gồm tất cả phân công)

---

#### 10. **Phân Công (phan_cong)**
Quản lý việc phân công nhân viên phục vụ cho bàn trong từng phiên.

**Columns:**
- `id` (PK) - ID phân công
- `trang_thai` (Enum) - Trạng thái: mo, dong
- `phuc_vu_id` (FK) - Nhân viên được phân công
- `ban_id` (FK) - Bàn được phân công
- `phien_ban_id` (FK) - Thuộc phiên nào
- `ngay_tao` - Thời gian tạo
- `ngay_sua_doi` - Thời gian cập nhật

**Relationships:**
- Many-to-One với `PhucVu`
- Many-to-One với `Ban`
- Many-to-One với `PhienBan`

**Schemas:**
- `PhanCongCreateSchema` - Tạo phân công mới
- `PhanCongUpdateSchema` - Cập nhật phân công
- `PhanCongOutSchema` - Trả về thông tin cơ bản (chỉ IDs)
- `PhanCongDetailOutSchema` - Trả về thông tin chi tiết (bao gồm thông tin phục vụ và bàn)

---

### Database Diagram (ERD)

```
┌─────────────┐
│   VaiTro    │
│─────────────│
│ id (PK)     │
│ vai_tro     │──┐
└─────────────┘  │
                 │
                 │ 1:N
                 ↓
┌─────────────┐  │   ┌──────────────┐
│  TaiKhoan   │←─┘   │  NguoiDung   │
│─────────────│      │──────────────│
│ id (PK)     │──┐   │ id (PK)      │
│ ten_tai_khoan│ │   │ ho_ten       │
│ mat_khau    │  │   │ type         │
│ trang_thai  │  │   │ tai_khoan_id │←─┐
│ vai_tro_id  │  │   └──────────────┘  │
└─────────────┘  │          ↑          │ 1:N
                 │ 1:N      │          │
                 └──────────┘          │
                            │          │
              ┌─────────────┴────────────┐
              │                          │
     ┌────────▼────────┐      ┌─────────▼────────┐
     │     PhucVu      │      │      LeTan       │
     │─────────────────│      │──────────────────│
     │ nguoi_dung_id   │      │ nguoi_dung_id    │
     │ is_nhom_truong  │      └─────────┬────────┘
     │ khu_vuc_id      │                │
     └────────┬────────┘                │ 1:N
              │                         ↓
              │ N:1          ┌──────────────────┐
              ↓              │    PhienBan      │
     ┌────────────────┐      │──────────────────│
     │    KhuVuc      │      │ id (PK)          │
     │────────────────│      │ trang_thai       │
     │ id (PK)        │      │ le_tan_id (FK)   │
     │ ten            │      └─────────┬────────┘
     │ nhom_truong_id │                │ 1:1
     └────────┬───────┘                ↓
              │ 1:N          ┌──────────────────┐
              ↓              │    KhungGio      │
     ┌────────────────┐      │──────────────────│
     │      Ban       │      │ id (PK)          │
     │────────────────│◆─────│ tg_bat_dau       │
     │ id (PK)        │ N:M  │ tg_ket_thuc_dk   │
     │ ten            │      │ trang_thai       │
     │ so_ghe         │      │ phien_ban_id     │
     │ trang_thai     │      └──────────────────┘
     │ khu_vuc_id     │
     └────────┬───────┘
              │
              │ N:1
              ↓
     ┌────────────────┐
     │   PhanCong     │
     │────────────────│
     │ id (PK)        │
     │ trang_thai     │
     │ phuc_vu_id (FK)│←──────┐
     │ ban_id (FK)    │       │
     │ phien_ban_id   │       │
     └────────────────┘       │
              ↑               │
              └───────────────┘
```

### Enums Sử Dụng

```python
# Trạng thái tài khoản
class TrangThaiTaiKhoan(Enum):
    MO = 'mo'          # Tài khoản đang hoạt động
    KHOA = 'khoa'      # Tài khoản bị khóa

# Trạng thái bàn
class TrangThaiBan(Enum):
    TRONG = 'trong'     # Bàn trống
    COKHACH = 'cokhach' # Có khách đang ngồi
    GIUCHO = 'giucho'   # Đã được đặt trước

# Trạng thái chung (phiên, khung giờ, phân công)
class TrangThai(Enum):
    MO = 'mo'          # Đang mở/hoạt động
    DONG = 'dong'      # Đã đóng/hoàn thành

# Các vai trò trong hệ thống
class TenVaiTro(Enum):
    ADMIN = 'admin'      # Quản trị viên
    QUANLY = 'quanly'    # Quản lý
    THUNGAN = 'thungan'  # Thu ngân
    LETAN = 'letan'      # Lễ tân
    PHUCVU = 'phucvu'    # Phục vụ
```

### Schema Design Patterns

#### Input Schemas (Create/Update)
- **CreateSchema**: Validate dữ liệu đầu vào khi tạo mới, tất cả trường required
- **UpdateSchema**: Validate dữ liệu khi cập nhật, các trường optional
- **LoginSchema**: Schema đặc biệt cho authentication

#### Output Schemas
- **OutSchema**: Trả về thông tin cơ bản, không bao gồm sensitive data (password)
- **DetailOutSchema**: Trả về thông tin chi tiết với nested relationships

#### Validation Rules
- Độ dài string: min/max length
- Số nguyên: range validation
- Enum: OneOf validation
- DateTime: format validation, business logic validation
- Security: exclude password trong output schemas



## Testing

### Cài Đặt Testing Dependencies

Testing dependencies đã được include trong `requirements.txt`:
- `pytest==8.3.4` - Testing framework
- `pytest-cov==6.0.0` - Coverage plugin
- `pytest-flask==1.3.0` - Flask testing utilities

Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### Cấu Trúc Test

```
tests/
├── __init__.py              # Test package
├── conftest.py              # Pytest fixtures và configuration
├── test_schemas.py          # Schema validation tests (✅ READY)
├── test_dao.py              # DAO layer tests (TODO)
├── test_services.py         # Service layer tests (TODO)
└── test_routes.py           # Route/API tests (TODO)
```

### Chạy Tests

#### Chạy Tất Cả Tests
```bash
pytest
```

#### Chạy Tests Với Coverage Report
```bash
# Basic coverage
pytest --cov=app

# Coverage với HTML report
pytest --cov=app --cov-report=html

# Coverage với missing lines
pytest --cov=app --cov-report=term-missing
```

#### Chạy Test File Cụ Thể
```bash
# Test schemas
pytest tests/test_schemas.py

# Test với verbose output
pytest tests/test_schemas.py -v

# Test với extra verbose (show each test)
pytest tests/test_schemas.py -vv
```

#### Chạy Test Class Cụ Thể
```bash
pytest tests/test_schemas.py::TestTaiKhoanSchemas
```

#### Chạy Test Function Cụ Thể
```bash
pytest tests/test_schemas.py::TestTaiKhoanSchemas::test_tai_khoan_create_valid
```

#### Chạy Tests Theo Pattern
```bash
# Chạy tất cả tests có "validation" trong tên
pytest -k "validation"

# Chạy tất cả tests của TaiKhoan
pytest -k "TaiKhoan"
```

#### Chạy Tests Với Markers
```bash
# Chỉ chạy unit tests
pytest -m unit

# Chỉ chạy integration tests
pytest -m integration

# Bỏ qua slow tests
pytest -m "not slow"
```

### Test Coverage Status

#### ✅ Schema Validation Tests (100% Complete)

**File:** `tests/test_schemas.py` (600+ dòng code, 80+ test cases)

| Schema Category | Test Classes | Test Cases | Status |
|----------------|--------------|------------|--------|
| **VaiTro** | `TestVaiTroSchemas` | 5 tests | ✅ |
| **TaiKhoan** | `TestTaiKhoanSchemas` | 11 tests | ✅ |
| **NguoiDung** | `TestNguoiDungSchemas` | 6 tests | ✅ |
| **PhucVu** | `TestPhucVuSchemas` | 4 tests | ✅ |
| **LeTan** | `TestLeTanSchemas` | 3 tests | ✅ |
| **KhuVuc** | `TestKhuVucSchemas` | 5 tests | ✅ |
| **Ban** | `TestBanSchemas` | 7 tests | ✅ |
| **KhungGio** | `TestKhungGioSchemas` | 4 tests | ✅ |
| **PhienBan** | `TestPhienBanSchemas` | 4 tests | ✅ |
| **PhanCong** | `TestPhanCongSchemas` | 3 tests | ✅ |
| **Edge Cases** | `TestSchemaEdgeCases` | 8 tests | ✅ |
| **List Serialization** | `TestSchemaListSerialization` | 2 tests | ✅ |
| **Default Values** | `TestSchemaDefaultValues` | 3 tests | ✅ |
| **Performance** | `TestSchemaPerformance` | 2 tests | ✅ |

**Total:** 67 test cases covering all schemas

#### Test Coverage Details

**Valid Input Tests:**
- ✅ All CreateSchema với valid data
- ✅ All UpdateSchema với partial data  
- ✅ All OutSchema serialization
- ✅ Default values cho optional fields
- ✅ Nested relationships

**Validation Error Tests:**
- ✅ Required fields missing
- ✅ String length validation (min/max)
- ✅ Number range validation (1-50 cho số ghế)
- ✅ Enum validation (vai trò, trạng thái)
- ✅ DateTime format validation
- ✅ Unknown fields rejection
- ✅ Multiple validation errors
- ✅ Empty string rejection
- ✅ Null values cho nullable fields

**Security Tests:**
- ✅ Password exclusion trong TaiKhoanOutSchema
- ✅ Sensitive data không được serialize

**Performance Tests:**
- ✅ Serialize 1000+ objects
- ✅ Validate 1000+ inputs

### Test Examples

#### Example 1: Chạy Schema Tests
```bash
# Windows PowerShell
cd D:\flask\BTL
.\venv\Scripts\Activate.ps1
pytest tests/test_schemas.py -v

# Expected output:
# tests/test_schemas.py::TestVaiTroSchemas::test_vai_tro_create_valid PASSED
# tests/test_schemas.py::TestVaiTroSchemas::test_vai_tro_create_invalid_role PASSED
# ...
# ======================== 67 passed in 2.50s =========================
```

#### Example 2: Chạy Với Coverage
```bash
pytest tests/test_schemas.py --cov=app.schemas --cov-report=term-missing

# Expected output:
# Name                      Stmts   Miss  Cover   Missing
# -------------------------------------------------------
# app/schemas/__init__.py       0      0   100%
# app/schemas/schema.py       250      0   100%
# -------------------------------------------------------
# TOTAL                       250      0   100%
```

#### Example 3: Debug Failed Test
```bash
# Chạy với pdb debugger khi fail
pytest tests/test_schemas.py --pdb

# Chạy với full traceback
pytest tests/test_schemas.py --tb=long

# Chạy với print statements visible
pytest tests/test_schemas.py -s
```

### Continuous Integration

Để tích hợp với CI/CD pipeline (GitHub Actions, GitLab CI, etc.):

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Writing New Tests

Template cho test mới:

```python
# tests/test_example.py
import pytest
from marshmallow import ValidationError
from app.schemas.schema import ExampleSchema

class TestExampleSchema:
    """Test ExampleSchema"""
    
    def test_example_valid(self):
        """Test with valid data"""
        schema = ExampleSchema()
        data = {"field": "value"}
        result = schema.load(data)
        assert result['field'] == 'value'
    
    def test_example_invalid(self):
        """Test with invalid data"""
        schema = ExampleSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"field": "invalid"})
        assert 'field' in exc_info.value.messages
```

### Troubleshooting Tests

#### Import Errors
```
ImportError: No module named 'app'
```
**Solution:** Đảm bảo bạn chạy pytest từ root directory (D:\flask\BTL)

#### Database Errors
```
sqlalchemy.exc.OperationalError
```
**Solution:** Schema tests không cần database. Nếu gặp lỗi này, kiểm tra imports.

#### Fixture Not Found
```
fixture 'sample_data' not found
```
**Solution:** Fixtures được định nghĩa trong `tests/conftest.py`. Đảm bảo file này tồn tại.

## API Endpoints

### Web Routes
- `GET /test` - Test endpoint (hiển thị test.html)

*(Các endpoints khác sẽ được bổ sung khi phát triển)*

### RESTful API
*(Dự kiến - chưa implement)*

### WebSocket Events
*(Dự kiến - chưa implement)*


## Admin Panel

Truy cập admin panel tại: `http://127.0.0.1:5000/admin`

Flask-Admin cung cấp giao diện quản trị tự động cho:
*(Dự kiến - chưa implement)*

## Design Patterns Được Sử Dụng

1. **3-Tier** - Phân tầng rõ ràng, độc lập framework
2. **Dependency Injection** - Loose coupling, dễ test
3. **Repository Pattern** - DAOs abstract database access
4. **Service Pattern** - Business logic encapsulation
5. **Factory Pattern** - Application factory (`create_app()`)
6. **Blueprint Pattern** - Modular Flask routes
7. **DTO Pattern** - Marshmallow schemas cho data transfer

## Best Practices

### Code Organization
- Mỗi layer có trách nhiệm rõ ràng (Separation of Concerns)
- Dependency Inversion Principle - depend on abstractions
- Single Responsibility Principle - mỗi class một nhiệm vụ

### Database
- Sử dụng migrations cho mọi thay đổi schema
- Indexes cho foreign keys và frequent queries
- Soft delete thay vì hard delete (khi cần)

### Security
- Không commit file `.env` vào Git
- Hash passwords
- Validate và sanitize tất cả inputs
- Sử dụng CSRF protection
- Rate limiting cho API endpoints

### Performance
- Database connection pooling
- Query optimization với SQLAlchemy
- Caching với Redis (nếu cần)
- Lazy loading cho relationships

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```
**Giải pháp**: Kiểm tra MySQL service đang chạy và credentials trong `.env` đúng

### Import Error
```
ImportError: No module named 'flask'
```
**Giải pháp**: Đảm bảo virtual environment đã được activate và `pip install -r requirements.txt` đã chạy

### Migration Error
```
alembic.util.exc.CommandError: Target database is not up to date
```
**Giải pháp**: Chạy `flask db upgrade` để apply pending migrations

## Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Roadmap

- [x] Setup project structure
- [x] Configure Flask application factory
- [x] Setup SQLAlchemy và migrations
- [x] Configure Dependency Injection
- [ ] Implement user authentication
- [ ] Implement menu management
- [ ] Implement order management
- [ ] Implement table management
- [ ] Implement reservation system
- [ ] Implement real-time updates (SocketIO)
- [ ] Implement payment integration
- [ ] Add comprehensive tests
- [ ] Deploy to production




---
**Lưu ý**: Đây là project bài tập lớn phục vụ mục đích học tập. README sẽ được cập nhật liên tục theo tiến độ phát triển project.

