// 1. Tìm thẻ chứa dữ liệu
const dataElement = document.getElementById("phien-data-json");
// Nhận dữ liệu từ Flask (Jinja2 convert sang JSON Object)
let dsPhienBan = JSON.parse(dataElement.textContent);
const prefix = 'http://127.0.0.1:5000'
const sessionGridElm = document.querySelector('.session-grid');


sessionGridElm.addEventListener('click', function (e) {
    const confirmBtn = e.target.closest('button.btn-confirm');
    if (confirmBtn) {
        const confirmMsg = `Bạn có chắc chắn muốn đảm nhận cho phiên bàn?`;
        if (!confirm(confirmMsg)) return;

        const phienId = confirmBtn.dataset.phienId;

        xuLyDamNhan(phienId);
    }
});

async function xuLyDamNhan(phienId) {
    try {
        const response = await fetch(`${prefix}/api/v1/phien-ban/${phienId}/dam-nhan`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-type': 'application/json',
            },
        });
        if (!response.ok) {
            const errorData = await response.json();
            const errMsg = errorData.message;
            throw new Error(errMsg);
        }

        const data = await response.json();
        dsPhienBan = dsPhienBan.map((phien) => {
            if (phien.id !== data.id) return phien;
            else return data;
        });
        let innerHTML = ``
        dsPhienBan.forEach((phien) => {
            innerHTML += `
            <div class="session-card">
            <div class="card-header">
                <h3 class="card-title">${phien.id}</h3>
                <span class="badge ${phien.trang_thai === 'MO' ? 'badge-open' : 'badge-draft'}badge-open">${phien.trang_thai === 'MO' ? '⏳ Đang hoạt động' : 'Trống'}</span>
            </div>

            <p class="card-info">🕒 Bắt đầu: ${phien.khung_gio.tg_bat_dau}</p>
            <div style="background: #F7FAFC; padding: 8px; border-radius: 8px; margin-bottom: 15px; font-size: 0.9em;">
                ${phien.nguoi_dam_nhan_id ? '<strong>🧑‍💼 Đã có người đảm nhận</strong>' : '<span style="color: #A0AEC0;">Chưa có người đảm nhận</span>'}
            </div>

            <div style="margin-top: auto; display: flex; gap: 10px;">
                ${phien.nguoi_dam_nhan_id ? '' : `
                    <div style="flex: 1;">
                        <button data-phien-id="${phien.id}" type="button" class="btn-confirm" style="width: 100%; background: #4299E1; font-size: 0.9em;">
                            ✋ Đảm nhận
                        </button>
                    </div>`}
                <a href="${`${prefix}/danh-sach-phien/chi-tiet/${phien.id}`}" class="btn-confirm" style="flex: 1; text-align: center; text-decoration: none; font-size: 0.9em;">
                    📄 Chi tiết
                </a>
            </div>
        </div>
                `;
        });

        sessionGridElm.innerHTML = innerHTML;
        Swal.fire({
            icon: 'success',
            title: 'Thành công!',
            text: 'Đảm nhận phiên thành công!',
            timer: 2000,              // Tự tắt sau 2 giây
            showConfirmButton: false  // Không cần nút bấm
        });
    } catch (error) {
        Swal.fire({
            icon: 'error',               // Icon lỗi (dấu X đỏ đẹp mắt)
            title: 'Úi chà!',            // Tiêu đề
            text: error.message,         // Nội dung lỗi (lấy từ server)
            confirmButtonText: 'Đóng'    // Chữ trên nút
        });
    }
}