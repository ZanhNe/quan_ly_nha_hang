from typing import List, Dict, Any
from injector import inject
import jwt
import datetime as dt
from app.data.models import (KhuVuc, Ban, PhienBan, LeTan, PhucVu, ThuNgan, DauBep, QuanLy, TaiKhoan, TenVaiTro, NguoiDung, ThucDon, PhieuMon
                             , HoanThanhMon, HuyMon, DoanhThu, CauHinhThue, KhuyenMai, TrangThaiDoanhThu, TrangThaiTaiKhoan, DatBan, TrangThai)
from app.data.dao.interfaces.interfaces import (IKhuVucDAO, IBanDAO, INguoiDungDAO, IPhienBanDAO, ITaiKhoanDAO, IVaiTroDAO
                                                , IThucDonDAO, ITuyChonMonReadDAO, IPhieuMonReadDAO, IMonGhiReadDAO
                                                , IThongBaoReadDAO, IKhuyenMaiDAO, ICauHinhThueDAO, IDoanhThuDAO, IYeuCauReadDAO
                                                , IBaoCaoDAO, IDatBanDAO)
from app.domain.services.interfaces.interfaces import (IBoChonNhanVien, IBanService, IKhuVucService, ITaiKhoanService,
                                                       IPhienBanService, IThucDonService, IThemMonService, INguoiDungService,
                                                       IDoanhThuThanhToanService, IDoanhThuService, IKhuyenMaiService, IBaoCaoService)
from datetime import date, timedelta
from app.payment.interface import ThanhToanOnline
from .transaction_manager import transaction_manager
from app.schemas.schema import KhuVucOutSchema
from app.schemas.init_schema import (khuvucs_out_schema, ds_ban_out_schema, phuc_vu_out_schema
                                     , le_tan_out_schema, nguoi_dung_out_schema, phien_ban_out_less_schema
                                     , phien_ban_out_schema, thuc_don_out_schema, phieu_mon_out_schema
                                     , phieu_mon_out_less_schema, mon_ghi_out_schema, thong_bao_out_schema, doanh_thu_out_less_schema
                                     , khuyen_mai_out_schema, doanh_thu_out_schema, yc_mon_ghi_out_schema, convert_yeu_cau
                                     , dat_ban_out_schema)
from app.utils.helper import IHelper



class NguoiDungService(INguoiDungService):
    @inject
    def __init__(self, thong_bao_read_dao: IThongBaoReadDAO):
        self.thong_bao_read_dao = thong_bao_read_dao

    def xu_ly_lay_thong_bao_nguoi_dung(self, nguoi_dung_id: int, page: int, limit: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi lấy thông báo của người dùng') as session:
            ds_thong_bao, has_more = self.thong_bao_read_dao.find_by_nguoi_dung_id(session=session, nguoi_dung_id=nguoi_dung_id, page=page, limit=limit)
            unread_count = self.thong_bao_read_dao.count_unread(session=session, nguoi_dung_id=nguoi_dung_id)

            ds_thong_bao_out = thong_bao_out_schema.dump(ds_thong_bao, many=True)

            return ds_thong_bao_out, has_more, unread_count




# Pure
class BoChonNhanVien(IBoChonNhanVien):
    def chon_phuc_vu(self, ds_phucvu: List[PhucVu]) -> PhucVu:
        tai_thap_nhat = 999

        phucvu = None

        for pv in ds_phucvu: # Chọn ra ông nào đang ít việc nhất để giao (đỡ tị nạnh :v)
            if pv.so_ban_dang_phuc_vu <= 2 and pv.so_ban_dang_phuc_vu < tai_thap_nhat: #Phục vụ chỉ tối đa 3 bàn
                tai_thap_nhat = pv.so_ban_dang_phuc_vu
                phucvu = pv

        return phucvu
    



class TaiKhoanService(ITaiKhoanService):
    # Xử lý các luồng đăng ký, đăng nhập, xác thực...
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

            tai_khoan = TaiKhoan(email=tai_khoan_create['email'], ten_tai_khoan=tai_khoan_create['ten_tai_khoan'], \
                                 mat_khau=mat_khau_hash, xac_thuc_token=token, vai_tro=vo_danh)
            nguoi_dung = NguoiDung(ho_ten="Chưa có tên", tai_khoan=tai_khoan)

            
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)

            print(tai_khoan.nguoi_dung)

            self.helper.send_verification_email(user_email=tai_khoan.email, token=token)

            return True
    
    def xac_thuc_tai_khoan(self, token: str) -> bool:
        with transaction_manager.transaction('Có lỗi trong quá trình xác thực') as session:
            if not token:
                return False
            
            tai_khoan = self.tai_khoan_dao.find_by_xac_thuc_token(session=session, token=token)
            info = self.helper.verify_token(token=token)
            
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
            
            if tai_khoan.trang_thai == TrangThaiTaiKhoan.KHOA:
                raise Exception('Tài khoản đã bị khóa')
            
            flag = self.helper.check_pass(plain=tai_khoan_login['mat_khau'], hashed_pass=tai_khoan.mat_khau)
            if not flag:
                raise Exception('Mật khẩu không chính xác')
            
            nguoi_dung = tai_khoan.nguoi_dung
            nguoi_dung_dto = None

            if isinstance(nguoi_dung, PhucVu):
                nguoi_dung_dto = phuc_vu_out_schema.dump(nguoi_dung)
            elif isinstance(nguoi_dung, LeTan):
                nguoi_dung_dto = le_tan_out_schema.dump(nguoi_dung)
            elif isinstance(nguoi_dung, NguoiDung):
                nguoi_dung_dto = nguoi_dung_out_schema.dump(nguoi_dung)

            return nguoi_dung_dto

    def lay_danh_sach_cho_xet_duyet(self) -> List[Dict[str, Any]]:
        # Lấy mấy tài khoản vừa đăng ký đang chờ admin duyệt
        with transaction_manager.transaction('Lỗi khi lấy danh sách tài khoản chờ xét duyệt') as session:
            ds_tai_khoan = self.tai_khoan_dao.find_cho_xet_duyet(session=session)
            
            # Bọc lại data theo schema cho chuẩn bài
            ds_tai_khoan_out = []
            for tk in ds_tai_khoan:
                tk_dict = {
                    'id': tk.id,
                    'ten_tai_khoan': tk.ten_tai_khoan,
                    'email': tk.email,
                    'ho_ten': tk.nguoi_dung.ho_ten if tk.nguoi_dung else 'Chưa có tên',
                    'ngay_tao': str(tk.ngay_tao),
                    'is_xac_thuc': tk.is_xac_thuc,
                    'vai_tro': tk.vai_tro.vai_tro.value if tk.vai_tro else None
                }
                ds_tai_khoan_out.append(tk_dict)
            
            return ds_tai_khoan_out
    
    def xu_ly_duyet_tai_khoan(self, admin_id: int, tai_khoan_id: int, vai_tro_ten: str) -> Dict[str, Any]:
        # Luồng duyệt tài khoản: Check Admin -> Check User -> Gán Role -> Re-create Profile
        with transaction_manager.transaction('Lỗi khi duyệt tài khoản') as session:
            # Kiểm tra admin
            admin = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=admin_id)
            if not admin or admin.vai_tro.vai_tro != TenVaiTro.ADMIN:
                raise Exception('Bạn không có quyền duyệt tài khoản.')
            
            # Lấy tài khoản cần duyệt
            tai_khoan = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=tai_khoan_id)
            if not tai_khoan:
                raise Exception('Tài khoản không tồn tại.')
            
            # Phải xác thực email rồi mới cho duyệt tiếp
            if not tai_khoan.is_xac_thuc:
                raise Exception('Tài khoản chưa xác thực email.')
            
            if tai_khoan.vai_tro.vai_tro != TenVaiTro.VODANH:
                raise Exception('Tài khoản này đã được duyệt hoặc không ở trạng thái chờ duyệt.')
            
            # Lấy vai trò mới
            vai_tro_moi = self.vai_tro_dao.find_by_ten_vai_tro(session=session, ten_vai_tro=vai_tro_ten)
            if not vai_tro_moi:
                raise Exception(f'Vai trò {vai_tro_ten} không tồn tại.')
            
            if vai_tro_ten == 'VODANH':
                raise Exception('Không thể gán vai trò VODANH.')
            
            # Gán vai trò mới
            tai_khoan.vai_tro = vai_tro_moi
            
            # Gán info người dùng tương ứng với role (Phục vụ, Đầu bếp...)
            nguoi_dung = tai_khoan.nguoi_dung
            if not nguoi_dung:
                raise Exception('Người dùng không tồn tại.')
            
            # Lưu thông tin cũ
            ho_ten = nguoi_dung.ho_ten
            
            # Xóa nguoi_dung cũ (base class)
            session.delete(nguoi_dung)
            session.flush()
            
            # Tạo nguoi_dung mới với đúng subclass
            new_nguoi_dung = self._tao_nguoi_dung_theo_vai_tro(vai_tro_ten, ho_ten, tai_khoan.id)
            session.add(new_nguoi_dung)
            
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)
            
            return {
                'id': tai_khoan.id,
                'ten_tai_khoan': tai_khoan.ten_tai_khoan,
                'email': tai_khoan.email,
                'vai_tro': vai_tro_moi.vai_tro.value,
                'ho_ten': ho_ten,
                'message': 'Duyệt tài khoản thành công.'
            }
    
    def _tao_nguoi_dung_theo_vai_tro(self, vai_tro_ten: str, ho_ten: str, tai_khoan_id: int):
        # Factory này để tạo đúng loại nhân viên (Phục vụ, Đầu bếp...)
        from app.data.models import PhucVu, LeTan, DauBep, ThuNgan, QuanLy, NguoiDung
        
        if vai_tro_ten == 'PHUCVU':
            return PhucVu(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'LETAN':
            return LeTan(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'DAUBEP':
            return DauBep(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'THUNGAN':
            return ThuNgan(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        elif vai_tro_ten == 'QUANLY':
            return QuanLy(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
        else:
            return NguoiDung(ho_ten=ho_ten, tai_khoan_id=tai_khoan_id)
    
    def xu_ly_tu_choi_tai_khoan(self, admin_id: int, tai_khoan_id: int) -> bool:
        # Không thích thì khóa luôn cho nhanh
        with transaction_manager.transaction('Lỗi khi từ chối tài khoản') as session:
            # Kiểm tra admin
            admin = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=admin_id)
            if not admin or admin.vai_tro.vai_tro != TenVaiTro.ADMIN:
                raise Exception('Bạn không có quyền từ chối tài khoản.')
            
            # Lấy tài khoản cần từ chối
            tai_khoan = self.tai_khoan_dao.find_by_id(session=session, tai_khoan_id=tai_khoan_id)
            if not tai_khoan:
                raise Exception('Tài khoản không tồn tại.')
            
            # Khóa tài khoản
            tai_khoan.trang_thai = TrangThaiTaiKhoan.KHOA
            
            self.tai_khoan_dao.save(session=session, tai_khoan=tai_khoan)
            
            return True


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
    def __init__(self, bo_chon_nhan_vien: IBoChonNhanVien, phien_ban_dao: IPhienBanDAO, nguoidung_dao: INguoiDungDAO, ban_dao: IBanDAO, dat_ban_dao: IDatBanDAO):
        self.phien_ban_dao = phien_ban_dao
        self.nguoidung_dao = nguoidung_dao
        self.ban_dao = ban_dao
        self.bo_chon_nhan_vien = bo_chon_nhan_vien
        self.dat_ban_dao = dat_ban_dao

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
    
    def xu_ly_dat_ban(self, letan_id: int, dat_ban_create_schema: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi xử lý đặt bàn") as session:
            ds_ban = self.get_ban_details(ban_schemas_in=dat_ban_create_schema['ds_ban'])

            print(ds_ban)
            if not len(ds_ban):
                raise Exception("Vui lòng chọn ít nhất 1 bàn")
            
            for ban in ds_ban:
                if not ds_ban[0].kiem_tra_thuoc_cung_khu_vuc(ban=ban):
                    raise Exception('Trường hợp đặt nhiều bàn thì phải cùng 1 khu vực! Vui lòng chọn lại!')
                if not ban.kiem_tra_thoi_gian_danh_dau(tg=dat_ban_create_schema['tg_den']):
                    raise Exception(f'Bàn {ban.ten} hiện đang chuẩn bị cho khách đặt trước! Vui lòng chọn lại!')

            letan = self.nguoidung_dao.find_by_id(session=session, id=letan_id)
            if not letan:
                raise Exception('Không tồn tại lễ tân này trong hệ thống!')
            print("QUA ĐƯỢC ĐÂY")
            # Extract customer info from nested khach_hang object
            khach_hang = dat_ban_create_schema['khach_hang']
            ten_khach = khach_hang['ten']
            sdt = khach_hang['sdt']
            so_luong = khach_hang['so_luong']
            
            db = None
            if isinstance(letan, LeTan):
                db = letan.dat_ban(tg_den=dat_ban_create_schema['tg_den'], ten_khach=ten_khach\
                                   , sdt=sdt, so_luong=so_luong, ds_ban=ds_ban)

                self.dat_ban_dao.save(session=session, dat_ban=db)

                print(db)
            
            dat_ban_out = dat_ban_out_schema.dump(db)
            print(dat_ban_out)

            return dat_ban_out
            
            

                
            

            

    def xu_ly_chon_ban(self, letan_id: int, ban_schemas_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Gán bàn cho khách lúc mới vào (khai trương phiên mới)
        with transaction_manager.transaction('Lỗi khi xử lý chọn bàn') as session:
            phien = None
            
            ds_ban = self.get_ban_details(ban_schemas_in=ban_schemas_in) #Lấy ra danh sách bàn từ client chỉ định sang
            
            tg_bat_dau = dt.datetime.now() # Lấy giờ hiện tại để bắt đầu tính tiền/phục vụ :v

            if not len(ds_ban):
                raise Exception('Vui lòng chọn ít nhất 1 bàn để có thể đánh dấu!')

            

            for ban in ds_ban:
                if not ban.kiem_tra_ban_trong(): # Check xem bàn có ai đang ngồi chưa
                    raise Exception(f'Bàn {ban.ten} hiện đang được sử dụng! Vui lòng chọn lại!')
                if not ds_ban[0].kiem_tra_thuoc_cung_khu_vuc(ban=ban): # Phải cùng một tầng/khu vực mới dễ quản lý
                    raise Exception('Trường hợp đặt nhiều bàn thì phải cùng 1 khu vực! Vui lòng chọn lại!')
                if not ban.kiem_tra_thoi_gian_danh_dau(tg=tg_bat_dau): # Check xem sắp tới giờ của khách đặt trước chưa
                    raise Exception(f'Bàn {ban.ten} hiện đang chuẩn bị cho khách đặt trước! Vui lòng chọn lại!')
                
            letan = self.nguoidung_dao.find_by_id(session=session, id=letan_id) #Lấy ra lễ tân từ client chỉ định sang
            ds_phucvu = self.nguoidung_dao.find_by_khuvuc_id(session=session, khuvuc_id=ds_ban[0].khu_vuc_id) #Lấy ra danh sách nhân viên phục vụ từ client chỉ định sang
            

            if not letan:
                raise Exception('Không tồn tại lễ tân này trong hệ thống!')
            if not len(ds_phucvu):
                raise Exception('Không tồn tại nhân viên nào của khu vực để phục vụ!')
            
            if isinstance(letan, LeTan):
                phien = letan.tao_phien(tg_bat_dau=tg_bat_dau)
            else:
                print(letan.type)
                raise Exception('Không phải lễ tân để có thể chọn bàn!')

            khung_gio = phien.khung_gio

            for ban in ds_ban:
                ban.them_khung_gio(khung_gio=khung_gio) # Đánh dấu khung giờ cho từng bàn
            


            for ban in ds_ban: # Điều phối nhân viên phục vụ (ai đang rảnh thì giao việc)
                phucvu = self.bo_chon_nhan_vien.chon_phuc_vu(ds_phucvu=ds_phucvu) # Ưu tiên ông đang ít bàn nhất
                phien.phan_cong(phuc_vu=phucvu, ban=ban)
            
            self.phien_ban_dao.save(session=session, phien=phien)

            ds_ban_dto = ds_ban_out_schema.dump(ds_ban)

            
            return ds_ban_dto

    def lay_danh_sach_dat_ban_active(self, letan_id: int) -> List[Dict[str, Any]]:
        # Xem những ông nào đã đặt nhưng chưa tới
        with transaction_manager.transaction('Lỗi khi lấy danh sách đặt bàn') as session:
            letan = self.nguoidung_dao.find_by_id(session=session, id=letan_id)
            if not letan:
                raise Exception('Không tồn tại lễ tân này trong hệ thống!')
            
            ds_dat_ban = self.dat_ban_dao.find_all_active(session=session)
            ds_dat_ban_out = dat_ban_out_schema.dump(ds_dat_ban, many=True)
            
            return ds_dat_ban_out
    
    def xu_ly_xac_nhan_khach_den(self, letan_id: int, dat_ban_id: int) -> Dict[str, Any]:
        """
        Xác nhận khách đặt bàn đã đến.
        Logic xử lý khách đến trễ: dùng thời gian hiện tại, kiểm tra xung đột với các khung giờ khác.
        """
        with transaction_manager.transaction('Lỗi khi xác nhận khách đến') as session:
            # 1. Validate lễ tân và đặt bàn
            letan = self.nguoidung_dao.find_by_id(session=session, id=letan_id)
            if not letan:
                raise Exception('Không tồn tại lễ tân này trong hệ thống!')
            if not isinstance(letan, LeTan):
                raise Exception('Không phải lễ tân để có thể xác nhận!')
            
            dat_ban = self.dat_ban_dao.find_by_id(session=session, dat_ban_id=dat_ban_id)
            if not dat_ban:
                raise Exception('Đặt bàn không tồn tại!')
            if dat_ban.trang_thai != TrangThai.MO:
                raise Exception('Đặt bàn này đã được xử lý hoặc đã hủy!')
            
            ds_ban = dat_ban.ds_ban_dat
            if not len(ds_ban):
                raise Exception('Không có bàn nào trong đặt bàn này!')
            
            # 2. Thời gian hiện tại (khách đến)
            tg_bat_dau = dt.datetime.now()
            
            # 3. Kiểm tra bàn trống và xung đột khung giờ
            for ban in ds_ban:
                if not ban.kiem_tra_ban_trong():
                    raise Exception(f'Bàn {ban.ten} hiện đang có khách! Không thể xác nhận.')
                
                # Kiểm tra xung đột với các khung giờ khác (bỏ qua khung giờ đặt bàn hiện tại)
                for kg in ban.ds_khung_gio:
                    if kg.id != dat_ban.khung_gio_id:
                        if not kg.thoi_gian_hop_le(tg=tg_bat_dau):
                            raise Exception(f'Bàn {ban.ten} có lịch đặt trước lúc {kg.tg_bat_dau.strftime("%H:%M")}. Khách đến trễ quá, không thể xử lý!')
            
            # Bọc lại data theo schema cho chuẩn bài
            # 4. Lấy danh sách phục vụ của khu vực
            ds_phucvu = self.nguoidung_dao.find_by_khuvuc_id(session=session, khuvuc_id=ds_ban[0].khu_vuc_id)
            if not len(ds_phucvu):
                raise Exception('Không tồn tại nhân viên nào của khu vực để phục vụ!')
            
            # 5. Hủy khung giờ đặt bàn cũ
            khung_gio_dat_ban = dat_ban.khung_gio
            if khung_gio_dat_ban:
                khung_gio_dat_ban.trang_thai = TrangThai.HOANTHANH
            
            # 6. Tạo phiên bàn mới (giống xu_ly_chon_ban)
            phien = letan.tao_phien(tg_bat_dau=tg_bat_dau)
            khung_gio_an = phien.khung_gio
            
            # 7. Thêm khung giờ ăn cho các bàn và đánh dấu có khách
            for ban in ds_ban:
                ban.them_khung_gio(khung_gio=khung_gio_an)
            
            # 8. Phân công phục vụ
            for ban in ds_ban:
                phucvu = self.bo_chon_nhan_vien.chon_phuc_vu(ds_phucvu=ds_phucvu)
                phien.phan_cong(phuc_vu=phucvu, ban=ban)
            
            # 9. Cập nhật trạng thái đặt bàn
            dat_ban.trang_thai = TrangThai.HOANTHANH
            
            # 10. Lưu phiên
            self.phien_ban_dao.save(session=session, phien=phien)
            
            # 11. Trả về kết quả
            result = {
                'dat_ban': dat_ban_out_schema.dump(dat_ban),
                'ds_ban': ds_ban_out_schema.dump(ds_ban),
                'phien_ban_id': phien.id,
                'message': f'Xác nhận thành công! Phiên #{phien.id} đã được tạo.'
            }
            
            return result


class PhienBanService(IPhienBanService):
    @inject
    def __init__(self, them_mon_service: IThemMonService, phien_ban_dao: IPhienBanDAO, nguoi_dung_dao: INguoiDungDAO, phieu_mon_read_dao: IPhieuMonReadDAO, mon_ghi_read_dao: IMonGhiReadDAO, yeu_cau_read_dao: IYeuCauReadDAO):
        self.phien_ban_dao = phien_ban_dao
        self.nguoi_dung_dao = nguoi_dung_dao
        self.them_mon_service = them_mon_service
        self.phieu_mon_read_dao = phieu_mon_read_dao
        self.mon_ghi_read_dao = mon_ghi_read_dao
        self.yeu_cau_read_dao = yeu_cau_read_dao

    def lay_toan_bo_phieu_mon_da_gui_bep(self, dau_bep_id: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi lấy toàn bộ phiếu món đã gửi') as session:
            dau_bep = self.nguoi_dung_dao.find_by_id(session=session, id=dau_bep_id)
            if not dau_bep:
                raise Exception('Bạn không phải đầu bếp để có thể lấy ra toàn bộ phiếu món đã gửi bếp.')
            
            ds_phieu_mon = self.phieu_mon_read_dao.find_by_trang_thai_mo(session=session)
            ds_phieu_mon_out_less = phieu_mon_out_less_schema.dump(ds_phieu_mon, many=True)
            return ds_phieu_mon_out_less
            

    def lay_phien_ban_chi_tiet(self, phien_ban_id: int, user_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi đang lấy chi tiết phiên bàn') as session:
            phien_ban = self.phien_ban_dao.find_by_id(session=session, phien_ban_id=phien_ban_id)
            if not phien_ban:
                raise Exception('Phiên bàn không tồn tại.')
            if not phien_ban.kiem_tra_phien_dang_hoat_dong():
                raise Exception('Phiên bàn này đã đóng.')
            # Chỉ ông nào có liên quan (Lễ tân/Phục vụ) mới được xem chi tiết
            # if not phien_ban.thuoc_phien_ban(user_id=user_id):
            #     raise Exception('Bạn không thuộc về phiên bàn này.')
            phien_ban_out = phien_ban_out_schema.dump(phien_ban)

            return phien_ban_out
            

    def lay_danh_sach_phien_cua_phuc_vu(self, phucvu_id: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi đang lấy danh sách phiên của phục vụ') as session:
            ds_phien_ban = self.phien_ban_dao.find_by_phucvu_id(session=session, phucvu_id=phucvu_id)
            
            ds_phien_ban_out_less = phien_ban_out_less_schema.dump(ds_phien_ban, many=True)
            return ds_phien_ban_out_less

    def lay_danh_sach_phien_cua_thu_ngan(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi đang lấy danh sách phiên của thu ngân') as session:
            thu_ngan = self.nguoi_dung_dao.find_by_id(session=session, id=thu_ngan_id)
            if not thu_ngan:
                raise Exception('Không tồn tại thu ngân.')
            if not isinstance(thu_ngan, ThuNgan):
                raise Exception('Người dùng không thuộc thu ngân.')
            ds_phien_ban = self.phien_ban_dao.find_by_mo(session=session)
            ds_phien_ban_out_less = phien_ban_out_less_schema.dump(ds_phien_ban, many=True)

            return ds_phien_ban_out_less

    def xu_ly_dam_nhan_phien_ban(self, phien_ban_id: int, phucvu_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi xử lý đảm nhận') as session:
            phucvu = None
            phien_ban = self.phien_ban_dao.find_by_id(session=session, phien_ban_id=phien_ban_id)
            if not phien_ban:
                raise Exception('Phiên bàn không tồn tại.')
            if not phien_ban.kiem_tra_phien_dang_hoat_dong():
                raise Exception('Phiên bàn này không hoạt động.')

            if phien_ban.kiem_tra_co_nguoi_dam_nhan():
                if not phien_ban.kiem_tra_nguoi_dam_nhan(phucvu_id=phucvu_id):
                    raise Exception('Phiên bàn này đã có người khác đảm nhận.')
                else:
                    raise Exception('Phục vụ hiện đang đảm nhận phiên này.')
            else:
                phucvu = self.nguoi_dung_dao.find_by_id(session=session, id=phucvu_id)
                if not phucvu:
                    raise Exception('Không tồn tại phục vụ.')
                if not isinstance(phucvu, PhucVu):
                    raise Exception('Người dùng không thuộc phục vụ.')
                if not phucvu.kiem_tra_chua_dam_nhan_phien_nao(): # Mỗi ông chỉ nên ôm 1 phiên tại 1 thời điểm thôi
                    raise Exception('Phục vụ hiện đang đảm nhận bàn khác, vui lòng không đảm nhận thêm.')
                phien_ban.chon_phuc_vu_dam_nhan(phuc_vu=phucvu)

                self.phien_ban_dao.save(session=session, phien=phien_ban)

                phien_ban_out = phien_ban_out_less_schema.dump(phien_ban)

                return phien_ban_out
            
    def xu_ly_tao_phieu_mon(self, phien_ban_id: int, phucvu_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi tạo phiếu món') as session:
            phien_ban = self.phien_ban_dao.find_by_id(session=session, phien_ban_id=phien_ban_id)
            if not phien_ban:
                raise Exception('Phiên bàn không tồn tại.')
            if not phien_ban.kiem_tra_phien_dang_hoat_dong():
                raise Exception('Phiên hiện đã đóng.')
            if not phien_ban.kiem_tra_co_nguoi_dam_nhan():
                raise Exception('Phiên bàn hiện chưa có người đảm nhận.')
            if not phien_ban.kiem_tra_nguoi_dam_nhan(phucvu_id=phucvu_id):
                raise Exception('Phiên bàn không phải do phục vụ này đảm nhận.')
            if phien_ban.dang_co_phieu_mo():
                raise Exception('Hiện tại phiên bàn đang có 1 phiếu mở, vui lòng xử lý phiếu đấy trước khi mở phiếu khác.')
            if not phien_ban.chua_ton_tai_doanh_thu(): #Phiên bàn đã tồn tại doanh thu, chuẩn bị thanh toán
                raise Exception("Phiên bàn đã tồn tại doanh thu cho chuẩn bị thanh toán, không thể tạo thêm phiếu món.")
            
            phien_ban.tao_phieu_mon()
            self.phien_ban_dao.save(session=session, phien=phien_ban)
            phieu_mon = phien_ban.ds_phieu_mon[-1]
            phieu_mon_out = phieu_mon_out_schema.dump(phieu_mon)
            return phieu_mon_out
            
    
    def xu_ly_them_mon_ghi_phieu_mon(self, phucvu_id: int, phieu_mon_id: int, mon_ghi_create_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi thêm món vào phiếu') as session:
            if not len(mon_ghi_create_schemas['ds_mon_ghi']):  #Nếu như bên client gửi sang phiếu món mà không có món nào thì sẽ quăng ra lỗi nha
                raise Exception('Phải thêm ít nhất 1 món.')
            
            phien_ban = self.phien_ban_dao.find_by_phieu_mon_id(session=session, phieu_mon_id=phieu_mon_id)
            if not phien_ban:
                raise Exception('Phiên bàn không tồn tại.')
            if not phien_ban.kiem_tra_phien_dang_hoat_dong():
                raise Exception('Phiên bàn đã đóng.')
            
            if not phien_ban.kiem_tra_nguoi_dam_nhan(phucvu_id=phucvu_id): #KIểm tra xem người gửi phiếu có phải người đảm nhận không
                raise Exception('Bạn không phải người đảm nhận của phiên bàn này để có thể thêm món vào phiếu')
            
            phieu_mon = phien_ban.lay_phieu_mon(phieu_mon_id=phieu_mon_id)
            
            if not phieu_mon:
                raise Exception('Không tồn tại phiếu món thuộc phiên bàn.')
            if not phieu_mon.is_phieu_mo():
                raise Exception('Hiện tại phiếu không mở.')
            
            phieu_mon = self.them_mon_service.them_mon_ghi(phieu_mon=phieu_mon, mon_ghi_create_schemas=mon_ghi_create_schemas)
            phieu_mon.gui_phieu() #Gửi phiếu sau khi đã thêm các món ghi vào phiếu

            self.phien_ban_dao.save(session=session, phien=phien_ban) #Lưu phiên bàn xuống DB

            phieu_mon_out = phieu_mon_out_schema.dump(phieu_mon)
            phieu_mon_out_less = phieu_mon_out_less_schema.dump(phieu_mon)
            return phieu_mon_out, phieu_mon_out_less

            
            
            

    def lay_chi_tiet_phieu_mon(self, phien_ban_id: int, phieu_mon_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi lấy ra chi tiết phiếu món') as session:
            phien_ban = self.phien_ban_dao.find_by_id(session=session, phien_ban_id=phien_ban_id)
            if not phien_ban:
                raise Exception('Phiên bàn không tồn tại.')
            phieu_mon = phien_ban.lay_phieu_mon(phieu_mon_id=phieu_mon_id)
            if not phieu_mon:
                raise Exception('Phiếu món không tồn tại.')

            phieu_mon_out = phieu_mon_out_schema.dump(phieu_mon)
            return phieu_mon_out
        
    def lay_chi_tiet_phieu_mon_cho_bep(self, dau_bep_id: int, phieu_mon_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi lấy ra chi tiết phiếu món') as session:
            dau_bep = self.nguoi_dung_dao.find_by_id(session=session, id=dau_bep_id)
            if not dau_bep:
                raise Exception('Bạn không phải đầu bếp để có thể lấy ra toàn bộ phiếu món đã gửi bếp.')
            phieu_mon = self.phieu_mon_read_dao.find_by_id(session=session, phieu_mon_id=phieu_mon_id)
            if not phieu_mon:
                raise Exception('Phiếu món không tồn tại.')

            phieu_mon_out = phieu_mon_out_schema.dump(phieu_mon)
            return phieu_mon_out
        
    def xu_ly_cap_nhat_trang_thai_mon(self, dau_bep_id: int, mon_ghi_id: int, mon_ghi_status_update: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi cập nhật trạng thái món trong phiếu') as session:
            dau_bep = self.nguoi_dung_dao.find_by_id(session=session, id=dau_bep_id)
            if not dau_bep:
                raise Exception('Bạn không phải đầu bếp để có thể lấy ra toàn bộ phiếu món đã gửi bếp.')
            phien_ban = self.phien_ban_dao.find_by_mon_ghi_id(session=session, mon_ghi_id=mon_ghi_id)

            print("Phiên bàn ID: ", phien_ban.id)
            
            if not phien_ban:
                raise Exception('Không tồn tại món ghi thuộc về phiếu của phiên bàn.')
            status = None
            if mon_ghi_status_update['trang_thai'] == 'HOANTHANH':
                status = HoanThanhMon()
            elif mon_ghi_status_update['trang_thai'] == 'HUY':
                status = HuyMon()
            
            if not phien_ban.cap_nhat_mon_ghi(status=status, mon_ghi_id=mon_ghi_id): #Tức là cập nhật xong, nhưng chưa hoàn thành phiếu
                mon_ghi = self.mon_ghi_read_dao.find_by_id(session=session, mon_ghi_id=mon_ghi_id)
                mon_ghi_out = mon_ghi_out_schema.dump(mon_ghi)

                return mon_ghi_out
            else:
                mon_ghi = self.mon_ghi_read_dao.find_by_id(session=session, mon_ghi_id=mon_ghi_id)
                
                phieu_mon = mon_ghi.phieu_mon
                phuc_vu_dam_nhan = phieu_mon.phien_ban.nguoi_dam_nhan
                tb = phuc_vu_dam_nhan.\
                    them_thong_bao(HoanThanhMon(), tieu_de='Bếp đã hoàn thành', noi_dung=f'Đầu bếp đã hoàn thành các món ăn trong phiếu #{phieu_mon.id}, vui lòng đến quầy và mang ra cho khách'\
                                   , link=f'http://127.0.0.1:5000/phien-ban/{phieu_mon.phien_ban_id}/phieu-mon/{phieu_mon.id}')
                
                self.nguoi_dung_dao.save(session=session, nguoi_dung=phuc_vu_dam_nhan)
                phieu_mon_out = phieu_mon_out_schema.dump(phieu_mon)
                tb_out = thong_bao_out_schema.dump(tb)
                return phieu_mon_out, tb_out

    def xu_ly_tao_yeu_cau_mon_ghi(self, phuc_vu_id: int, mon_ghi_id: int, yc_create) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi đang tạo yêu cầu") as session:
            mon_ghi = self.mon_ghi_read_dao.find_by_id(session=session, mon_ghi_id=mon_ghi_id)
            
            if not mon_ghi.kiem_tra_phuc_vu(phuc_vu_id=phuc_vu_id):
                raise Exception("Bạn không phải người đảm nhận của phiên để có thể gửi yêu cầu cho quản lý.")
            yc = mon_ghi.tao_yeu_cau(ly_do=yc_create['ly_do'])

            phien_ban = mon_ghi.phieu_mon.phien_ban
            self.phien_ban_dao.save(session=session, phien=phien_ban)

            yc_out = yc_mon_ghi_out_schema.dump(yc)

            return yc_out
    
    def lay_danh_sach_yeu_cau(self, quan_ly_id: int) -> List[Dict[str, Any]]:
        # Quản lý xem có đứa nào gửi yêu cầu hỗ trợ/hủy món không
        with transaction_manager.transaction("Lỗi khi đang lấy danh sách yêu cầu") as session:
            #Kiểm tra quản lý --> chưa làm
            ds_yeu_cau = self.yeu_cau_read_dao.find_all_by_pending(session=session)

            print(ds_yeu_cau)
            ds_yc_out = convert_yeu_cau(ds_yeu_cau=ds_yeu_cau)

            return ds_yc_out

    def xu_ly_chap_thuan_yeu_cau(self, quan_ly_id: int, yeu_cau_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi đang chấp thuận yêu cầu") as session:
            yeu_cau = self.yeu_cau_read_dao.find_by_id(session=session, yeu_cau_id=yeu_cau_id)
            if not yeu_cau:
                raise Exception("Yêu cầu không tồn tại.")
            
            yeu_cau.chap_thuan(quan_ly_duyet_id=quan_ly_id)
            self.yeu_cau_read_dao.save(session=session, yeu_cau=yeu_cau)

            yc_out = yc_mon_ghi_out_schema.dump(yeu_cau)
            return yc_out

    def xu_ly_tu_choi_yeu_cau(self, quan_ly_id: int, yeu_cau_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi đang từ chối yêu cầu") as session:
            yeu_cau = self.yeu_cau_read_dao.find_by_id(session=session, yeu_cau_id=yeu_cau_id)
            if not yeu_cau:
                raise Exception("Yêu cầu không tồn tại.")
            
            yeu_cau.tu_choi(quan_ly_duyet_id=quan_ly_id)
            self.yeu_cau_read_dao.save(session=session, yeu_cau=yeu_cau)

            yc_out = yc_mon_ghi_out_schema.dump(yeu_cau)
            return yc_out




            




            



                



            
            
class ThemMonService(IThemMonService):
    @inject
    def __init__(self, tuy_chon_mon_dao: ITuyChonMonReadDAO, thuc_don_dao: IThucDonDAO):
        self.tuy_chon_mon_dao = tuy_chon_mon_dao
        self.thuc_don_dao = thuc_don_dao
    
    def them_mon_ghi(self, phieu_mon: PhieuMon, mon_ghi_create_schemas: List[Dict[str, Any]]) -> PhieuMon:
        with transaction_manager.transaction('Lỗi khi xử lý thêm món vào phiếu') as session:
            thuc_don = self.thuc_don_dao.find_first(session=session)
            if not thuc_don:
                raise Exception("Thực đơn chưa tồn tại để chọn món.")
            
            hmap = {} # Dùng map để lọc trùng tùy chọn món cho nhanh
            ds_tuy_chon_id = [] #Dùng để lưu danh sách tùy chọn món ID từ Hmap
            for mon_ghi in mon_ghi_create_schemas['ds_mon_ghi']:
                for tuy_chon in mon_ghi['ds_tuy_chon']:
                    if not hmap.get(tuy_chon['tuy_chon_id']):
                        hmap[f'{tuy_chon['tuy_chon_id']}'] = tuy_chon['tuy_chon_id'] 
            
            for k, v in hmap.items():
                ds_tuy_chon_id.append(v) #Gắn vào danh sách để đưa xuống tầng DB
            
            ds_tuy_chon = self.tuy_chon_mon_dao.find_by_ids(session=session, tuy_chon_mon_ids=ds_tuy_chon_id)

            found_ids = {tuy_chon.id for tuy_chon in ds_tuy_chon}
            requested_ids = {id for id in ds_tuy_chon_id}

            invalid_ids = requested_ids - found_ids

            if invalid_ids:
                raise Exception('Tùy chọn món không hợp lệ, vui lòng chọn lại.')
            
            for tuy_chon in ds_tuy_chon:
                hmap[f'{tuy_chon.id}'] = tuy_chon #Lưu ngược lại trong hmap để khi duyệt qua lại có thể truy vấn ra
            

            
            for mon_ghi in mon_ghi_create_schemas['ds_mon_ghi']:
                ds_tc = []
                mo_ta_mon = thuc_don.lay_mo_ta_mon(mo_ta_mon_id=mon_ghi['mo_ta_mon_id']) #Lấy ra mô tả món tương ứng để liên kết cho món ghi, xong lưu món ghi xuống DB
                if not mo_ta_mon:
                    raise Exception('Món không tồn tại.')
                for tuy_chon_requested in mon_ghi['ds_tuy_chon']:
                    ds_tc.append(hmap[f'{tuy_chon_requested['tuy_chon_id']}']) #Lấy ra tùy chọn món từ hmap để liên kết cho món ghi
                phieu_mon.them_mon_ghi(so_luong=mon_ghi['so_luong'], ghi_chu=mon_ghi['ghi_chu'], mo_ta_mon=mo_ta_mon, ds_tuy_chon=ds_tc)

            return phieu_mon

                
            

            

        

class ThucDonService(IThucDonService):
    @inject
    def __init__(self, thuc_don_dao: IThucDonDAO):
        self.thuc_don_dao = thuc_don_dao

    def lay_thuc_don(self) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi lấy ra thực đơn') as session:
            thuc_don = self.thuc_don_dao.find_first(session=session)
            thuc_don_out = thuc_don_out_schema.dump(thuc_don)
            print(thuc_don_out)
            return thuc_don_out
        

class DoanhThuService(IDoanhThuService):
    @inject
    def __init__(self, phien_ban_dao: IPhienBanDAO, nguoi_dung_dao: INguoiDungDAO, khuyen_mai_dao: IKhuyenMaiDAO, doanh_thu_dao: IDoanhThuDAO, thue_dao: ICauHinhThueDAO, doanh_thu_thanh_toan_service: IDoanhThuThanhToanService):
        self.nguoi_dung_dao = nguoi_dung_dao
        self.khuyen_mai_dao = khuyen_mai_dao
        self.doanh_thu_thanh_toan_service = doanh_thu_thanh_toan_service
        self.thue_dao = thue_dao
        self.doanh_thu_dao = doanh_thu_dao
        self.phien_ban_dao = phien_ban_dao
    
    def lay_doanh_thu_cua_phien_ban(self, thu_ngan_id: int, phien_ban_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi đang lấy doanh thu của phiên bàn') as session:
            doanh_thu = self.doanh_thu_dao.find_by_phien_ban_id(session=session, phien_ban_id=phien_ban_id)

            if not doanh_thu:
                return None
            
            if doanh_thu.thu_ngan_id != thu_ngan_id:
                raise Exception("Bạn không thuộc phiên thanh toán này.")
            return doanh_thu
            
    
    def lay_doanh_thu_chi_tiet(self, thu_ngan_id: int, doanh_thu_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi lấy doanh thu') as session:
            doanh_thu = self.doanh_thu_dao.find_by_id(session=session, doanh_thu_id=doanh_thu_id)

            if not doanh_thu:
                raise Exception("Doanh thu không tồn tại.")
            if doanh_thu.thu_ngan_id != thu_ngan_id:
                raise Exception("Bạn không thuộc phiên thanh toán này.")
            
            doanh_thu_out = doanh_thu_out_schema.dump(doanh_thu)
            return doanh_thu_out

    def xu_ly_tam_tinh(self, thu_ngan_id: int, phien_ban_id: int) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi đang xử lý tạm tính') as session:
            data_preview = None
            thu_ngan = self.nguoi_dung_dao.find_by_id(session=session, id=thu_ngan_id)
            if not thu_ngan:
                raise Exception("Không tồn tại thu ngân để xử lý")
            
            if not isinstance(thu_ngan, ThuNgan):
                raise Exception('Không thuộc vai trò thu ngân để làm điều này.')
            
            phien_ban = self.phien_ban_dao.find_by_id(session=session, phien_ban_id=phien_ban_id)

            if not phien_ban.khong_co_phieu_mon_dang_nau():
                raise Exception("Hiện tại đang có phiếu món đang nấu, không thể tạm tính.")
            
            doanh_thu = None
            
            if phien_ban.is_doanh_thu():
                doanh_thu = phien_ban.doanh_thu
                if doanh_thu.thu_ngan_id != thu_ngan_id:
                    raise Exception("Doanh thu này không phải của bạn.")
            else:
                doanh_thu = thu_ngan.tao_doanh_thu(phien_ban_id=phien_ban_id)
                self.nguoi_dung_dao.save(session=session, nguoi_dung=thu_ngan)


            
            ds_khuyen_mai = self.khuyen_mai_dao.find_by_hoat_dong_and_tu_dong_ap_dung(session=session)
            thue = self.thue_dao.find_by_hoat_dong(session=session)
            if not thue:
                raise Exception("Quản trị viên hệ thống chưa cấu hình thuế, vui lòng liên hệ để hỗ trợ.")
            
            data_preview = self.doanh_thu_thanh_toan_service.tao_preview(doanh_thu=doanh_thu, thue=thue, ds_khuyen_mai=ds_khuyen_mai)


            return data_preview

    def lay_doanh_thu_cua_thu_ngan(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction('Lỗi khi đang lấy doanh thu của thu ngân') as session:
            thu_ngan = self.nguoi_dung_dao.find_by_id(session=session, id=thu_ngan_id)
            if not thu_ngan:
                raise Exception('Không tồn tại thu ngân.')
            if not isinstance(thu_ngan, ThuNgan):
                raise Exception('Không thuộc vai trò thu ngân để làm điều này.')
            ds_doanh_thu = thu_ngan.ds_doanh_thu_chua_hoan_thanh
            ds_doanh_thu_out_less = doanh_thu_out_less_schema.dump(ds_doanh_thu, many=True)
            return ds_doanh_thu_out_less
        
    def xu_ly_ap_dung_khuyen_mai(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi áp dụng khuyến mãi.') as session:
            doanh_thu = self.doanh_thu_dao.find_by_id(session=session, doanh_thu_id=doanh_thu_id)
            if not doanh_thu:
                raise Exception('Không tồn tại doanh thu.')
            if doanh_thu.thu_ngan_id != thu_ngan_id:
                raise Exception("Không phải thu ngân thuộc Doanh Thu này.")
            

            ds_khuyen_mai_tu_dong = self.khuyen_mai_dao.find_by_hoat_dong_and_tu_dong_ap_dung(session=session)
            ds_khuyen_mai_tuy_chon = self.khuyen_mai_dao.find_by_ids(session=session, khuyen_mai_ids=khuyen_mai_in_schema['ids'])

            if not len(ds_khuyen_mai_tuy_chon):
                raise Exception("Không tồn tại khuyến mãi theo chỉ định để áp dụng.")
            
            thue = self.thue_dao.find_by_hoat_dong(session=session)
            if not thue:
                raise Exception("Quản trị viên hệ thống chưa cấu hình thuế, vui lòng liên hệ để hỗ trợ.")
            data_preview = self.doanh_thu_thanh_toan_service.tao_preview(doanh_thu=doanh_thu, thue=thue, ds_khuyen_mai=ds_khuyen_mai_tu_dong, ds_khuyen_mai_tuy_chon=ds_khuyen_mai_tuy_chon)

            return data_preview

        
    def xu_ly_thanh_toan_tien_mat(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi đang thanh toán tiền mặt') as session:
            doanh_thu = self.doanh_thu_dao.find_by_id(session=session, doanh_thu_id=doanh_thu_id)
            if not doanh_thu:
                raise Exception('Không tồn tại doanh thu.')
            if doanh_thu.thu_ngan_id != thu_ngan_id:
                raise Exception("Không phải thu ngân thuộc Doanh Thu này.")
            
            ds_khuyen_mai_tuy_chon = self.khuyen_mai_dao.find_by_ids(session=session, khuyen_mai_ids=khuyen_mai_in_schema['ids'])
            ds_khuyen_mai_tu_dong = self.khuyen_mai_dao.find_by_hoat_dong_and_tu_dong_ap_dung(session=session)

            thue = self.thue_dao.find_by_hoat_dong(session=session)
            if not thue:
                raise Exception("Quản trị viên hệ thống chưa cấu hình thuế, vui lòng liên hệ để hỗ trợ.")
            
            self.doanh_thu_thanh_toan_service.xu_ly_thanh_toan_doanh_thu(doanh_thu=doanh_thu, thue=thue, ds_khuyen_mai_tu_dong=ds_khuyen_mai_tu_dong, ds_khuyen_mai_tuy_chon=ds_khuyen_mai_tuy_chon)

            doanh_thu_out = doanh_thu_out_schema.dump(doanh_thu)
            
            return doanh_thu_out
        
    def xu_ly_thanh_toan_online(self, thu_ngan_id: int, doanh_thu_id: int, khuyen_mai_in_schema: Dict[str, Any]) -> Dict[str, Any]:
        with transaction_manager.transaction('Lỗi khi đang thanh toán online') as session:
            doanh_thu = self.doanh_thu_dao.find_by_id(session=session, doanh_thu_id=doanh_thu_id)
            if not doanh_thu:
                raise Exception('Không tồn tại doanh thu.')
            if doanh_thu.thu_ngan_id != thu_ngan_id:
                raise Exception("Không phải thu ngân thuộc Doanh Thu này.")
            
            ds_khuyen_mai_tuy_chon = self.khuyen_mai_dao.find_by_ids(session=session, khuyen_mai_ids=khuyen_mai_in_schema['ids'])
            ds_khuyen_mai_tu_dong = self.khuyen_mai_dao.find_by_hoat_dong_and_tu_dong_ap_dung(session=session)

            thue = self.thue_dao.find_by_hoat_dong(session=session)
            if not thue:
                raise Exception("Quản trị viên hệ thống chưa cấu hình thuế, vui lòng liên hệ để hỗ trợ.")
            
            info = self.doanh_thu_thanh_toan_service.xu_ly_thanh_toan_doanh_thu_online(doanh_thu=doanh_thu, thue=thue, ds_khuyen_mai_tu_dong=ds_khuyen_mai_tu_dong, ds_khuyen_mai_tuy_chon=ds_khuyen_mai_tuy_chon)


            doanh_thu_out = doanh_thu_out_schema.dump(doanh_thu)
            doanh_thu_out['clientSecret'] = info['clientSecret']

            return doanh_thu_out
        
    def xu_ly_hoan_thanh_online(self, payload, sig_header, endpoint_secret):
        with transaction_manager.transaction("Lỗi khi đang hoàn thành quá trình thanh toán Online") as session:
            metadata = self.doanh_thu_thanh_toan_service.xu_ly_hoan_thanh_thanh_toan_online(payload=payload, sig_header=sig_header, endpoint_secret=endpoint_secret)

            doanh_thu_id = metadata.get('doanh_thu_id')
            thanh_toan_id = metadata.get('thanh_toan_id')

            

            print("Doanh_Thu_id", doanh_thu_id)
            print("Thanh_Toan_id", thanh_toan_id)

            doanh_thu = self.doanh_thu_dao.find_by_id(session=session, doanh_thu_id=int(doanh_thu_id))

            if not doanh_thu:
                raise Exception("Không tồn tại doanh thu để thanh toán.")
            
            flag = doanh_thu.hoan_tat_thanh_toan(thanh_toan_id=int(thanh_toan_id))
            
            self.doanh_thu_dao.save(session=session, doanh_thu=doanh_thu)

            print(flag)

            

            


            
            
                




        

class DoanhThuThanhToanService(IDoanhThuThanhToanService):
    @inject
    def __init__(self, doanh_thu_dao: IDoanhThuDAO, thanh_toan_online: ThanhToanOnline):
        self.doanh_thu_dao = doanh_thu_dao
        self.thanh_toan_online = thanh_toan_online

    def tao_preview(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None = None) -> Dict[str, Any]:
        tien_giam_gia = 0
        khuyen_mai_id_1 = None
        khuyen_mai_id_2 = None
        so_tien_giam_1 = 0
        so_tien_giam_2 = 0
        tong_tien = doanh_thu.phien_ban.tinh_tong_tien()
        for km in ds_khuyen_mai:
            if km.co_the_su_dung(tong_tien):
                so_tien_giam_1 = km.tinh_so_tien_duoc_giam(tong_tien)
                tien_giam_gia += so_tien_giam_1
                khuyen_mai_id_1 = km.id
                break
        if ds_khuyen_mai_tuy_chon:
            for km in ds_khuyen_mai_tuy_chon:
                if km.co_the_su_dung(tong_tien):
                    so_tien_giam_2 = km.tinh_so_tien_duoc_giam(tong_tien)
                    tien_giam_gia += so_tien_giam_2
                    khuyen_mai_id_2 = km.id
                    break
                else: 
                    raise Exception("Không đủ điều kiện để sử dụng")

        
        tien_sau_giam = tong_tien - tien_giam_gia
        ten_thue = thue.ten
        ti_le_thue = thue.ti_le
        tien_thue = thue.tinh_gia_tri(tien_sau_giam)

        tien_cuoi_cung = tien_sau_giam - tien_thue
        data_preview = {'id': doanh_thu.id,'tong_tien': tong_tien, 'tien_giam_gia': tien_giam_gia, 'ten_thue': ten_thue, 'ti_le_thue': ti_le_thue, 'tien_thue': tien_thue, 'tien_cuoi_cung': tien_cuoi_cung, 'trang_thai': 'CHUAHOANTHANH', 'phien_ban_id': doanh_thu.phien_ban_id}
        data_preview['ds_khuyen_mai'] = []
        if khuyen_mai_id_1:
            data_preview['ds_khuyen_mai'].append({'phien_ban_id': doanh_thu.phien_ban_id, 'khuyen_mai_id': khuyen_mai_id_1, 'so_tien_giam': so_tien_giam_1})
        
        if khuyen_mai_id_2:
            data_preview['ds_khuyen_mai'].append({'phien_ban_id': doanh_thu.phien_ban_id, 'khuyen_mai_id': khuyen_mai_id_2, 'so_tien_giam': so_tien_giam_2})
        return data_preview
    
    def xu_ly_thanh_toan_doanh_thu(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai_tu_dong: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None):
        with transaction_manager.transaction("Lỗi khi xử lý doanh thu") as session:
            doanh_thu.cap_nhat(thue=thue, ds_khuyen_mai_tu_dong=ds_khuyen_mai_tu_dong, ds_khuyen_mai_tuy_chon=ds_khuyen_mai_tuy_chon)
            doanh_thu.thanh_toan_tien_mat()

            self.doanh_thu_dao.save(session=session, doanh_thu=doanh_thu)

    def xu_ly_thanh_toan_doanh_thu_online(self, doanh_thu: DoanhThu, thue: CauHinhThue, ds_khuyen_mai_tu_dong: List[KhuyenMai], ds_khuyen_mai_tuy_chon: List[KhuyenMai] | None):
        with transaction_manager.transaction("Lỗi khi xử lý doanh thu") as session:
            doanh_thu.cap_nhat(thue=thue, ds_khuyen_mai_tu_dong=ds_khuyen_mai_tu_dong, ds_khuyen_mai_tuy_chon=ds_khuyen_mai_tuy_chon)
            doanh_thu.thanh_toan_online()

            self.doanh_thu_dao.save(session=session, doanh_thu=doanh_thu)

            metadata = {
                'doanh_thu_id': doanh_thu.id,
                'thanh_toan_id': doanh_thu.lay_phien_thanh_toan().id
            }

            info = self.thanh_toan_online.xu_ly_thanh_toan_online(so_tien=doanh_thu.tien_cuoi_cung, metadata=metadata)
            return info
        

    def xu_ly_hoan_thanh_thanh_toan_online(self, payload, sig_header, endpoint_secret) -> Dict[str, Any]:
        return self.thanh_toan_online.xac_thuc_webhook(payload=payload, sig_header=sig_header, endpoint_secret=endpoint_secret)
        
        
    

    
            
            
            

                
            

        
class KhuyenMaiService(IKhuyenMaiService):
    @inject
    def __init__(self, khuyen_mai_dao: IKhuyenMaiDAO, nguoi_dung_dao: INguoiDungDAO):
        self.khuyen_mai_dao = khuyen_mai_dao
        self.nguoi_dung_dao = nguoi_dung_dao

    def lay_danh_sach_khuyen_mai_tuy_chon(self, thu_ngan_id: int) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy danh sách khuyến mãi") as session:
            thu_ngan = self.nguoi_dung_dao.find_by_id(session=session, id=thu_ngan_id)
            if not thu_ngan:
                raise Exception('Không tồn tại thu ngân.')
            ds_khuyen_mai = self.khuyen_mai_dao.find_by_tuy_chon(session=session)
            ds_khuyen_mai_out = khuyen_mai_out_schema.dump(ds_khuyen_mai, many=True)

            return ds_khuyen_mai_out


class BaoCaoService(IBaoCaoService):
    """Service xử lý báo cáo cho Quản lý"""

    @inject
    def __init__(self, bao_cao_dao: IBaoCaoDAO):
        self.bao_cao_dao = bao_cao_dao

    def lay_tong_quan(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy tổng quan báo cáo") as session:
            
            thong_ke = self.bao_cao_dao.thong_ke_tong_quan(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)
            
           
            top_mon = self.bao_cao_dao.top_mon_ban_chay(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay, limit=5)
            
            
            chart_data = self.bao_cao_dao.thong_ke_theo_ngay(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)
            
            
            thong_ke_gio = self.bao_cao_dao.thong_ke_theo_gio(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)

            return {
                'thong_ke': thong_ke,
                'top_mon': top_mon,
                'chart_data': chart_data,
                'thong_ke_gio': thong_ke_gio,
                'tu_ngay': str(tu_ngay),
                'den_ngay': str(den_ngay)
            }

    def lay_bao_cao_doanh_thu(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy báo cáo doanh thu") as session:
            thong_ke = self.bao_cao_dao.thong_ke_tong_quan(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)
            chi_tiet_ngay = self.bao_cao_dao.thong_ke_theo_ngay(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)
            thong_ke_gio = self.bao_cao_dao.thong_ke_theo_gio(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)

            return {
                'thong_ke': thong_ke,
                'chi_tiet_ngay': chi_tiet_ngay,
                'thong_ke_gio': thong_ke_gio,
                'tu_ngay': str(tu_ngay),
                'den_ngay': str(den_ngay)
            }

    def lay_hieu_suat_nhan_vien(self, quan_ly_id: int, tu_ngay, den_ngay) -> List[Dict[str, Any]]:
        with transaction_manager.transaction("Lỗi khi lấy hiệu suất nhân viên") as session:
            ds_nhan_vien = self.bao_cao_dao.hieu_suat_nhan_vien(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)
            
            return {
                'ds_nhan_vien': ds_nhan_vien,
                'tu_ngay': str(tu_ngay),
                'den_ngay': str(den_ngay)
            }

    def lay_thong_ke_mon_an(self, quan_ly_id: int, tu_ngay, den_ngay) -> Dict[str, Any]:
        with transaction_manager.transaction("Lỗi khi lấy thống kê món ăn") as session:
            top_mon = self.bao_cao_dao.top_mon_ban_chay(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay, limit=20)
            thong_ke_nhom = self.bao_cao_dao.thong_ke_theo_nhom_mon(session=session, tu_ngay=tu_ngay, den_ngay=den_ngay)

            return {
                'top_mon': top_mon,
                'thong_ke_nhom': thong_ke_nhom,
                'tu_ngay': str(tu_ngay),
                'den_ngay': str(den_ngay)
            }
