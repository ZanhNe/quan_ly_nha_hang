import datetime
from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from app.presentation.web.routes.test import test
from app.presentation.web.routes.index import index_bp
from app.api.api import api_bp
from app.extentions.extentions import db, ma, migrate, mail, bcrypt, socketio
from app.data.models import (VaiTro, TenVaiTro, TaiKhoan, LeTan, PhucVu, KhuVuc, Ban, KhungGio, PhienBan, PhanCong, TrangThaiBan)
from app.utils.helper import is_near

def create_app() -> Flask:
    app = Flask(__name__, \
            template_folder='presentation/web/templates', \
            static_folder='presentation/web/static', \
            static_url_path= '/assets')
    app.config.from_object(obj=Config)
    app.jinja_env.filters['is_near'] = is_near

    ma.init_app(app=app)
    db.init_app(app=app)
    migrate.init_app(app=app)

    mail.init_app(app=app)
    bcrypt.init_app(app=app)
    socketio.init_app(app=app)

    register_commands(app=app, db=db)
    app.register_blueprint(blueprint=test)
    app.register_blueprint(blueprint=index_bp)
    app.register_blueprint(blueprint=api_bp)

    return app




#Dùng để đăng ký command cho việc chạy CLI test thêm data vào Database
def register_commands(app: Flask, db: SQLAlchemy): #Chạy lệnh flask init-db để run command, đầu tiên là set FLASK_APP=entry.py trong terminal, sau đó mới flask init-db
    """Hàm này sẽ được gọi từ app.py để đăng ký lệnh CLI"""
    @app.cli.command('init-db')
    def init_db_command():
        db.drop_all()
        print("Đã xóa các bảng cũ")

        db.create_all()
        print("Đã tạo các bảng mới")
        try:
                #Tạo vai trò trước
                vaitro_1 = VaiTro(vai_tro=TenVaiTro.LETAN)
                vaitro_2 = VaiTro(vai_tro=TenVaiTro.PHUCVU)
                vaitro_3 = VaiTro(vai_tro=TenVaiTro.VODANH)

                db.session.add_all([vaitro_1, vaitro_2, vaitro_3])
                db.session.flush()

                #Tạo tài khoản và liên kết với người dùng
                tk_letan = TaiKhoan(ten_tai_khoan="tk1", mat_khau="123", vai_tro_id=vaitro_1.id)
                tk_phucvu = TaiKhoan(ten_tai_khoan="tk2", mat_khau="123", vai_tro_id=vaitro_2.id)

                db.session.add_all([tk_letan, tk_phucvu])
                db.session.flush()


                #Tạo khu vực
                khuvuc_A = KhuVuc(ten="A")

                db.session.add(khuvuc_A)
                db.session.flush()

                #Tạo Bàn
                ban_1 = Ban(ten="A1", so_ghe=4, khu_vuc_id=khuvuc_A.id)

                #Tạo người dùng cụ thể với vai trò
                letan = LeTan(ho_ten="Tran Do My", tai_khoan_id=tk_letan.id)
                phucvu = PhucVu(ho_ten="Diep Bao Doanh", tai_khoan_id=tk_phucvu.id, khu_vuc_id=khuvuc_A.id)

                db.session.add_all([letan, phucvu, ban_1])
                db.session.flush()

                

                #Tạo phiên bàn, phân công
                tg_hientai = datetime.datetime.now()

                phien_1 = PhienBan(le_tan_id=letan.id)
                phien_1.tao_khung_gio(tg_bat_dau=tg_hientai)

                db.session.add_all([phien_1, khuvuc_A])
                db.session.flush()

                #Tạo phân công
                phan_cong = PhanCong(phuc_vu_id=phucvu.id, ban_id=ban_1.id, phien_ban_id=phien_1.id)

                db.session.add(phan_cong)
                db.session.flush()

                # ------------ BẮT ĐẦU SCRIPT MỞ RỘNG ------------
                print("Đang thêm dữ liệu mock mở rộng...")

                # --- 1. Thêm các Vai Trò và Tài Khoản còn thiếu ---
                # Script gốc đã tạo vaitro_1 (LETAN) và vaitro_2 (PHUCVU)
                vaitro_admin = VaiTro(vai_tro=TenVaiTro.ADMIN)
                vaitro_quanly = VaiTro(vai_tro=TenVaiTro.QUANLY)
                vaitro_thungan = VaiTro(vai_tro=TenVaiTro.THUNGAN)
                
                db.session.add_all([vaitro_admin, vaitro_quanly, vaitro_thungan])
                db.session.flush() # Lấy ID cho các tài khoản
                
                # Tạo tài khoản cho các vai trò quản lý
                tk_admin = TaiKhoan(ten_tai_khoan="admin", mat_khau="admin123", vai_tro_id=vaitro_admin.id)
                tk_quanly = TaiKhoan(ten_tai_khoan="quanly", mat_khau="quanly123", vai_tro_id=vaitro_quanly.id)
                tk_thungan = TaiKhoan(ten_tai_khoan="thungan", mat_khau="thungan123", vai_tro_id=vaitro_thungan.id)
                
                # Tạo thêm tài khoản cho nhân viên mới
                tk_letan_2 = TaiKhoan(ten_tai_khoan="tk_letan2", mat_khau="123", vai_tro_id=vaitro_1.id) # Dùng vaitro_1 (Lễ Tân) từ script gốc
                tk_phucvu_2 = TaiKhoan(ten_tai_khoan="tk_pv2", mat_khau="123", vai_tro_id=vaitro_2.id) # Dùng vaitro_2 (Phục Vụ) từ script gốc
                tk_phucvu_3 = TaiKhoan(ten_tai_khoan="tk_pv3", mat_khau="123", vai_tro_id=vaitro_2.id)
                tk_phucvu_4 = TaiKhoan(ten_tai_khoan="tk_pv4", mat_khau="123", vai_tro_id=vaitro_2.id)
                
                db.session.add_all([
                tk_admin, tk_quanly, tk_thungan, tk_letan_2, 
                tk_phucvu_2, tk_phucvu_3, tk_phucvu_4
                ])
                db.session.flush()
                
                # --- 2. Thêm Khu Vực mới ---
                # khuvuc_A đã được tạo ở script gốc
                khuvuc_B = KhuVuc(ten="B (Ngoài trời)")
                khuvuc_C = KhuVuc(ten="C (Tầng 2)")
                
                db.session.add_all([khuvuc_B, khuvuc_C])
                db.session.flush() # Lấy ID cho nhân viên phục vụ
                
                # --- 3. Thêm Nhân Viên mới (LeTan, PhucVu) ---
                # letan (Tran Do My) và phucvu (Diep Bao Doanh) đã có từ script gốc
                
                # Thêm 1 Lễ tân
                letan_2 = LeTan(ho_ten="Mai Anh Tuấn", tai_khoan_id=tk_letan_2.id)
                
                # Thêm 1 Phục vụ cho khu vực A (nhân viên thường)
                phucvu_2 = PhucVu(ho_ten="Nguyễn Văn B", tai_khoan_id=tk_phucvu_2.id, khu_vuc_id=khuvuc_A.id)
                
                # Thêm 1 Phục vụ cho khu vực B (nhóm trưởng)
                phucvu_3 = PhucVu(ho_ten="Lê Thị C", tai_khoan_id=tk_phucvu_3.id, khu_vuc_id=khuvuc_B.id)
                
                # Thêm 1 Phục vụ cho khu vực C (nhóm trưởng)
                phucvu_4 = PhucVu(ho_ten="Phạm Văn D", tai_khoan_id=tk_phucvu_4.id, khu_vuc_id=khuvuc_C.id)
                
                db.session.add_all([letan_2, phucvu_2, phucvu_3, phucvu_4])
                db.session.flush() # Lấy ID để gán nhóm trưởng
                
                # --- 4. Cập nhật Nhóm Trưởng cho Khu Vực mới ---
                
                
                db.session.add_all([khuvuc_B, khuvuc_C]) # Cập nhật lại khu vực
                db.session.flush()

                # --- 5. Thêm Bàn mới cho các Khu Vực ---
                # ban_1 (4 ghế) đã có ở khu A từ script gốc
                ban_A2 = Ban(ten="A2", so_ghe=4, khu_vuc_id=khuvuc_A.id, trang_thai=TrangThaiBan.TRONG)
                ban_A3 = Ban(ten="A3", so_ghe=2, khu_vuc_id=khuvuc_A.id, trang_thai=TrangThaiBan.TRONG)
                ban_A4 = Ban(ten="A4", so_ghe=8, khu_vuc_id=khuvuc_A.id, trang_thai=TrangThaiBan.TRONG)
                
                ban_B1 = Ban(ten="B1", so_ghe=4, khu_vuc_id=khuvuc_B.id, trang_thai=TrangThaiBan.TRONG)
                ban_B2 = Ban(ten="B2", so_ghe=6, khu_vuc_id=khuvuc_B.id, trang_thai=TrangThaiBan.TRONG)
                
                ban_C1 = Ban(ten="C1", so_ghe=2, khu_vuc_id=khuvuc_C.id, trang_thai=TrangThaiBan.TRONG)
                ban_C2 = Ban(ten="C2", so_ghe=4, khu_vuc_id=khuvuc_C.id, trang_thai=TrangThaiBan.TRONG)
                ban_C3 = Ban(ten="C3", so_ghe=4, khu_vuc_id=khuvuc_C.id, trang_thai=TrangThaiBan.TRONG)
                
                db.session.add_all([
                ban_A2, ban_A3, ban_A4, ban_B1, ban_B2, ban_C1, ban_C2, ban_C3
                ])
                db.session.flush()
                
                # # --- 6. Tạo kịch bản Bàn "Có Khách" và "Giữ Chỗ" ---
                
                # # Kịch bản 1: Bàn A3 (2 ghế) đang "CÓ KHÁCH"
                # # - do letan_2 (Mai Anh Tuấn) check-in
                # # - do phucvu_2 (Nguyễn Văn B) phục vụ.
                # # - Giả sử khách vào 15 phút trước
                tg_hientai_2 = datetime.datetime.now() - datetime.timedelta(minutes=15) 
                
                phien_A3 = PhienBan(le_tan_id=letan_2.id)
                phien_A3.tao_khung_gio(tg_bat_dau=tg_hientai_2)
                ban_A3.trang_thai = TrangThaiBan.COKHACH # Cập nhật trạng thái bàn
                
                db.session.add_all([phien_A3, ban_A3]) 
                db.session.flush()
                
                phan_cong_A3 = PhanCong(phuc_vu_id=phucvu_2.id, ban_id=ban_A3.id, phien_ban_id=phien_A3.id)
                db.session.add(phan_cong_A3)
                db.session.flush()
                
                # # Kịch bản 2: Bàn B2 (6 ghế) được "GIỮ CHỖ"
                # # - do letan (Trần Do Mỹ) đặt
                # # - cho 2 tiếng nữa. 
                # # - phucvu_3 (Lê Thị C) sẽ phụ trách.
                # tg_dat_cho = datetime.datetime.now() + datetime.timedelta(hours=2)
                
                # phien_B2 = PhienBan(le_tan_id=letan.id) # letan từ script gốc
                # phien_B2.tao_khung_gio(tg_bat_dau=tg_dat_cho)
                # ban_B2.trang_thai = TrangThaiBan.GIUCHO # Cập nhật trạng thái bàn
                
                # db.session.add_all([phien_B2, ban_B2])
                # db.session.flush()
                
                # phan_cong_B2 = PhanCong(phuc_vu_id=phucvu_3.id, ban_id=ban_B2.id, phien_ban_id=phien_B2.id)
                # db.session.add(phan_cong_B2)
                
                # ------------ KẾT THÚC SCRIPT MỞ RỘNG ------------
                

                db.session.commit()

                print("Đã thêm dữ liệu mới thành công!")

        except Exception as e:
                print(e)
                db.session.rollback()
                print("Có lỗi trong quá trình thêm dữ liệu")









