const phieuBep = {
    ds_phieu_mon: [],
    els: {
        sessionGrid: document.querySelector('.session-grid')
    },
    init: function () {
        // Lấy danh sách phiếu chờ thô từ script tag
        const el = document.getElementById('tickets-raw');
        if (el) {
            try {
                this.ds_phieu_mon = JSON.parse(el.textContent);
            } catch (e) {
                console.error("Lỗi khi load danh sách phiếu bếp:", e);
            }
        }
    },
    nhanThemPhieu: function (data) {
        // Khi có phiếu mới từ phục vụ gửi xuống
        this.ds_phieu_mon = [...this.ds_phieu_mon, data];
        let inner = ``;
        this.ds_phieu_mon.forEach((phieu_mon) => {
            inner += `
            <a href="http://127.0.0.1:5000/bep/phieu-mon/${phieu_mon.id}" class="session-card">
            <div class="card-header">
                <strong style="color: #2D3748;">Phiếu #${phieu_mon.id}</strong>
                <span class="badge badge-sent">Đã gửi bếp</span>
            </div>
            <p class="card-info">🕒 Tạo lúc: ${phieu_mon.ngay_tao}</p>
            <div
                style="margin-top: 15px; text-align: right; color: var(--primary-color); font-weight: 600; font-size: 0.9em;">
                Xem →
            </div>
        </a>
            `
        });
        this.els.sessionGrid.innerHTML = inner;
    }

}


document.addEventListener('DOMContentLoaded', () => phieuBep.init());
export { phieuBep }