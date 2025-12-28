const phieuForm = document.querySelector('#phieu-form')
// Lấy data danh sách phiếu từ script tag
const dataElement = document.getElementById("dsphieu-data-json");
let dsPhieuMon = JSON.parse(dataElement.textContent);
const prefix = 'http://127.0.0.1:5000'
console.log(dsPhieuMon)

const sessionGridElm = document.querySelector('.session-grid');

console.log(sessionGridElm);

phieuForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const url = e.target.action;
    const method = e.target.method;

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-type': 'application/json',
            },
            credentials: 'include'

        });
        if (!response.ok) {
            const errorData = await response.json();
            const errMsg = errorData.message;
            throw new Error(errMsg);
        }

        const data = await response.json();

        // Thêm phiếu mới vừa tạo vào danh sách hiển thị
        dsPhieuMon = [...dsPhieuMon, data]

        let inner = ``

        if (dsPhieuMon.length !== 0) {

            dsPhieuMon.forEach((phieu) => {
                inner += `
                <a href="${prefix}/phien-ban/${phieu.phien_ban_id}/phieu-mon/${phieu.id}" class="session-card">
                    <div class="card-header">
                        <strong style="color: #2D3748;">Phiếu #${phieu.id}</strong>
                        <span class="badge ${phieu.trang_thai === 'DANGGHI' ? 'badge-draft' : phieu.trang_thai === 'DAGUI' ? 'badge-sent' : 'badge-done'}">${phieu.trang_thai === 'DANGGHI' ? 'Đang ghi món' : phieu.trang_thai === 'DAGUI' ? 'Đã gửi bếp' : 'Hoàn thành'}</span>
                    </div>
                    <p class="card-info">🕒 Tạo lúc: ${phieu.ngay_tao}</p>
                    <!-- <p class="card-info">📦 Số lượng: món</p> -->
                    <div style="margin-top: 15px; text-align: right; color: var(--primary-color); font-weight: 600; font-size: 0.9em;">
                        Xem / Sửa →
                    </div>
                </a>
                `
            })

        } else {
            inner += `
            <p style="color: #A0AEC0; grid-column: 1/-1; text-align: center;">Chưa có phiếu món nào.</p>
            `
        }

        sessionGridElm.innerHTML = inner
        Swal.fire({
            icon: 'success',
            title: 'Ngon lành!',
            text: 'Đã tạo xong phiếu món mới!',
            timer: 2000,
            showConfirmButton: false
        });
        console.log(data);

    } catch (error) {
        Swal.fire({
            icon: 'error',               // Icon lỗi (dấu X đỏ đẹp mắt)
            title: 'Úi chà!',            // Tiêu đề
            text: error.message,         // Nội dung lỗi (lấy từ server)
            confirmButtonText: 'Đóng'    // Chữ trên nút
        });
    }

});