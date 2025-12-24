from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import Schema, pre_load, post_dump
from marshmallow import fields, validate, validates, ValidationError
from app.data.models import (
    TaiKhoan, VaiTro, NguoiDung, PhucVu, LeTan, 
    KhuVuc, Ban, KhungGio, PhienBan, PhanCong,
    TrangThaiTaiKhoan, TrangThaiBan, TrangThai, TenVaiTro, KhungGioAn, KhungGioDatBan, 
    PhieuMon, MonGhi, TuyChonMon, NhomTuyChon, MoTaMon, ThucDon, NhomMon, TrangThaiMonGhi, ThongBao,
    ThuNgan, DoanhThu, KhuyenMaiTheoPhanTram, KhuyenMaiCung, KhuyenMai, ThanhToan, YeuCau, YCPhieuMon, YCMonGhi
)
from app.extentions.extentions import ma
from datetime import datetime
from typing import Optional


# ============================== Schema cho Base ==========================================

class BaseInSchema(Schema):
    """
    Schema cơ sở cho INPUT (JSON -> DTO).
    Nhiệm vụ: Validate dữ liệu đầu vào.
    Không biết gì về SQLAlchemy.
    """
    class Meta:
        # Báo lỗi ngay khi có trường không mong muốn
        unknown = "RAISE"

class BaseOutSchemaMeta:
    """
    Meta class configuration cho OUTPUT schemas.
    Không thể dùng như schema trực tiếp, chỉ để kế thừa Meta config.
    """
    unknown = "RAISE"
    load_instance = True


class ThongBaoOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Thông Báo.
    """
    class Meta(BaseOutSchemaMeta):
        model = ThongBao
    nguoi_nhan_id = auto_field()
    tieu_de = auto_field()
    noi_dung = auto_field()
    da_doc = auto_field()
    phan_loai = auto_field()
    link = auto_field()

class YeuCauCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Yêu cầu.
    """
    ly_do = fields.Str(
        required=True,
        error_messages={
            "required": "Phải có lý do",
        }
    )
    



class YeuCauOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Yêu Cầu.
    """
    class Meta(BaseOutSchemaMeta):
        model = YeuCau
    id = auto_field()
    trang_thai = auto_field()
    ly_do = auto_field()
    ngay_tao = auto_field()
    ngay_sua_doi = auto_field()

class YeuCauMonGhiOutSchema(YeuCauOutSchema):
    """
    DTO trả về cho Yêu Cầu Món Ghi.
    """
    class Meta(BaseOutSchemaMeta):
        model = YCMonGhi
    
    mon_ghi_id = auto_field()

# ============================== Schema cho Vai Trò ==========================================

class VaiTroCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Vai trò.
    """
    vai_tro = fields.Str(
        required=True, 
        validate=validate.OneOf([e.value for e in TenVaiTro]),
        error_messages={
            "required": "Vai trò là bắt buộc",
            "validator_failed": "Vai trò không hợp lệ. Chọn một trong: admin, quanly, thungan, letan, phucvu"
        }
    )

class VaiTroUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Vai trò.
    """
    vai_tro = fields.Str(
        validate=validate.OneOf([e.value for e in TenVaiTro]),
        error_messages={
            "validator_failed": "Vai trò không hợp lệ"
        }
    )

class VaiTroOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Vai trò.
    """
    class Meta(BaseOutSchemaMeta):
        model = VaiTro
    
    id = auto_field(dump_only=True)
    vai_tro = auto_field()


# ============================== Schema cho Tài Khoản ==========================================

class TaiKhoanCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Tài khoản.
    """

    email = fields.Email(required=True, error_messages={"invalid": "Email không hợp lệ"})
    ten_tai_khoan = fields.Str(
        required=True, 
        validate=validate.Length(min=5, max=500),
        error_messages={
            "required": "Tên tài khoản là bắt buộc",
            "validator_failed": "Tên tài khoản phải từ 5-500 ký tự"
        }
    )
    mat_khau = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "Mật khẩu là bắt buộc",
            "validator_failed": "Mật khẩu phải có ít nhất 8 ký tự"
        }
    )

    xac_nhan_mat_khau = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "Mật khẩu là bắt buộc",
            "validator_failed": "Mật khẩu phải có ít nhất 8 ký tự"
        }
    )

    
class TaiKhoanUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Tài khoản.
    """
    ten_tai_khoan = fields.Str(validate=validate.Length(min=5, max=500))
    mat_khau = fields.Str(validate=validate.Length(min=8))
    vai_tro_id = fields.Int()
    trang_thai = fields.Str(validate=validate.OneOf([e.value for e in TrangThaiTaiKhoan]))

class TaiKhoanLoginSchema(BaseInSchema):
    """
    DTO nhận vào cho đăng nhập.
    """

    # email = fields.Email(required=True, error_messages={"invalid": "Email không hợp lệ"})
    ten_tai_khoan = fields.Str(
        required=True,
        error_messages={"required": "Tên tài khoản là bắt buộc"}
    )
    mat_khau = fields.Str(
        required=True,
        error_messages={"required": "Mật khẩu là bắt buộc"}
    )

class TaiKhoanOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Tài khoản (không bao gồm mật khẩu).
    """
    class Meta(BaseOutSchemaMeta):
        model = TaiKhoan
        exclude = ('mat_khau',)  # Không trả về mật khẩu
    
    id = auto_field(dump_only=True)
    trang_thai = auto_field()
    is_xac_thuc = auto_field()


    # Nested relationship
    vai_tro = fields.Nested('VaiTroOutSchema', dump_only=True)


# ============================== Schema cho Người Dùng ==========================================

class NguoiDungCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Người dùng.
    """
    ho_ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={
            "required": "Họ tên là bắt buộc",
            "validator_failed": "Họ tên phải từ 2-255 ký tự"
        }
    )
    tai_khoan_id = fields.Int(
        required=True,
        error_messages={"required": "Tài khoản ID là bắt buộc"}
    )

class NguoiDungUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Người dùng.
    """
    ho_ten = fields.Str(validate=validate.Length(min=2, max=255))
    tai_khoan_id = fields.Int()

class NguoiDungOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Người dùng.
    """
    class Meta(BaseOutSchemaMeta):
        model = NguoiDung
    
    id = auto_field(dump_only=True)
    ho_ten = auto_field()
    type = auto_field()
    
    # Nested relationship
    tai_khoan = fields.Nested('TaiKhoanOutSchema', dump_only=True)


# ============================== Schema cho Phục Vụ ==========================================

class PhucVuCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Phục vụ.
    """
    ho_ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={
            "required": "Họ tên là bắt buộc",
            "validator_failed": "Họ tên phải từ 2-255 ký tự"
        }
    )
    tai_khoan_id = fields.Int(
        required=True,
        error_messages={"required": "Tài khoản ID là bắt buộc"}
    )
    is_nhom_truong = fields.Bool(
        required=True,
        error_messages={"required": "Trạng thái nhóm trưởng là bắt buộc"}
    )
    khu_vuc_id = fields.Int(
        required=True,
        error_messages={"required": "Khu vực ID là bắt buộc"}
    )

class PhucVuUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Phục vụ.
    """
    ho_ten = fields.Str(validate=validate.Length(min=2, max=255))
    tai_khoan_id = fields.Int()
    is_nhom_truong = fields.Bool()
    khu_vuc_id = fields.Int()

class PhucVuOutSchema(NguoiDungOutSchema):
    """
    DTO trả về cho Phục vụ.
    """
    class Meta(NguoiDungOutSchema.Meta):
        model = PhucVu
    
    
    # Nested relationships
    # ds_phan_cong_hien_tai
    
    # Computed property
    so_ban_dang_phuc_vu = fields.Method("get_so_ban_dang_phuc_vu", dump_only=True)
    
    def get_so_ban_dang_phuc_vu(self, obj):
        return obj.so_ban_dang_phuc_vu


# ============================== Schema cho Lễ Tân ==========================================

class LeTanCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Lễ tân.
    """
    ho_ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={
            "required": "Họ tên là bắt buộc",
            "validator_failed": "Họ tên phải từ 2-255 ký tự"
        }
    )
    tai_khoan_id = fields.Int(
        required=True,
        error_messages={"required": "Tài khoản ID là bắt buộc"}
    )

class LeTanUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Lễ tân.
    """
    ho_ten = fields.Str(validate=validate.Length(min=2, max=255))
    tai_khoan_id = fields.Int()

class LeTanOutSchema(NguoiDungOutSchema):
    """
    DTO trả về cho Lễ tân.
    """
    class Meta(NguoiDungOutSchema.Meta):
        model = LeTan


# ============================== Schema cho Đầu Bếp ==========================================

class ThuNganOutSchema(NguoiDungOutSchema):
    """
    DTO trả về cho Thu ngân.
    """
    class Meta(NguoiDungOutSchema.Meta):
        model = ThuNgan

    # Nested relationships
    ds_doanh_thu = fields.List(fields.Nested('DoanhThuLessOutSchema'), dump_only=True)

class DoanhThuOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Doanh thu.
    """
    class Meta(BaseOutSchemaMeta):
        model = DoanhThu

    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    tong_tien = auto_field()
    tien_giam_gia = auto_field()
    tien_cuoi_cung = auto_field()
    ten_thue = auto_field()
    ti_le_thue = auto_field()
    tien_thue = auto_field()

    trang_thai = auto_field()
    phien_ban_id = auto_field()
    thu_ngan_id = auto_field()

    phien_ban = fields.Nested('PhienBanOutSchema', exclude=('doanh_thu',), dump_only=True)
    ds_thanh_toan = fields.List(fields.Nested('ThanhToanOutSchema'), dump_only=True)
    
class ThanhToanOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Thanh toán.
    """
    class Meta(BaseOutSchemaMeta):
        model = ThanhToan

    so_tien = auto_field()
    phuong_thuc = auto_field()
    trang_thai = auto_field()


class DoanhThuLessOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Doanh thu nhưng chỉ gồm các thông tin cơ bản (cho xem sơ qua)
    """
    class Meta(BaseOutSchemaMeta):
        model = DoanhThu
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    tong_tien = auto_field()
    trang_thai = auto_field()
    phien_ban_id = auto_field()


class KhuyenMaiInSchema(SQLAlchemyAutoSchema):
    """
    DTO nhận vào để lấy thông tin
    """
    ids = fields.List(fields.Int(required=True, validate=validate.Range(min=1)))


class KhuyenMaiOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Doanh thu nhưng chỉ gồm các thông tin cơ bản (cho xem sơ qua)
    """
    class Meta(BaseOutSchemaMeta):
        model = KhuyenMai
    id = auto_field(dump_only=True)
    ten = auto_field(dump_only=True)
    mo_ta = auto_field(dump_only=True)
    hoat_dong = auto_field(dump_only=True)

    gia_tri_don_hang_toi_thieu = auto_field(dump_only=True)
    gioi_han = auto_field(dump_only=True)

    ngay_bat_dau = auto_field(dump_only=True)
    ngay_het_han = auto_field(dump_only=True)
    tu_dong_ap_dung = auto_field(dump_only=True)
    thu_tu_uu_tien = auto_field(dump_only=True)


    


# ============================== Schema cho Khu Vực ==========================================

class KhuVucCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Khu vực.
    """
    ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={
            "required": "Tên khu vực là bắt buộc",
            "validator_failed": "Tên khu vực phải từ 2-100 ký tự"
        }
    )

class KhuVucUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Khu vực.
    """
    ten = fields.Str(validate=validate.Length(min=2, max=100))
    nhom_truong_id = fields.Int(allow_none=True)

class KhuVucOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Khu vực.
    """
    class Meta(BaseOutSchemaMeta):
        model = KhuVuc
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    ten = auto_field()
    
    # Nested relationships
    ds_ban = fields.List(fields.Nested('BanOutSchema'), dump_only=True)


# ============================== Schema cho Bàn ==========================================

class BanCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Bàn.
    """
    ten = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Tên bàn là bắt buộc",
            "validator_failed": "Tên bàn phải từ 1-100 ký tự"
        }
    )
    so_ghe = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=50),
        error_messages={
            "required": "Số ghế là bắt buộc",
            "validator_failed": "Số ghế phải từ 1-50"
        }
    )
    khu_vuc_id = fields.Int(
        required=True,
        error_messages={"required": "Khu vực ID là bắt buộc"}
    )
    trang_thai = fields.Str(
        validate=validate.OneOf([e.value for e in TrangThaiBan]),
        load_default=TrangThaiBan.TRONG.value
    )

class BanUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Bàn.
    """
    ten = fields.Str(validate=validate.Length(min=1, max=100))
    so_ghe = fields.Int(validate=validate.Range(min=1, max=50))
    khu_vuc_id = fields.Int()
    trang_thai = fields.Str(validate=validate.OneOf([e.value for e in TrangThaiBan]))

class BanInSchema(BaseInSchema):
    """
    DTO nhận vào để lấy thông tin
    """
    id =  fields.Int(required=True, validate=validate.Range(min=1))
    



class PolymorphicKhungGioField(fields.Field):
    """
    Custom Field để xử lý đa hình cho KhungGio.
    Nó sẽ chọn Schema dựa trên thuộc tính 'type' của model.
    """
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        
        # 'value' ở đây là một object SQLAlchemy (KhungGio instance)
        # lấy 'type' từ object đó (config polymorphic_on=type)
        obj_type = getattr(value, 'type', None)

        # Mapping từ 'type' trong DB sang Schema Class
        # Key khớp với type trong model
        schema_map = {
            'khung_gio_an': KhungGioAnOutSchema,
            'khung_gio_dat_ban': KhungGioDatBanOutSchema,
            'khung_gio': KhungGioOutSchema # Fallback về schema gốc
        }

        # Chọn Schema class
        schema_class = schema_map.get(obj_type, KhungGioOutSchema)
        
        # Khởi tạo Schema và dump object
        # many=False vì field này xử lý TỪNG item trong list
        schema = schema_class()
        return schema.dump(value)


class BanOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Bàn.
    """
    class Meta(BaseOutSchemaMeta):
        model = Ban
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    ten = auto_field()
    so_ghe = auto_field()
    trang_thai = auto_field()
    khu_vuc_id = auto_field()
    
    # Nested relationships
    ds_khung_gio = fields.List(PolymorphicKhungGioField(), dump_only=True)


# ============================== Schema cho Khung Giờ ==========================================

class KhungGioCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Khung giờ.
    """
    tg_bat_dau = fields.DateTime(
        required=True,
        format='iso',
        error_messages={"required": "Thời gian bắt đầu là bắt buộc"}
    )
    tg_ket_thuc_du_kien = fields.DateTime(
        required=True,
        format='iso',
        error_messages={"required": "Thời gian kết thúc dự kiến là bắt buộc"}
    )
    phien_ban_id = fields.Int(
        required=True,
        error_messages={"required": "Phiên bàn ID là bắt buộc"}
    )
    trang_thai = fields.Str(
        validate=validate.OneOf([e.value for e in TrangThai]),
        load_default=TrangThai.MO.value
    )

class KhungGioUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Khung giờ.
    """
    tg_bat_dau = fields.DateTime(format='iso')
    tg_ket_thuc_du_kien = fields.DateTime(format='iso')
    trang_thai = fields.Str(validate=validate.OneOf([e.value for e in TrangThai]))
    phien_ban_id = fields.Int()


class KhungGioOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Khung giờ.
    """
    class Meta(BaseOutSchemaMeta):
        model = KhungGio
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    type =  auto_field()
    tg_bat_dau = auto_field()
    tg_ket_thuc_du_kien = auto_field()
    trang_thai = auto_field()
    phien_ban_id = auto_field()


class KhungGioAnOutSchema(KhungGioOutSchema):

    class Meta(KhungGioOutSchema.Meta):
        model =  KhungGioAn
    
class KhungGioDatBanOutSchema(KhungGioOutSchema):

    class Meta(KhungGioOutSchema.Meta):
        model =  KhungGioDatBan
    

# class KhungGioAnOutSchema(SQLAlchemyAutoSchema):
#     """
#     DTO trả về khung giờ ăn
    
#     Keyword arguments:
#     argument -- description
#     Return: return_description
#     """
#     class Meta(BaseOutSchemaMeta):
#         model = KhungGioAn
    
#     id = auto_field(dump_only=True)
#     ngay_tao = auto_field(dump_only=True)
#     ngay_sua_doi = auto_field(dump_only=True)
#     tg_bat_dau = auto_field()
#     tg_ket_thuc_du_kien = auto_field()
#     trang_thai = auto_field()
#     phien_ban_id = auto_field()

# class KhungGioDatbanOutSchema(SQLAlchemyAutoSchema):
#     """
#     DTO trả về khung giờ đặt bàn
    
#     Keyword arguments:
#     argument -- description
#     Return: return_description
#     """
#     class Meta(BaseOutSchemaMeta):
#         model = KhungGioDatBan
    
#     id = auto_field(dump_only=True)
#     ngay_tao = auto_field(dump_only=True)
#     ngay_sua_doi = auto_field(dump_only=True)
#     tg_bat_dau = auto_field()
#     tg_ket_thuc_du_kien = auto_field()
#     trang_thai = auto_field()
#     phien_ban_id = auto_field()


# ============================== Schema cho Phiên Bàn ==========================================

class PhienBanCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Phiên bàn.
    """
    le_tan_id = fields.Int(
        required=True,
        error_messages={"required": "Lễ tân ID là bắt buộc"}
    )
    trang_thai = fields.Str(
        validate=validate.OneOf([e.value for e in TrangThai]),
        load_default=TrangThai.MO.value
    )
    # Optional: thời gian bắt đầu cho khung giờ
    tg_bat_dau = fields.DateTime(format='iso', allow_none=True)

class PhienBanUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Phiên bàn.
    """
    trang_thai = fields.Str(validate=validate.OneOf([e.value for e in TrangThai]))
    le_tan_id = fields.Int()

class PhienBanOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Phiên bàn.
    """
    class Meta(BaseOutSchemaMeta):
        model = PhienBan
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    le_tan_id = auto_field()
    nguoi_dam_nhan_id = auto_field()
    
    # Nested relationships
    le_tan = fields.Nested('LeTanOutSchema', dump_only=True)
    khung_gio = fields.Nested('KhungGioOutSchema', dump_only=True)
    ds_phan_cong = fields.List(fields.Nested('PhanCongOutSchema'), dump_only=True)
    nguoi_dam_nhan = fields.Nested('PhucVuOutSchema', dump_only=True)
    
    ds_phieu_mon = fields.List(fields.Nested('PhieuMonOutSchema'), dump_only=True)
    doanh_thu = fields.Nested('DoanhThuOutSchema', dump_only=True)

class PhienBanOutLessSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Phiên bàn nhưng chỉ gồm các thông tin cơ bản (cho xem sơ qua)
    """
    class Meta(BaseOutSchemaMeta):
        model = PhienBan
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    le_tan_id = auto_field()
    nguoi_dam_nhan_id = auto_field()

    khung_gio = fields.Nested('KhungGioOutSchema', dump_only=True)
    

class PhienBanInSchema(SQLAlchemyAutoSchema):
    id =  fields.Int(required=True, validate=validate.Range(min=1))


# ============================== Schema cho Phân Công ==========================================

class PhanCongCreateSchema(BaseInSchema):
    """
    DTO nhận vào để tạo Phân công.
    """
    phuc_vu_id = fields.Int(
        required=True,
        error_messages={"required": "Phục vụ ID là bắt buộc"}
    )
    ban_id = fields.Int(
        required=True,
        error_messages={"required": "Bàn ID là bắt buộc"}
    )
    phien_ban_id = fields.Int(
        required=True,
        error_messages={"required": "Phiên bàn ID là bắt buộc"}
    )
    trang_thai = fields.Str(
        validate=validate.OneOf([e.value for e in TrangThai]),
        load_default=TrangThai.MO.value
    )

class PhanCongUpdateSchema(BaseInSchema):
    """
    DTO nhận vào để cập nhật Phân công.
    """
    trang_thai = fields.Str(validate=validate.OneOf([e.value for e in TrangThai]))
    phuc_vu_id = fields.Int()
    ban_id = fields.Int()
    phien_ban_id = fields.Int()

class PhanCongOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Phân công.
    """
    class Meta(BaseOutSchemaMeta):
        model = PhanCong
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    phuc_vu_id = auto_field()
    ban_id = auto_field()
    phien_ban_id = auto_field()
    
    # Nested relationships (optional, tùy use case)
    # Uncomment nếu cần trả về chi tiết
    # phuc_vu = fields.Nested('PhucVuOutSchema', dump_only=True, exclude=('ds_phan_cong_hien_tai',))
    # ban = fields.Nested('BanOutSchema', dump_only=True)

# ============================== Schema cho Phiếu Món ==========================================


class PhieuMonOutLessSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Phiếu món
    """
    class Meta(BaseOutSchemaMeta):
        model = PhieuMon
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    phien_ban_id = auto_field()



class PhieuMonOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Phiếu món
    """
    class Meta(BaseOutSchemaMeta):
        model = PhieuMon
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    phien_ban_id = auto_field()

    ds_mon_ghi = fields.List(fields.Nested('MonGhiOutSchema'), dump_only=True)


# ============================== Schema cho Món Ghi ==========================================

class TuyChonInSchema(BaseInSchema):
    tuy_chon_id = fields.Int()
    ten = fields.Str()
    gia = fields.Int()

class MonGhiCreateSchema(BaseInSchema):
    so_luong = fields.Int()
    ghi_chu = fields.Str(required=False)
    phieu_mon_id = fields.Int()
    mo_ta_mon_id = fields.Int()
    ds_tuy_chon = fields.List(fields.Nested(TuyChonInSchema), required=True)

class DanhSachMonGhiCreateSchema(BaseInSchema):
    ds_mon_ghi = fields.List(fields.Nested(MonGhiCreateSchema), required=True)

class MonGhiStatusUpdateSchema(BaseInSchema):
    trang_thai = fields.Str()

    @validates('trang_thai')
    def validate_trang_thai(self, value, **kwargs):
        tts = [tt.name for tt in TrangThaiMonGhi]


        for tt in tts:
            if value.upper() == tt.upper():
                return
            
        raise ValidationError('Trạng thái nhận vào không hợp lệ')


class MonGhiOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Món Ghi
    """
    class Meta(BaseOutSchemaMeta):
        model = MonGhi
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    so_luong = auto_field(dump_only=True)
    ghi_chu = auto_field(dump_only=True)
    trang_thai = auto_field(dump_only=True)
    phieu_mon_id = auto_field(dump_only=True)

    mo_ta_mon = fields.Nested('MoTaMonOutSchema', dump_only=True)
    ds_tuy_chon = fields.List(fields.Nested('TuyChonMonOutSchema'), dump_only=True)


# ============================== Schema cho Tùy Chọn Món (Topping) ==========================================

class TuyChonMonOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Tùy Chọn Món
    """
    class Meta(BaseOutSchemaMeta):
        model = TuyChonMon
    ten = auto_field(dump_only=True)
    hinh = auto_field(dump_only=True)
    gia = auto_field(dump_only=True)

# ============================== Schema cho Nhóm Tùy Chọn ==========================================

class NhomTuyChonOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Nhóm Tùy Chọn
    """
    class Meta(BaseOutSchemaMeta):
        model = NhomTuyChon
    
    ten = auto_field(dump_only=True)
    trang_thai = auto_field(dump_only=True)
    loai = auto_field(dump_only=True)

    ds_tuy_chon = fields.List(fields.Nested('TuyChonMonOutSchema'), dump_only=True)


# ============================== Schema cho Mô Tả Món ==========================================

class MoTaMonOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Mô Tả Món
    """
    class Meta(BaseOutSchemaMeta):
        model = MoTaMon
    
    ten = auto_field(dump_only=True)
    hinh = auto_field(dump_only=True)
    trang_thai = auto_field(dump_only=True)
    gia = auto_field(dump_only=True)

    ds_nhom_tuy_chon = fields.List(fields.Nested('NhomTuyChonOutSchema'), dump_only=True)


class NhomMonOutSchema(SQLAlchemyAutoSchema):
    class Meta(BaseOutSchemaMeta):
        model = NhomMon
    
    ten = auto_field(dump_only=True)

    ds_mo_ta_mon = fields.List(fields.Nested('MoTaMonOutSchema'), dump_only=True)

# ============================== Schema cho Thực Đơn ==========================================

class ThucDonOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về cho Thực Đơn
    """
    class Meta(BaseOutSchemaMeta):
        model = ThucDon
    ds_nhom_mon = fields.List(fields.Nested('NhomMonOutSchema', dump_only=True))




# ============================== Schema tổng hợp (cho các trường hợp đặc biệt) ==========================================

class PhanCongDetailOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về chi tiết đầy đủ cho Phân công (bao gồm thông tin phục vụ và bàn).
    """
    class Meta(BaseOutSchemaMeta):
        model = PhanCong
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    phuc_vu_id = auto_field()
    ban_id = auto_field()
    phien_ban_id = auto_field()
    
    # Nested relationships với thông tin đầy đủ
    phuc_vu = fields.Nested('PhucVuOutSchema', dump_only=True, exclude=('ds_phan_cong_hien_tai',))
    ban = fields.Nested('BanOutSchema', dump_only=True)


class PhienBanDetailOutSchema(SQLAlchemyAutoSchema):
    """
    DTO trả về chi tiết đầy đủ cho Phiên bàn (bao gồm tất cả phân công với thông tin chi tiết).
    """
    class Meta(BaseOutSchemaMeta):
        model = PhienBan
    
    id = auto_field(dump_only=True)
    ngay_tao = auto_field(dump_only=True)
    ngay_sua_doi = auto_field(dump_only=True)
    trang_thai = auto_field()
    le_tan_id = auto_field()
    
    # Nested relationships
    le_tan = fields.Nested('LeTanOutSchema', dump_only=True)
    khung_gio = fields.Nested('KhungGioOutSchema', dump_only=True)
    ds_phan_cong = fields.List(fields.Nested('PhanCongDetailOutSchema'), dump_only=True)


# class KhuVucDetailOutSchema(SQLAlchemyAutoSchema):
#     """
#     DTO trả về chi tiết đầy đủ cho Khu vực (bao gồm danh sách bàn với khung giờ).
#     """
#     class Meta(BaseOutSchemaMeta):
#         model = KhuVuc
    
#     id = auto_field(dump_only=True)
#     ngay_tao = auto_field(dump_only=True)
#     ngay_sua_doi = auto_field(dump_only=True)
#     ten = auto_field()
    
#     # Nested relationships
#     ds_ban = fields.List(fields.Nested('BanOutSchema'), dump_only=True)





    