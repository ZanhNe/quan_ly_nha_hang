import datetime
import random
from app import create_app
from app.extentions.extentions import db
from app.data.models import (
    VaiTro, TenVaiTro, TaiKhoan, TrangThaiTaiKhoan, 
    KhuVuc, Ban, TrangThaiBan, 
    NguoiDung, LeTan, PhucVu, DauBep, ThuNgan, QuanLy,
    PhienBan, PhanCong, TrangThai, 
    KhungGio, KhungGioAn, KhungGioDatBan, BienChung, ThucDon, MoTaMon, NhomTuyChon, TuyChonMon, LoaiNhomTuyChon, NhomMon,
    KhuyenMaiTheoPhanTram, CauHinhThue, KhuyenMaiCung,
    PhieuMon, TrangThaiPhieu, MonGhi, TrangThaiMonGhi,
    DoanhThu, TrangThaiDoanhThu, ThanhToan, TrangThaiThanhToan, PhuongThucThanhToan,
    YCMonGhi, TrangThaiYeuCau
)
from app.utils.helper import Helper

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
        
        db.session.flush()

        # ==========================================
        # 2. KHỞI TẠO KHU VỰC & BÀN
        # ==========================================
        print("🏠  Đang khởi tạo Khu Vực & Bàn...")
        
        # Khu vực A: Trong nhà
        kv_a = KhuVuc(ten="Sảnh Chính (Máy Lạnh)")
        db.session.add(kv_a)
        db.session.flush()
        
        list_ban_a = []
        for i in range(1, 8):  # Bàn A1 -> A7
            ban = Ban(ten=f"A{i}", so_ghe=4 if i < 6 else 8, khu_vuc_id=kv_a.id)
            db.session.add(ban)
            list_ban_a.append(ban)

        # Khu vực B: Ngoài trời
        kv_b = KhuVuc(ten="Sân Vườn (Ngoài Trời)")
        db.session.add(kv_b)
        db.session.flush()

        list_ban_b = []
        for i in range(1, 5):  # Bàn B1 -> B4
            ban = Ban(ten=f"B{i}", so_ghe=4, khu_vuc_id=kv_b.id)
            db.session.add(ban)
            list_ban_b.append(ban)

        # Khu vực VIP
        kv_vip = KhuVuc(ten="Phòng VIP")
        db.session.add(kv_vip)
        db.session.flush()

        list_ban_vip = []
        for i in range(1, 3):  # VIP1, VIP2
            ban = Ban(ten=f"VIP{i}", so_ghe=10, khu_vuc_id=kv_vip.id)
            db.session.add(ban)
            list_ban_vip.append(ban)

        db.session.flush()

        # ==========================================
        # 3. KHỞI TẠO TÀI KHOẢN & NHÂN VIÊN
        # ==========================================
        print("👥  Đang khởi tạo Tài khoản & Nhân viên...")

        def create_account(username, password, role_enum, name, user_type=None, kv_id=None):
            hashed_pw = helper.hass_pass(password)
            
            tk = TaiKhoan(
                ten_tai_khoan=username,
                mat_khau=hashed_pw,
                vai_tro_id=roles[role_enum].id,
                trang_thai=TrangThaiTaiKhoan.MO,
                is_xac_thuc=True
            )
            db.session.add(tk)
            db.session.flush()

            user = None
            if user_type == 'letan':
                user = LeTan(ho_ten=name, tai_khoan_id=tk.id)
            elif user_type == 'phucvu':
                user = PhucVu(ho_ten=name, tai_khoan_id=tk.id, khu_vuc_id=kv_id)
            elif user_type == 'daubep':
                user = DauBep(ho_ten=name, tai_khoan_id=tk.id) 
            elif user_type == 'thungan':
                user = ThuNgan(ho_ten=name, tai_khoan_id=tk.id)
            elif user_type == 'quanly':
                user = QuanLy(ho_ten=name, tai_khoan_id=tk.id)
            else:
                user = NguoiDung(ho_ten=name, tai_khoan_id=tk.id)
            
            db.session.add(user)
            db.session.flush()
            return user

        # --- Admin & Quản lý ---
        admin = create_account("admin", "admin123", TenVaiTro.ADMIN, "Super Admin")
        quanly = create_account("quanly", "123", TenVaiTro.QUANLY, "Nguyễn Văn Quản Lý", 'quanly')
        quanly2 = create_account("quanly2", "123", TenVaiTro.QUANLY, "Trần Thị Giám Đốc", 'quanly')

        # --- Thu Ngân ---
        thungan = create_account("thungan", "123", TenVaiTro.THUNGAN, "Lê Thị Thu Ngân", 'thungan')
        thungan2 = create_account("thungan2", "123", TenVaiTro.THUNGAN, "Phạm Văn Kế Toán", 'thungan')

        # --- Đầu bếp ---
        daubep_1 = create_account("daubep1", "123", TenVaiTro.DAUBEP, "Trần Minh Bếp Trưởng", 'daubep')
        daubep_2 = create_account("daubep2", "123", TenVaiTro.DAUBEP, "Lê Văn Bếp Phó", 'daubep')
        daubep_3 = create_account("daubep3", "123", TenVaiTro.DAUBEP, "Nguyễn Thị Bếp Chính", 'daubep')

        # --- Lễ tân ---
        letan_1 = create_account("letan1", "123", TenVaiTro.LETAN, "Nguyễn Thị Hương", 'letan')
        letan_2 = create_account("letan2", "123", TenVaiTro.LETAN, "Trần Văn Minh", 'letan')

        # --- Phục vụ khu A ---
        pv_a1 = create_account("pv_a1", "123", TenVaiTro.PHUCVU, "Phạm Văn Hùng", 'phucvu', kv_a.id)
        pv_a2 = create_account("pv_a2", "123", TenVaiTro.PHUCVU, "Nguyễn Thị Lan", 'phucvu', kv_a.id)
        pv_a3 = create_account("pv_a3", "123", TenVaiTro.PHUCVU, "Lê Văn Đức", 'phucvu', kv_a.id)
        pv_a4 = create_account("pv_a4", "123", TenVaiTro.PHUCVU, "Trần Thị Mai", 'phucvu', kv_a.id)
        pv_a5 = create_account("pv_a5", "123", TenVaiTro.PHUCVU, "Hoàng Văn Nam", 'phucvu', kv_a.id)
        
        # --- Phục vụ khu B ---
        pv_b1 = create_account("pv_b1", "123", TenVaiTro.PHUCVU, "Đỗ Thị Hoa", 'phucvu', kv_b.id)
        pv_b2 = create_account("pv_b2", "123", TenVaiTro.PHUCVU, "Vũ Văn Tuấn", 'phucvu', kv_b.id)

        # --- Phục vụ khu VIP ---
        pv_vip = create_account("pv_vip", "123", TenVaiTro.PHUCVU, "Nguyễn Thị Ngọc", 'phucvu', kv_vip.id)

        ds_phuc_vu = [pv_a1, pv_a2, pv_a3, pv_a4, pv_a5, pv_b1, pv_b2, pv_vip]

        # ==========================================
        # 4. TẠO MENU (THỰC ĐƠN PHONG PHÚ)
        # ==========================================
        print("🍱  Đang khởi tạo Thực Đơn...")
        
        thuc_don = ThucDon()
        db.session.add(thuc_don)
        db.session.flush()

        # Nhóm món
        nhom_khai_vi = NhomMon(ten="Khai Vị", thuc_don_id=thuc_don.id)
        nhom_mon_chinh = NhomMon(ten="Món Chính", thuc_don_id=thuc_don.id)
        nhom_lau = NhomMon(ten="Lẩu", thuc_don_id=thuc_don.id)
        nhom_com = NhomMon(ten="Cơm", thuc_don_id=thuc_don.id)
        nhom_nuoc = NhomMon(ten="Nước Uống", thuc_don_id=thuc_don.id)
        nhom_trang_mieng = NhomMon(ten="Tráng Miệng", thuc_don_id=thuc_don.id)

        db.session.add_all([nhom_khai_vi, nhom_mon_chinh, nhom_lau, nhom_com, nhom_nuoc, nhom_trang_mieng])
        db.session.flush()

        # Nhóm tùy chọn
        ntc_da = NhomTuyChon(ten="Mức Đá", loai=LoaiNhomTuyChon.SINGLE)
        ntc_duong = NhomTuyChon(ten="Mức Đường", loai=LoaiNhomTuyChon.SINGLE)
        ntc_cay = NhomTuyChon(ten="Độ Cay", loai=LoaiNhomTuyChon.SINGLE)
        
        db.session.add_all([ntc_da, ntc_duong, ntc_cay])
        db.session.flush()

        # Tùy chọn chi tiết
        tc_da_it = TuyChonMon(ten="Ít đá", gia=0, nhom_tuy_chon=ntc_da)
        tc_da_bt = TuyChonMon(ten="Bình thường", gia=0, nhom_tuy_chon=ntc_da)
        tc_da_nhieu = TuyChonMon(ten="Nhiều đá", gia=0, nhom_tuy_chon=ntc_da)
        
        tc_duong_0 = TuyChonMon(ten="Không đường", gia=0, nhom_tuy_chon=ntc_duong)
        tc_duong_30 = TuyChonMon(ten="30% đường", gia=0, nhom_tuy_chon=ntc_duong)
        tc_duong_50 = TuyChonMon(ten="50% đường", gia=0, nhom_tuy_chon=ntc_duong)
        tc_duong_100 = TuyChonMon(ten="100% đường", gia=0, nhom_tuy_chon=ntc_duong)

        tc_cay_0 = TuyChonMon(ten="Không cay", gia=0, nhom_tuy_chon=ntc_cay)
        tc_cay_it = TuyChonMon(ten="Ít cay", gia=0, nhom_tuy_chon=ntc_cay)
        tc_cay_vua = TuyChonMon(ten="Vừa cay", gia=0, nhom_tuy_chon=ntc_cay)
        tc_cay_nhieu = TuyChonMon(ten="Siêu cay", gia=5000, nhom_tuy_chon=ntc_cay)

        db.session.add_all([tc_da_it, tc_da_bt, tc_da_nhieu, tc_duong_0, tc_duong_30, tc_duong_50, tc_duong_100, tc_cay_0, tc_cay_it, tc_cay_vua, tc_cay_nhieu])
        db.session.flush()

        # === KHAI VỊ ===
        mon_goi_cuon = MoTaMon(ten="Gỏi cuốn tôm thịt", gia=45000, nhom_mon_id=nhom_khai_vi.id)
        mon_cha_gio = MoTaMon(ten="Chả giò chiên giòn", gia=55000, nhom_mon_id=nhom_khai_vi.id)
        mon_salad = MoTaMon(ten="Salad trộn thập cẩm", gia=65000, nhom_mon_id=nhom_khai_vi.id)
        mon_sup = MoTaMon(ten="Súp cua bắp", gia=40000, nhom_mon_id=nhom_khai_vi.id)

        # === MÓN CHÍNH ===
        mon_pho = MoTaMon(ten="Phở bò tái nạm", gia=65000, nhom_mon_id=nhom_mon_chinh.id)
        mon_bun_bo = MoTaMon(ten="Bún bò Huế", gia=70000, nhom_mon_id=nhom_mon_chinh.id)
        mon_hu_tieu = MoTaMon(ten="Hủ tiếu Nam Vang", gia=60000, nhom_mon_id=nhom_mon_chinh.id)
        mon_mi_quang = MoTaMon(ten="Mì Quảng", gia=55000, nhom_mon_id=nhom_mon_chinh.id)
        mon_banh_mi = MoTaMon(ten="Bánh mì thịt nướng", gia=35000, nhom_mon_id=nhom_mon_chinh.id)
        mon_bo_bit_tet = MoTaMon(ten="Bò bít tết", gia=150000, nhom_mon_id=nhom_mon_chinh.id)
        mon_suon_nuong = MoTaMon(ten="Sườn nướng BBQ", gia=120000, nhom_mon_id=nhom_mon_chinh.id)
        mon_ca_kho_to = MoTaMon(ten="Cá kho tộ", gia=85000, nhom_mon_id=nhom_mon_chinh.id)

        mon_pho.ds_nhom_tuy_chon.append(ntc_cay)
        mon_bun_bo.ds_nhom_tuy_chon.append(ntc_cay)

        # === LẨU ===
        mon_lau_thai = MoTaMon(ten="Lẩu Thái chua cay", gia=250000, nhom_mon_id=nhom_lau.id)
        mon_lau_nam = MoTaMon(ten="Lẩu nấm chay", gia=200000, nhom_mon_id=nhom_lau.id)
        mon_lau_hai_san = MoTaMon(ten="Lẩu hải sản", gia=350000, nhom_mon_id=nhom_lau.id)

        mon_lau_thai.ds_nhom_tuy_chon.append(ntc_cay)

        # === CƠM ===
        mon_com_tam = MoTaMon(ten="Cơm tấm sườn bì chả", gia=55000, nhom_mon_id=nhom_com.id)
        mon_com_chien = MoTaMon(ten="Cơm chiên Dương Châu", gia=50000, nhom_mon_id=nhom_com.id)
        mon_com_ga = MoTaMon(ten="Cơm gà Hội An", gia=60000, nhom_mon_id=nhom_com.id)

        # === NƯỚC UỐNG ===
        mon_cafe_sua = MoTaMon(ten="Cafe sữa đá", gia=25000, nhom_mon_id=nhom_nuoc.id)
        mon_cafe_den = MoTaMon(ten="Cafe đen", gia=20000, nhom_mon_id=nhom_nuoc.id)
        mon_tra_dao = MoTaMon(ten="Trà đào cam sả", gia=35000, nhom_mon_id=nhom_nuoc.id)
        mon_nuoc_ep = MoTaMon(ten="Nước ép cam", gia=30000, nhom_mon_id=nhom_nuoc.id)
        mon_sinh_to = MoTaMon(ten="Sinh tố xoài", gia=35000, nhom_mon_id=nhom_nuoc.id)
        mon_bia = MoTaMon(ten="Bia Sài Gòn", gia=20000, nhom_mon_id=nhom_nuoc.id)
        mon_nuoc_ngot = MoTaMon(ten="Pepsi/Coca", gia=15000, nhom_mon_id=nhom_nuoc.id)

        mon_cafe_sua.ds_nhom_tuy_chon.append(ntc_da)
        mon_cafe_sua.ds_nhom_tuy_chon.append(ntc_duong)
        mon_cafe_den.ds_nhom_tuy_chon.append(ntc_da)
        mon_tra_dao.ds_nhom_tuy_chon.append(ntc_da)
        mon_tra_dao.ds_nhom_tuy_chon.append(ntc_duong)

        # === TRÁNG MIỆNG ===
        mon_che = MoTaMon(ten="Chè thập cẩm", gia=25000, nhom_mon_id=nhom_trang_mieng.id)
        mon_kem = MoTaMon(ten="Kem 3 viên", gia=35000, nhom_mon_id=nhom_trang_mieng.id)
        mon_flan = MoTaMon(ten="Bánh flan", gia=20000, nhom_mon_id=nhom_trang_mieng.id)
        mon_trai_cay = MoTaMon(ten="Đĩa trái cây", gia=45000, nhom_mon_id=nhom_trang_mieng.id)

        ds_mon = [
            mon_goi_cuon, mon_cha_gio, mon_salad, mon_sup,
            mon_pho, mon_bun_bo, mon_hu_tieu, mon_mi_quang, mon_banh_mi, mon_bo_bit_tet, mon_suon_nuong, mon_ca_kho_to,
            mon_lau_thai, mon_lau_nam, mon_lau_hai_san,
            mon_com_tam, mon_com_chien, mon_com_ga,
            mon_cafe_sua, mon_cafe_den, mon_tra_dao, mon_nuoc_ep, mon_sinh_to, mon_bia, mon_nuoc_ngot,
            mon_che, mon_kem, mon_flan, mon_trai_cay
        ]
        db.session.add_all(ds_mon)
        db.session.flush()

        # ==========================================
        # 5. CẤU HÌNH THUẾ & KHUYẾN MÃI
        # ==========================================
        print("💰  Đang khởi tạo Thuế & Khuyến mãi...")
        
        thue = CauHinhThue(ten="VAT 10%", ti_le=0.1)
        km1 = KhuyenMaiTheoPhanTram(ten="Giảm 5% đơn trên 100k", mo_ta="Áp dụng tự động", gia_tri_don_hang_toi_thieu=100000, thu_tu_uu_tien=1, phan_tram=5)
        km2 = KhuyenMaiCung(ten="Chào bạn mới", mo_ta="Giảm 20k đơn từ 200k", gia_tri_don_hang_toi_thieu=200000, tu_dong_ap_dung=False, thu_tu_uu_tien=2, so_tien_tru=20000)
        km3 = KhuyenMaiTheoPhanTram(ten="VIP Member 10%", mo_ta="Dành cho thành viên VIP", gia_tri_don_hang_toi_thieu=500000, tu_dong_ap_dung=False, thu_tu_uu_tien=3, phan_tram=10)

        db.session.add_all([thue, km1, km2, km3])
        db.session.flush()

        # ==========================================
        # 6. TẠO DỮ LIỆU PHIÊN BÀN & DOANH THU (ĐÃ HOÀN THÀNH)
        # ==========================================
        print("📊  Đang tạo dữ liệu lịch sử (15 ngày gần nhất)...")

        all_bans = list_ban_a + list_ban_b + list_ban_vip
        
        # Tạo dữ liệu cho 15 ngày gần nhất
        for day_offset in range(15, 0, -1):
            ngay = datetime.datetime.now() - datetime.timedelta(days=day_offset)
            
            # Mỗi ngày có từ 5-12 đơn
            so_don = random.randint(5, 12)
            
            for _ in range(so_don):
                # Random giờ trong ngày (10h - 21h)
                gio = random.randint(10, 21)
                phut = random.randint(0, 59)
                tg_bat_dau = ngay.replace(hour=gio, minute=phut, second=0, microsecond=0)
                
                # Random bàn và phục vụ
                ban = random.choice(all_bans)
                phuc_vu = random.choice(ds_phuc_vu)
                
                # Tạo phiên bàn
                phien = PhienBan(
                    le_tan_id=random.choice([letan_1.nguoi_dung_id, letan_2.nguoi_dung_id]),
                    nguoi_dam_nhan_id=phuc_vu.nguoi_dung_id,
                    trang_thai=TrangThai.HOANTHANH
                )
                
                kg = KhungGioAn(
                    tg_bat_dau=tg_bat_dau,
                    tg_ket_thuc_du_kien=tg_bat_dau + datetime.timedelta(minutes=BienChung.THOIGIANCODINH),
                    trang_thai=TrangThai.HOANTHANH
                )
                phien.khung_gio = kg
                
                db.session.add(phien)
                db.session.flush()

                # Phân công
                pc = PhanCong(
                    phuc_vu_id=phuc_vu.nguoi_dung_id,
                    ban_id=ban.id,
                    phien_ban_id=phien.id,
                    trang_thai=TrangThai.HOANTHANH
                )
                db.session.add(pc)

                # Tạo phiếu món (1-2 phiếu mỗi phiên)
                so_phieu = random.randint(1, 2)
                tong_tien_phien = 0
                
                for _ in range(so_phieu):
                    phieu = PhieuMon(
                        phien_ban_id=phien.id,
                        trang_thai=TrangThaiPhieu.HOANTHANH
                    )
                    db.session.add(phieu)
                    db.session.flush()

                    # Thêm món vào phiếu (2-6 món)
                    so_mon = random.randint(2, 6)
                    ds_mon_random = random.sample(ds_mon, min(so_mon, len(ds_mon)))
                    
                    for mon in ds_mon_random:
                        so_luong = random.randint(1, 3)
                        mon_ghi = MonGhi(
                            so_luong=so_luong,
                            phieu_mon_id=phieu.id,
                            mo_ta_mon_id=mon.id,
                            trang_thai=TrangThaiMonGhi.HOANTHANH
                        )
                        # Cập nhật ngày tạo để match với phiên
                        mon_ghi.ngay_tao = tg_bat_dau
                        db.session.add(mon_ghi)
                        tong_tien_phien += mon.gia * so_luong

                db.session.flush()

                # Tạo doanh thu
                tien_giam = 0
                if tong_tien_phien >= 100000:
                    tien_giam = int(tong_tien_phien * 0.05)
                
                tien_sau_giam = tong_tien_phien - tien_giam
                tien_thue = int(tien_sau_giam * 0.1)
                tien_cuoi = tien_sau_giam - tien_thue

                dt = DoanhThu(
                    tong_tien=tong_tien_phien,
                    tien_giam_gia=tien_giam,
                    tien_cuoi_cung=tien_cuoi,
                    trang_thai=TrangThaiDoanhThu.DAHOANTHANH,
                    ten_thue="VAT 10%",
                    ti_le_thue=0.1,
                    tien_thue=tien_thue,
                    thu_ngan_id=random.choice([thungan.nguoi_dung_id, thungan2.nguoi_dung_id]),
                    phien_ban_id=phien.id
                )
                dt.ngay_tao = tg_bat_dau
                db.session.add(dt)
                db.session.flush()

                # Tạo thanh toán
                tt = ThanhToan(
                    so_tien=tien_cuoi,
                    phuong_thuc=random.choice([PhuongThucThanhToan.TIENMAT, PhuongThucThanhToan.STRIPE]),
                    trang_thai=TrangThaiThanhToan.THANHCONG,
                    doanh_thu_id=dt.id
                )
                db.session.add(tt)

        # ==========================================
        # 7. TẠO PHIÊN ĐANG HOẠT ĐỘNG (HÔM NAY)
        # ==========================================
        print("🔄  Đang tạo phiên hoạt động hiện tại...")
        
        # 2 phiên đang hoạt động
        for i, (ban, pv) in enumerate([(list_ban_a[0], pv_a1), (list_ban_b[0], pv_b1)]):
            tg_now = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(10, 30))
            
            phien_mo = PhienBan(
                le_tan_id=letan_1.nguoi_dung_id,
                nguoi_dam_nhan_id=pv.nguoi_dung_id,
                trang_thai=TrangThai.MO
            )
            
            kg_mo = KhungGioAn(
                tg_bat_dau=tg_now,
                tg_ket_thuc_du_kien=tg_now + datetime.timedelta(minutes=BienChung.THOIGIANCODINH),
                trang_thai=TrangThai.MO
            )
            phien_mo.khung_gio = kg_mo
            
            db.session.add(phien_mo)
            db.session.flush()

            # Cập nhật trạng thái bàn
            ban.trang_thai = TrangThaiBan.COKHACH
            ban.ds_khung_gio.append(kg_mo)

            # Phân công
            pc_mo = PhanCong(
                phuc_vu_id=pv.nguoi_dung_id,
                ban_id=ban.id,
                phien_ban_id=phien_mo.id,
                trang_thai=TrangThai.MO
            )
            db.session.add(pc_mo)

            # Tạo phiếu món đang chờ bếp
            phieu_mo = PhieuMon(
                phien_ban_id=phien_mo.id,
                trang_thai=TrangThaiPhieu.DAGUI
            )
            db.session.add(phieu_mo)
            db.session.flush()

            # Thêm món
            ds_mon_random = random.sample(ds_mon, 3)
            for mon in ds_mon_random:
                mg = MonGhi(
                    so_luong=random.randint(1, 2),
                    phieu_mon_id=phieu_mo.id,
                    mo_ta_mon_id=mon.id,
                    trang_thai=TrangThaiMonGhi.CHUANAU
                )
                db.session.add(mg)

        # ==========================================
        # 8. TẠO YÊU CẦU ĐANG CHỜ DUYỆT
        # ==========================================
        print("📋  Đang tạo yêu cầu chờ duyệt...")

        # Lấy một số món ghi từ phiên đang hoạt động để tạo yêu cầu
        # Tạo 3-5 yêu cầu pending
        for i in range(random.randint(3, 5)):
            # Tạo phiên và món ghi mới cho yêu cầu
            tg = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(5, 60))
            
            phien_yc = PhienBan(
                le_tan_id=letan_1.nguoi_dung_id,
                nguoi_dam_nhan_id=random.choice(ds_phuc_vu).nguoi_dung_id,
                trang_thai=TrangThai.MO
            )
            kg_yc = KhungGioAn(
                tg_bat_dau=tg,
                tg_ket_thuc_du_kien=tg + datetime.timedelta(minutes=60),
                trang_thai=TrangThai.MO
            )
            phien_yc.khung_gio = kg_yc
            db.session.add(phien_yc)
            db.session.flush()

            phieu_yc = PhieuMon(phien_ban_id=phien_yc.id, trang_thai=TrangThaiPhieu.DAGUI)
            db.session.add(phieu_yc)
            db.session.flush()

            mon = random.choice(ds_mon)
            mg_yc = MonGhi(
                so_luong=1,
                phieu_mon_id=phieu_yc.id,
                mo_ta_mon_id=mon.id,
                trang_thai=TrangThaiMonGhi.TAMNGUNG  # Đang chờ xử lý
            )
            db.session.add(mg_yc)
            db.session.flush()

            # Tạo yêu cầu
            ly_do_list = [
                "Khách muốn hủy món vì đợi lâu",
                "Món bị sai, khách yêu cầu đổi",
                "Khách đổi ý không muốn ăn món này",
                "Món bị nguội, khách yêu cầu hủy",
                "Khách báo dị ứng thực phẩm"
            ]
            
            yc = YCMonGhi(
                ly_do=random.choice(ly_do_list),
                trang_thai=TrangThaiYeuCau.CHODUYET,
                trang_thai_truoc=TrangThaiMonGhi.CHUANAU,
                mon_ghi_id=mg_yc.id
            )
            yc.ngay_tao = tg
            db.session.add(yc)

        # ==========================================
        # COMMIT
        # ==========================================
        db.session.commit()
        
        print("")
        print("✨ ═══════════════════════════════════════════════════ ✨")
        print("        ĐÃ KHỞI TẠO MOCK DATA THÀNH CÔNG!")
        print("✨ ═══════════════════════════════════════════════════ ✨")
        print("")
        print("📌 DANH SÁCH TÀI KHOẢN:")
        print("─────────────────────────────────────────────────────")
        print("  👑 Admin:     admin / admin123")
        print("  📊 Quản lý:   quanly / 123")
        print("  💰 Thu ngân:  thungan / 123")
        print("  👨‍🍳 Đầu bếp:  daubep1 / 123")
        print("  🎀 Lễ tân:    letan1 / 123")
        print("  🍽️  Phục vụ:  pv_a1, pv_a2, pv_b1... / 123")
        print("─────────────────────────────────────────────────────")
        print("")
        print("📈 DỮ LIỆU ĐÃ TẠO:")
        print(f"  • 15 ngày dữ liệu lịch sử")
        print(f"  • ~100+ đơn hàng hoàn thành")
        print(f"  • 29 món ăn trong thực đơn")
        print(f"  • 2 phiên đang hoạt động")
        print(f"  • 3-5 yêu cầu chờ duyệt")
        print("")

if __name__ == '__main__':
    seed_data()
