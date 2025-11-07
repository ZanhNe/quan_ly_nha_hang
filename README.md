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

*(Phần này sẽ được cập nhật khi các models được định nghĩa)*



## Testing

Chạy test suite:
```bash
# Chạy tất cả tests
pytest

# Chạy với coverage
pytest --cov=app

# Chạy test cụ thể
pytest tests/test_services.py
```

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

