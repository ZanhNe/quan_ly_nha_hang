from typing import List, Dict, Any
from injector import inject
import jwt
import datetime as dt
from app.data.models import KhuVuc, Ban, PhienBan, LeTan, PhucVu, TaiKhoan, TenVaiTro, NguoiDung
from app.data.dao.interfaces.interfaces import (IKhuVucDAO, IBanDAO, INguoiDungDAO, IPhienBanDAO, ITaiKhoanDAO, IVaiTroDAO)
from app.domain.services.interfaces.interfaces import (IBoChonNhanVien, IBanService, IKhuVucService, ITaiKhoanService)
from .transaction_manager import transaction_manager
from app.schemas.schema import KhuVucOutSchema
from app.schemas.init_schema import khuvucs_out_schema, ds_ban_out_schema, phuc_vu_out_schema, le_tan_out_schema, nguoi_dung_out_schema
from app.utils.helper import IHelper





# Pure
class BoChonNhanVien(IBoChonNhanVien):
    def chon_phuc_vu(self, ds_phucvu: List[PhucVu]) -> PhucVu:
        tai_thap_nhat = 999

        phucvu = None

        for pv in ds_phucvu:
            if pv.so_ban_dang_phuc_vu <= 2 and pv.so_ban_dang_phuc_vu < tai_thap_nhat:
                tai_thap_nhat = pv.so_ban_dang_phuc_vu
                phucvu = pv
        return phucvu
    





# Service

class TaiKhoanService(ITaiKhoanService):
    @inject
    def __init__(self, tai_khoan_dao: ITaiKhoanDAO, vai_tro_dao: IVaiTroDAO, helper: IHelper):
        self.tai_khoan_dao = tai_khoan_dao
        self.vai_tro_dao = vai_tro_dao
        self.helper = helper

    def dang_ky_tai_khoan(self, tai_khoan_create: List[Dict[str, Any]]) -> bool:
        with transaction_manager.transaction('Lỗi khi đăng ký tài khoản') as session:
            if tai_khoan_create['mat_khau'] != tai_khoan_create['xac_nhan_mat_khau']:
                raise Exception('Mật khẩu xác nhận không trùng khớp với mật khẩu chỉ định')
            
            tai_khoan = self.tai_khoan_dao.find_by_ten_tai_khoan(session=session, ten_tai_khoan=tai_khoan_create['ten_tai_khoan'])
            
            if tai_khoan:
                raise Exception('Tài khoản đã tồn tại!')


            
            vo_danh = self.vai_tro_dao.find_by_ten_vai_tro(session=session, ten_vai_tro=TenVaiTro.VODANH)
            mat_khau_hash = self.helper.hass_pass(tai_khoan_create['mat_khau'])
            
            token = self.helper.generate_token(email=tai_khoan_create['email'])

            nguoi_dung = NguoiDung(ho_ten="Chưa có tên", tai_khoan=tai_khoan)
            tai_khoan = TaiKhoan(email=tai_khoan_create['email'], ten_tai_khoan=tai_khoan_create['ten_tai_khoan'], \
                                 mat_khau=mat_khau_hash, xac_thuc_token=token, vai_tro=vo_danh, nguoi_dung=nguoi_dung)
            
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)

            self.helper.send_verification_email(user_email=tai_khoan.email, token=token)

            return True
    
    def xac_thuc_tai_khoan(self, token: str) -> bool:
        with transaction_manager.transaction('Có lỗi trong quá trình xác thực') as session:
            if not token:
                return False
            
            tai_khoan = self.tai_khoan_dao.find_by_xac_thuc_token(session=session, token=token)
            print(tai_khoan)
            info = self.helper.verify_token(token=token)
            print('Infor trả ra: ', info)
            
            if not tai_khoan or not info:
                return False
            
            tai_khoan.is_xac_thuc = True
            tai_khoan.xac_thuc_token = None

            return True
        
    def dang_nhap_tai_khoan(self, tai_khoan_login: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Có lỗi trong quá trình đăng nhập') as session:
            tai_khoan = self.tai_khoan_dao.find_by_ten_tai_khoan(session=session, ten_tai_khoan=tai_khoan_login['ten_tai_khoan'])
            if not tai_khoan:
                raise Exception('Tài khoản không tồn tại')
            
            
            flag = self.helper.check_pass(plain=tai_khoan_login['mat_khau'], hashed_pass=tai_khoan.mat_khau)
            if not flag:
                raise Exception('Mật khẩu không chính xác')
            
            nguoi_dung = tai_khoan.nguoi_dung
            print(nguoi_dung)
            nguoi_dung_dto = None

            if isinstance(nguoi_dung, PhucVu):
                nguoi_dung_dto = phuc_vu_out_schema.dump(nguoi_dung)
            elif isinstance(nguoi_dung, LeTan):
                nguoi_dung_dto = le_tan_out_schema.dump(nguoi_dung)
            elif isinstance(nguoi_dung, NguoiDung):
                nguoi_dung_dto = nguoi_dung_out_schema.dump(nguoi_dung)

            print(nguoi_dung_dto)
            return nguoi_dung_dto

            
        
            
            
            
            
            
            


            

        

class KhuVucService(IKhuVucService):

    @inject
    def __init__(self, khuvuc_dao: IKhuVucDAO):
        self.khuvuc_dao = khuvuc_dao

    def get_all_khuvuc(self) -> List[KhuVucOutSchema]:
        with transaction_manager.transaction('Lỗi khi lấy ra toàn bộ khu vực') as session:
            ds_khuvuc = self.khuvuc_dao.find_all(session=session)
            ds_khuvuc_schema = khuvucs_out_schema.dump(obj=ds_khuvuc)

            return ds_khuvuc_schema
        
    
class BanService(IBanService):
    @inject
    def __init__(self, bo_chon_nhan_vien: IBoChonNhanVien, phien_ban_dao: IPhienBanDAO, nguoidung_dao: INguoiDungDAO, ban_dao: IBanDAO):
        self.phien_ban_dao = phien_ban_dao
        self.nguoidung_dao = nguoidung_dao
        self.ban_dao = ban_dao
        self.bo_chon_nhan_vien = bo_chon_nhan_vien

    def get_ban_details(self, ban_schemas_in: List[Dict[str, Any]]) -> List[Ban]:
        with transaction_manager.transaction('Lỗi khi lấy ra danh sách bàn') as session:
            ids = [ban['id'] for ban in ban_schemas_in]
            ds_ban = self.ban_dao.find_all_by_ids(session=session, ids=ids)

            found_ids = {ban.id for ban in ds_ban}
            requested_ids = {ban['id'] for ban in ban_schemas_in}

            invalid_ids = found_ids - requested_ids

            if invalid_ids:
                raise Exception("Bàn không hợp lệ")
            
            return ds_ban
    
    def xu_ly_chon_ban(self, letan_id: int, ban_schemas_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi xử lý chọn bàn') as session:
            phien = None
            
            ds_ban = self.get_ban_details(ban_schemas_in=ban_schemas_in)
            
            tg_bat_dau = dt.datetime.now()

            if not len(ds_ban):
                raise Exception('Vui lòng chọn ít nhất 1 bàn để có thể đánh dấu!')

            

            for ban in ds_ban:
                if not ban.kiem_tra_ban_trong():
                    raise Exception(f'Bàn {ban.ten} hiện đang được sử dụng! Vui lòng chọn lại!')
                if not ds_ban[0].kiem_tra_thuoc_cung_khu_vuc(ban=ban):
                    raise Exception('Trường hợp đặt nhiều bàn thì phải cùng 1 khu vực! Vui lòng chọn lại!')
                if not ban.kiem_tra_thoi_gian_danh_dau(tg=tg_bat_dau):
                    raise Exception(f'Bàn {ban.ten} hiện đang chuẩn bị cho khách đặt trước! Vui lòng chọn lại!')
                
            letan = self.nguoidung_dao.find_by_id(session=session, id=letan_id)
            ds_phucvu = self.nguoidung_dao.find_by_khuvuc_id(session=session, khuvuc_id=ds_ban[0].khu_vuc_id)
            
            if not letan:
                raise Exception('Không tồn tại lễ tân này trong hệ thống!')
            if not len(ds_phucvu):
                raise Exception('Không tồn tại nhân viên nào của khu vực để phục vụ!')
            
            if isinstance(letan, LeTan):
                phien = letan.tao_phien(tg_bat_dau=tg_bat_dau)
            else:
                raise Exception('Không phải lễ tân để có thể chọn bàn!')

            khung_gio = phien.khung_gio

            for ban in ds_ban:
                ban.them_khung_gio(khung_gio=khung_gio)

                

            
            for ban in ds_ban:
                phucvu = self.bo_chon_nhan_vien.chon_phuc_vu(ds_phucvu=ds_phucvu)
                phien.phan_cong(phuc_vu=phucvu, ban=ban)
            
            self.phien_ban_dao.save(session=session, phien=phien)

            print(ds_ban[0].ds_khung_gio[0])

            ds_ban_dto = ds_ban_out_schema.dump(ds_ban)

            
            return ds_ban_dto



            

            
            

            


                
            
                
            
            
            
            
            
            
            