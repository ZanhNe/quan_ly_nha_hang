# Các Schema dùng để validate và serialize dữ liệu
from app.schemas.schema import (KhuVucOutSchema, BanOutSchema, TaiKhoanCreateSchema, TaiKhoanLoginSchema\
                                , PhucVuOutSchema, LeTanOutSchema, NguoiDungOutSchema, BanInSchema, PhienBanOutLessSchema
                                , PhienBanInSchema, PhienBanOutSchema, ThucDonOutSchema, PhieuMonOutSchema, DanhSachMonGhiCreateSchema
                                , PhieuMonOutLessSchema, MonGhiOutSchema, MonGhiStatusUpdateSchema, ThongBaoOutSchema, DoanhThuLessOutSchema
                                , KhuyenMaiOutSchema, KhuyenMaiInSchema, DoanhThuOutSchema, YeuCauMonGhiOutSchema, YeuCauCreateSchema
                                , DatBanCreateSchema, DatBanOutSchema, TaiKhoanOutSchema)

from app.schemas.schema import (AdminTaiKhoanCreateSchema, AdminTaiKhoanUpdateSchema, AdminDuyetTaiKhoanSchema, AdminNhanVienCreateSchema
                                , AdminNhanVienUpdateSchema, AdminKhuVucCreateSchema, AdminKhuVucUpdateSchema, AdminBanCreateSchema
                                , AdminBanUpdateSchema, AdminNhomMonCreateSchema, AdminNhomMonUpdateSchema, AdminMonCreateSchema, AdminMonUpdateSchema
                                , AdminMonTrangThaiSchema, AdminKhuyenMaiCreateSchema, AdminKhuyenMaiUpdateSchema, AdminCauHinhThueCreateSchema
                                , AdminCauHinhThueUpdateSchema, AdminThucDonOutSchema)



# Khởi tạo các instance của schema để dùng chung trong toàn ứng dụng
khuvucs_out_schema = KhuVucOutSchema(many=True)
ds_ban_out_schema = BanOutSchema(many=True)
ds_ban_in_schema = BanInSchema(many=True)
phien_ban_in_schema = PhienBanInSchema()
phien_ban_out_less_schema = PhienBanOutLessSchema()
phien_ban_out_schema = PhienBanOutSchema()
thuc_don_out_schema = ThucDonOutSchema()
phieu_mon_out_schema = PhieuMonOutSchema()
phieu_mon_out_less_schema = PhieuMonOutLessSchema()
ds_mon_ghi_create_schema = DanhSachMonGhiCreateSchema()

mon_ghi_out_schema = MonGhiOutSchema()
mon_ghi_status_update_schema = MonGhiStatusUpdateSchema()

tai_khoan_create_schema = TaiKhoanCreateSchema()
tai_khoan_login_schema = TaiKhoanLoginSchema()
tai_khoan_out_schema = TaiKhoanOutSchema()

phuc_vu_out_schema = PhucVuOutSchema()
le_tan_out_schema = LeTanOutSchema()
nguoi_dung_out_schema = NguoiDungOutSchema()

thong_bao_out_schema = ThongBaoOutSchema()
doanh_thu_out_less_schema = DoanhThuLessOutSchema()
doanh_thu_out_schema = DoanhThuOutSchema()
khuyen_mai_out_schema = KhuyenMaiOutSchema()
khuyen_mai_in_schema = KhuyenMaiInSchema()

yc_mon_ghi_out_schema = YeuCauMonGhiOutSchema()
yc_create_schema = YeuCauCreateSchema()

dat_ban_create_schema = DatBanCreateSchema()
dat_ban_out_schema = DatBanOutSchema()


admin_tai_khoan_create_schema = AdminTaiKhoanCreateSchema()
admin_tai_khoan_update_schema = AdminTaiKhoanUpdateSchema()
admin_duyet_tai_khoan_schema = AdminDuyetTaiKhoanSchema()
admin_nhan_vien_create_schema = AdminNhanVienCreateSchema()
admin_nhan_vien_update_schema = AdminNhanVienUpdateSchema()
admin_khu_vuc_create_schema = AdminKhuVucCreateSchema()
admin_khu_vuc_update_schema = AdminKhuVucUpdateSchema()
admin_ban_create_schema = AdminBanCreateSchema()
admin_ban_update_schema = AdminBanUpdateSchema()
admin_nhom_mon_create_schema = AdminNhomMonCreateSchema()
admin_nhom_mon_update_schema = AdminNhomMonUpdateSchema()
admin_mon_create_schema = AdminMonCreateSchema()
admin_mon_update_schema = AdminMonUpdateSchema()
admin_mon_trang_thai_schema = AdminMonTrangThaiSchema()
admin_khuyen_mai_create_schema = AdminKhuyenMaiCreateSchema()
admin_khuyen_mai_update_schema = AdminKhuyenMaiUpdateSchema()
admin_cau_hinh_thue_create_schema = AdminCauHinhThueCreateSchema()
admin_cau_hinh_thue_update_schema = AdminCauHinhThueUpdateSchema()


admin_thuc_don_out_schema = AdminThucDonOutSchema()


def convert_yeu_cau(ds_yeu_cau):
    """
    Hàm bổ trợ để convert danh sách yêu cầu sang định dạng JSON schema tương ứng.
    """
    yc_out = []
    for yc in ds_yeu_cau:
        if yc.type == 'yc_mon_ghi':
            yc_out.append(yc_mon_ghi_out_schema.dump(yc))
        
    return yc_out