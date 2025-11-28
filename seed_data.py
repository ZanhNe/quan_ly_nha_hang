import datetime
from app import create_app # Thay đổi tùy theo cách bạn khởi tạo app
from app.extentions.extentions import db
from app.data.models import (
    VaiTro, TenVaiTro, TaiKhoan, TrangThaiTaiKhoan, 
    KhuVuc, Ban, TrangThaiBan, 
    NguoiDung, LeTan, PhucVu, 
    PhienBan, PhanCong, TrangThai, 
    KhungGio, KhungGioAn, KhungGioDatBan, BienChung
)
from app.utils.helper import Helper

# Khởi tạo Helper để hash password
helper = Helper()

app = create_app()

def seed_data():
    with app.app_context():
        print("🗑️  Đang xóa dữ liệu cũ (Clean DB)...")
        db.drop_all()
        db.create_all()
        print("✅  Đã tạo lại tables mới.")

        # ==========================================
        # 1. KHỞI TẠO VAI TRÒ (ROLES)
        # ==========================================
        print("👤  Đang khởi tạo Vai Trò...")
        roles = {}
        for role_enum in TenVaiTro:
            vt = VaiTro(vai_tro=role_enum)
            db.session.add(vt)
            roles[role_enum] = vt
        
        db.session.flush() # Để lấy ID

        # ==========================================
        # 2. KHỞI TẠO KHU VỰC & BÀN
        # ==========================================
        print("w  Đang khởi tạo Khu Vực & Bàn...")
        
        # Khu vực A: Trong nhà (Sảnh chính)
        kv_a = KhuVuc(ten="Sảnh Chính (Máy Lạnh)")
        db.session.add(kv_a)
        db.session.flush()
        
        list_ban_a = []
        for i in range(1, 6): # Bàn A1 -> A5
            ban = Ban(ten=f"A{i}", so_ghe=4 if i < 5 else 8, khu_vuc_id=kv_a.id)
            db.session.add(ban)
            list_ban_a.append(ban)

        # Khu vực B: Ngoài trời
        kv_b = KhuVuc(ten="Sân Vườn (Ngoài Trời)")
        db.session.add(kv_b)
        db.session.flush()

        list_ban_b = []
        for i in range(1, 4): # Bàn B1 -> B3
            ban = Ban(ten=f"B{i}", so_ghe=4, khu_vuc_id=kv_b.id)
            db.session.add(ban)
            list_ban_b.append(ban)

        db.session.flush()

        # ==========================================
        # 3. KHỞI TẠO TÀI KHOẢN & NHÂN VIÊN
        # ==========================================
        print("busts_in_silhouette:  Đang khởi tạo Tài khoản & Nhân viên...")

        # Hàm helper tạo tài khoản nhanh
        def create_account(username, password, role_enum, name, user_type=None, kv_id=None):
            # Hash password
            hashed_pw = helper.hass_pass(password)
            
            tk = TaiKhoan(
                ten_tai_khoan=username,
                mat_khau=hashed_pw,
                vai_tro_id=roles[role_enum].id,
                trang_thai=TrangThaiTaiKhoan.MO,
                is_xac_thuc=True # Bypass xác thực email
            )
            db.session.add(tk)
            db.session.flush()

            user = None
            if user_type == 'letan':
                user = LeTan(ho_ten=name, tai_khoan_id=tk.id)
            elif user_type == 'phucvu':
                user = PhucVu(ho_ten=name, tai_khoan_id=tk.id, khu_vuc_id=kv_id)
            else:
                # Admin hoặc Quản lý (dùng class NguoiDung cơ bản hoặc tạo riêng nếu có model)
                user = NguoiDung(ho_ten=name, tai_khoan_id=tk.id)
            
            db.session.add(user)
            db.session.flush()
            return user

        # --- Admin & Manager ---
        admin = create_account("admin", "admin123", TenVaiTro.ADMIN, "Super Admin")
        quanly = create_account("quanly", "123", TenVaiTro.QUANLY, "Nguyễn Quản Lý")

        # --- Lễ Tân ---
        letan_1 = create_account("letan1", "123", TenVaiTro.LETAN, "Trần Lễ Tân", 'letan')
        letan_2 = create_account("letan2", "123", TenVaiTro.LETAN, "Lê Tiếp Đón", 'letan')

        # --- Phục Vụ ---
        # Phục vụ khu A
        pv_a1 = create_account("pv_a1", "123", TenVaiTro.PHUCVU, "Phục Vụ A1", 'phucvu', kv_a.id)
        pv_a2 = create_account("pv_a2", "123", TenVaiTro.PHUCVU, "Phục Vụ A2", 'phucvu', kv_a.id)
        pv_a3 = create_account("pv_a3", "123", TenVaiTro.PHUCVU, "Phục Vụ A3", 'phucvu', kv_a.id)
        pv_a4 = create_account("pv_a4", "123", TenVaiTro.PHUCVU, "Phục Vụ A4", 'phucvu', kv_a.id)
        pv_a5 = create_account("pv_a5", "123", TenVaiTro.PHUCVU, "Phục Vụ A5", 'phucvu', kv_a.id)
        
        # Phục vụ khu B
        pv_b1 = create_account("pv_b1", "123", TenVaiTro.PHUCVU, "Phục Vụ B1", 'phucvu', kv_b.id)
        pv_b2 = create_account("pv_b2", "123", TenVaiTro.PHUCVU, "Phục Vụ B2", 'phucvu', kv_b.id)

        # ==========================================
        # 4. GIẢ LẬP KỊCH BẢN (MOCK SCENARIO)
        # ==========================================
        print("rocket:  Đang chạy các kịch bản giả lập...")

        # --- KỊCH BẢN 1: Bàn A1 đang có khách ăn (Đã vào 30p trước) ---
        # 1. Lấy bàn
        ban_active = list_ban_a[0] # A1
        
        # 2. Tạo Phiên (Session) do Lễ tân 1 tạo
        tg_bat_dau = datetime.datetime.now() - datetime.timedelta(minutes=30)
        phien_an = PhienBan(le_tan_id=letan_1.nguoi_dung_id, trang_thai=TrangThai.MO)
        
        # 3. Tạo Khung Giờ Ăn (Quan trọng: Dùng KhungGioAn)
        # Lưu ý: Mặc dù model PhienBan có hàm tao_khung_gio, nhưng để rõ ràng type, ta tạo thủ công
        kg_an = KhungGioAn(
            tg_bat_dau=tg_bat_dau,
            tg_ket_thuc_du_kien=tg_bat_dau + datetime.timedelta(minutes=60), # Dự kiến ăn 60p
            trang_thai=TrangThai.MO
        )
        phien_an.khung_gio = kg_an # Link One-to-One
        
        db.session.add_all([phien_an, kg_an])
        db.session.flush()

        # 4. Link Khung Giờ vào Bàn (Quan trọng: cập nhật bảng trung gian ban_khunggio)
        ban_active.them_khung_gio(kg_an)
        ban_active.trang_thai = TrangThaiBan.COKHACH
        
        # 5. Phân công cho Phục vụ A1
        pc_active = PhanCong(
            phuc_vu_id=pv_a1.nguoi_dung_id,
            ban_id=ban_active.id,
            phien_ban_id=phien_an.id,
            trang_thai=TrangThai.MO,
            dam_nhan_ghi_mon=True
        )
        db.session.add(pc_active)


        # --- KỊCH BẢN 2: Bàn A2 đang được GIỮ CHỖ (Khách đến trong 1 tiếng nữa) ---
        ban_reserve = list_ban_a[1] # A2
        tg_dat = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        # Tạo Khung Giờ Đặt Bàn (Khác KhungGioAn, không cần PhienBan ngay lập tức nếu logic chưa cần check-in)
        # Tuy nhiên model KhungGio có khoá ngoại phien_ban_id, nên ta cần tạo 1 phiên giữ chỗ
        phien_dat = PhienBan(le_tan_id=letan_2.nguoi_dung_id, trang_thai=TrangThai.MO)
        
        kg_dat = KhungGioDatBan(
            tg_bat_dau=tg_dat,
            tg_ket_thuc_du_kien=tg_dat + datetime.timedelta(minutes=BienChung.THOIGIANCODINH),
            trang_thai=TrangThai.MO
        )
        phien_dat.khung_gio = kg_dat

        db.session.add_all([phien_dat, kg_dat])
        db.session.flush()

        # Link vào bàn
        ban_reserve.them_khung_gio(kg_dat)
        ban_reserve.trang_thai = TrangThaiBan.GIUCHO


        # --- KỊCH BẢN 3: Bàn B1 vừa mới vào (Check-in ngay bây giờ) ---
        ban_new = list_ban_b[0] # B1
        tg_now = datetime.datetime.now()
        
        phien_new = PhienBan(le_tan_id=letan_1.nguoi_dung_id)
        # Sử dụng phương thức của model (sẽ tạo base KhungGio, bạn có thể override trong model nếu muốn ra KhungGioAn)
        # Ở đây tôi tạo thủ công KhungGioAn cho chuẩn polymorphic
        kg_new = KhungGioAn(
            tg_bat_dau=tg_now,
            tg_ket_thuc_du_kien=tg_now + datetime.timedelta(minutes=90),
            trang_thai=TrangThai.MO
        )
        phien_new.khung_gio = kg_new
        
        db.session.add_all([phien_new, kg_new])
        db.session.flush()
        
        ban_new.them_khung_gio(kg_new)
        ban_new.trang_thai = TrangThaiBan.COKHACH
        
        # Phân công cho PV B1
        pc_new = PhanCong(
            phuc_vu_id=pv_b1.nguoi_dung_id,
            ban_id=ban_new.id,
            phien_ban_id=phien_new.id,
            dam_nhan_ghi_mon=True
        )
        db.session.add(pc_new)


        # ==========================================
        # 5. COMMIT
        # ==========================================
        db.session.commit()
        print("✨  Đã khởi tạo Mock Data thành công! ✨")
        print("---------------------------------------")
        print("Account Admin:   admin / admin123")
        print("Account Lễ tân:  letan1 / 123")
        print("Account Phục vụ: pv_a1 / 123")
        print("---------------------------------------")

if __name__ == '__main__':
    seed_data()