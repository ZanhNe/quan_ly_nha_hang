const tamTinhBtn = document.querySelector('button.btn-provisional');
const kmBtn = document.querySelector('button.btn-promo');
const ttBtn = document.querySelector('button.btn-pay');

const previewEl = document.getElementById('preview-data-json');
const phienEl = document.getElementById('phien-data-json');
const dskmEl = document.getElementById('dskm-data-json');

const totalEl = document.getElementById('rawTotal');
const discountEl = document.getElementById('discountValue');
const taxEl = document.getElementById('taxValue');
const finalEl = document.getElementById('finalTotal');


let payload = {
    ids: []
}

const ds_khuyen_mai = JSON.parse(dskmEl.textContent);
const phien_ban = JSON.parse(phienEl.textContent);
const preview = JSON.parse(previewEl.textContent);

// 0. KHỞI TẠO STRIPE (Ở đầu file JS)
// Thay pk_test_... bằng Key của bạn
const stripe = Stripe("pk_test_51SfE2JBtQUhREE2Mbt9pAYFKH68NRW4xYVqtb0FWzOxv6lhTljl2gW0dTarGvpZaMfYx0F34s6hAVFvvH0iLm7lX00fMYfCT7K");

const km = ds_khuyen_mai.reduce((acc, value) => {
    acc[value.id] = value.ten
    return acc
}, {});

const KHUYENMAI_ID = null;

const doanh_thu_id = preview?.id ? preview.id : null;


tamTinhBtn.addEventListener('click', (e) => {
    inTamTinh();
})

kmBtn.addEventListener('click', (e) => {
    moModalKhuyenMai();
})

ttBtn.addEventListener('click', (e) => {
    moModalThanhToan();
})




function inTamTinh() {
    // Gọi API in tạm tính hoặc mở tab mới
    fetch(`http://127.0.0.1:5000/api/v1/phien-ban/${phien_ban.id}/doanh_thu/preview`)
        .then((resp) => resp.json())
        .then((data) => console.log(data));
}

async function apDungKhuyenMai(km_id) {
    payload = {
        ids: [+km_id]
    }

    console.log(payload)
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/doanh-thu/${doanh_thu_id}`, {
            method: 'PUT',
            headers: {
                'Content-type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            const errMsg = errorData.message;
            throw new Error(errMsg);
        }
        Swal.fire({
            icon: 'success',
            title: 'Thành công!',
            text: 'Áp dụng khuyến mãi thành công!',
            timer: 2000,              // Tự tắt sau 2 giây
            showConfirmButton: false  // Không cần nút bấm
        });

        const data = await response.json();
        return data;
    } catch (error) {
        Swal.fire({
            icon: 'error',               // Icon lỗi (dấu X đỏ đẹp mắt)
            title: 'Úi chà!',            // Tiêu đề
            text: error.message,         // Nội dung lỗi (lấy từ server)
            confirmButtonText: 'Đóng'    // Chữ trên nút
        });
    }

}

async function moModalKhuyenMai() {
    if (!doanh_thu_id) {
        Swal.fire({
            icon: 'error',
            title: 'Úi chà!',
            text: 'Bạn chưa tính tạm bill để có thể áp dụng khuyến mãi.',
            confirmButtonText: 'Đóng'
        });
        return;
    }

    const { value: couponCode } = await Swal.fire({
        title: 'Áp dụng Khuyến mãi',
        input: 'select',
        inputOptions: km,
        inputPlaceholder: 'Chọn chương trình khuyến mãi',
        showCancelButton: true,
    });

    if (couponCode) {

        // Gọi Backend áp dụng khuyến mãi
        console.log("Apply KM ID:", couponCode);
        // location.reload() hoặc cập nhật UI số tiền
        const data = await apDungKhuyenMai(couponCode);
        totalEl.textContent = (data.tong_tien).toLocaleString('en-US', { maximumFractionDigits: 0 });;
        discountEl.textContent = (data.tien_giam_gia).toLocaleString('en-US', { maximumFractionDigits: 0 });;
        taxEl.textContent = (data.tien_thue).toLocaleString('en-US', { maximumFractionDigits: 0 });;
        finalEl.textContent = (data.tien_cuoi_cung).toLocaleString('en-US', { maximumFractionDigits: 0 });;
    }
}


async function moModalThanhToan() {

    if (!doanh_thu_id) {
        Swal.fire({
            icon: 'error',
            title: 'Úi chà!',
            text: 'Bạn chưa tính tạm bill để có thể thanh toán',
            confirmButtonText: 'Đóng'
        });
        return;
    }

    // MODAL 1: CHỌN PHƯƠNG THỨC
    const { value: method } = await Swal.fire({
        title: 'Xác nhận Thanh toán',
        html: `
              <div class="text-start">
                  <p>Tổng tiền: <b>${document.getElementById('finalTotal').innerText}</b></p>
                  <label class="form-label">Hình thức:</label>
                  <select id="paymentMethod" class="form-control">
                      <option value="tienmat">💵 Tiền mặt</option>
                      <option value="stripe">💳 Stripe / Thẻ quốc tế</option>
                  </select>
              </div>
          `,
        focusConfirm: false,
        confirmButtonText: 'Tiếp tục',
        showCancelButton: true,
        preConfirm: () => {
            return document.getElementById('paymentMethod').value;
        }
    });

    if (!method) return; // User bấm hủy

    // XỬ LÝ THEO TỪNG PHƯƠNG THỨC
    if (method === 'tienmat') {
        // ... Code xử lý tiền mặt cũ của bạn giữ nguyên ...
        xyLyTienMat();
    } else if (method === 'stripe') {
        xuLyStripe();
    }
}

// HÀM TÁCH RIÊNG ĐỂ XỬ LÝ STRIPE
async function xuLyStripe() {
    try {
        // BƯỚC 1: Gọi Backend để tạo PaymentIntent và lấy clientSecret
        // Hiển thị loading trong lúc chờ server
        Swal.fire({
            title: 'Đang khởi tạo cổng thanh toán...',
            didOpen: () => Swal.showLoading()
        });

        const response = await fetch(`http://127.0.0.1:5000/api/v1/doanh-thu/${doanh_thu_id}/thanh-toan/online`, {
            method: 'POST',
            headers: { 'Content-type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload) // Gửi kèm thông tin khuyến mãi nếu có
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.message || "Lỗi khởi tạo thanh toán");

        const clientSecret = data.clientSecret; // Đảm bảo backend trả về field này
        console.log("clientSecret", clientSecret);

        // BƯỚC 2: HIỂN THỊ MODAL NHẬP THẺ
        let elements;

        await Swal.fire({
            title: 'Thanh toán qua Thẻ',
            // Tạo sẵn một div trống để Stripe mount vào
            html: `
                <div id="stripe-payment-element" style="min-height: 250px;"></div>
                <div id="stripe-error-message" class="text-danger mt-2"></div>
            `,
            width: 600,
            allowOutsideClick: false,
            confirmButtonText: 'Thanh toán ngay',
            showCancelButton: true,
            cancelButtonText: 'Hủy',

            // Hook này chạy ngay khi Modal hiện ra -> Lúc này div #stripe-payment-element đã có trong DOM
            didOpen: () => {
                const appearance = { theme: 'stripe' };
                elements = stripe.elements({ appearance, clientSecret });

                const paymentElement = elements.create("payment");
                paymentElement.mount("#stripe-payment-element");
            },

            // Hook này chạy khi user bấm nút "Thanh toán ngay"
            showLoaderOnConfirm: true, // Hiển thị vòng xoay loading trên nút bấm
            preConfirm: async () => {
                // Gọi Stripe xác nhận thanh toán
                const { error } = await stripe.confirmPayment({
                    elements,
                    confirmParams: {
                        // Redirect về trang hóa đơn sau khi thành công
                        // Backend của bạn nên trả về invoice_url hoặc bạn tự build url
                        return_url: `http://127.0.0.1:5000/thu-ngan/doanh-thu/${doanh_thu_id}`,
                    },
                    // Quan trọng: Chặn redirect tự động để xử lý lỗi nếu có ngay tại đây
                    // Tuy nhiên với mô hình redirect, bạn cứ để nó redirect.
                });

                // Nếu code chạy đến đây nghĩa là có lỗi (vì nếu thành công nó đã redirect rồi)
                if (error) {
                    Swal.showValidationMessage(`Lỗi: ${error.message}`);
                }
            }
        });

    } catch (error) {
        Swal.fire('Lỗi', error.message, 'error');
    }
}

// Tách hàm xử lý tiền mặt ra cho gọn
function xyLyTienMat() {
    fetch(`http://127.0.0.1:5000/api/v1/doanh-thu/${doanh_thu_id}/thanh-toan/tien-mat`, {
        method: 'POST',
        headers: { 'Content-type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    }).then((resp) => resp.json())
        .then((data) => {
            window.location.href = data.redirect_url;
        });
}




