#Schema
from app.schemas.schema import (KhuVucOutSchema, BanOutSchema, TaiKhoanCreateSchema, TaiKhoanLoginSchema\
                                , PhucVuOutSchema, LeTanOutSchema, NguoiDungOutSchema, BanInSchema)



#init schema
khuvucs_out_schema = KhuVucOutSchema(many=True)
ds_ban_out_schema = BanOutSchema(many=True)
ds_ban_in_schema = BanInSchema(many=True)

tai_khoan_create_schema = TaiKhoanCreateSchema()
tai_khoan_login_schema = TaiKhoanLoginSchema()

phuc_vu_out_schema = PhucVuOutSchema()
le_tan_out_schema = LeTanOutSchema()
nguoi_dung_out_schema = NguoiDungOutSchema()