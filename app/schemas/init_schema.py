#Schema
from app.schemas.schema import (KhuVucOutSchema, BanOutSchema, TaiKhoanCreateSchema, TaiKhoanLoginSchema\
                                , PhucVuOutSchema, LeTanOutSchema, NguoiDungOutSchema, BanInSchema, PhienBanOutLessSchema
                                , PhienBanInSchema, PhienBanOutSchema, ThucDonOutSchema, PhieuMonOutSchema, DanhSachMonGhiCreateSchema
                                , PhieuMonOutLessSchema, MonGhiOutSchema, MonGhiStatusUpdateSchema, ThongBaoOutSchema, DoanhThuLessOutSchema
                                , KhuyenMaiOutSchema, KhuyenMaiInSchema, DoanhThuOutSchema, YeuCauMonGhiOutSchema, YeuCauCreateSchema)



#init schema
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

def convert_yeu_cau(ds_yeu_cau):
    yc_out = []
    for yc in ds_yeu_cau:
        if yc.type == 'yc_mon_ghi':
            yc_out.append(yc_mon_ghi_out_schema.dump(yc))
        
    return yc_out