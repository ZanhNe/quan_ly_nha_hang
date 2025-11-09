from flask import Flask
from app.config import Config
from app.presentation.web.routes.test import test
from app.extentions.extentions import db, ma, migrate
from flask_sqlalchemy import SQLAlchemy
from app.data.models import VaiTro, TenVaiTro, TaiKhoan, LeTan, PhucVu, KhuVuc, Ban, KhungGio, PhienBan, PhanCong, NguoiDung
import datetime

def create_app() -> Flask:
    app = Flask(__name__, \
            template_folder='presentation/web/templates', \
            static_folder='presentation/web/static', \
            static_url_path= '/assets')
    app.config.from_object(obj=Config)
    ma.init_app(app=app)
    db.init_app(app=app)
    migrate.init_app(app=app)

    register_commands(app=app, db=db)

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

                db.session.add_all([vaitro_1, vaitro_2])
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
                ban_1 = Ban(ten="ban_1", so_ghe=4, khu_vuc_id=khuvuc_A.id)

                #Tạo người dùng cụ thể với vai trò
                letan = LeTan(ho_ten="Tran Do My", tai_khoan_id=tk_letan.id)
                phucvu = PhucVu(is_nhom_truong=True, ho_ten="Diep Bao Doanh", tai_khoan_id=tk_phucvu.id, khu_vuc_id=khuvuc_A.id)

                db.session.add_all([letan, phucvu, ban_1])
                db.session.flush()

                khuvuc_A.nhom_truong_id = phucvu.id

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

                db.session.commit()

                print("Đã thêm dữ liệu mới thành công!")

        except Exception as e:
                print(e)
                db.session.rollback()
                print("Có lỗi trong quá trình thêm dữ liệu")







