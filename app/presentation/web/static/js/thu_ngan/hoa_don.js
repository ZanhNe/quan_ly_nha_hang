const doanh_thu_id = document.getElementById("phien-id").dataset.id; // Lấy ID phiên để thực hiện polling
const POLLING_INTERVAL = 3000; // Kiểm tra lại trạng thái sau mỗi 3 giây
let isPolling = false;

// Lấy trạng thái ban đầu của phiên từ thuộc tính data
const initialStatus = document.getElementById("initial-status").dataset.status;

if (initialStatus !== "DAHOANTHANH") {
  startPolling();
}

function startPolling() {
  if (isPolling) return;
  isPolling = true;
  // Hiện hiệu ứng chờ, ẩn các nút hành động trong khi chờ thanh toán hoàn tất
  document.getElementById("loadingOverlay").style.display = "flex";
  document.getElementById("actionButtons").style.display = "none";

  const poll = setInterval(async () => {
    try {
      // Gọi API check trạng thái phiên bàn (trả về JSON PhienBanOutSchema)
      const response = await fetch(`/api/v1/doanh-thu/${doanh_thu_id}`, {
        credentials: 'include'
      });
      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();
      console.log(data)
      // Kiểm tra trạng thái doanh thu trong object trả về
      // Cấu trúc dựa trên Schema: phien_ban -> doanh_thu -> trang_thai
      if (data && data.trang_thai === "DAHOANTHANH") {
        clearInterval(poll);
        isPolling = false;
        renderBill(data);
        document.getElementById("loadingOverlay").style.display = "none";
        document.getElementById("actionButtons").style.display = "block";

        // Phát âm thanh hoặc thông báo
        Swal.fire({
          icon: "success",
          title: "Thanh toán thành công!",
          timer: 1500,
          showConfirmButton: false,
        });
      }
    } catch (error) {
      console.error("Polling error:", error);
      // Có thể hiển thị nút "Thử lại" nếu lỗi liên tục
    }
  }, POLLING_INTERVAL);
}

function renderBill(data) {
  // Đổ dữ liệu hóa đơn vào giao diện để in
  document.getElementById("billDate").innerText = new Date(
    data.ngay_tao
  ).toLocaleString("vi-VN");

  // Xóa danh sách cũ và render lại từ đầu
  const tbody = document.getElementById("billItemsBody");
  tbody.innerHTML = "";

  let subTotal = 0;

  if (data.phien_ban.ds_phieu_mon) {
    data.phien_ban.ds_phieu_mon.forEach((phieu) => {
      if (phieu.ds_mon_ghi) {
        phieu.ds_mon_ghi.forEach((mon) => {
          // Tính tiền từng món, bao gồm cả topping/tùy chọn

          let itemTotal = mon.mo_ta_mon.gia * mon.so_luong;
          let optionsHtml = "";

          if (mon.ds_tuy_chon && mon.ds_tuy_chon.length > 0) {
            const optionNames = mon.ds_tuy_chon
              .map((opt) => {
                itemTotal += opt.gia; // Cộng giá topping
                return opt.ten;
              })
              .join(", ");
            optionsHtml = `<div class="item-options">+ ${optionNames}</div>`;
          }

          // Cộng vào tổng hàng (để verify)
          subTotal += itemTotal;

          const row = `
                            <tr>
                                <td>
                                    <div class="item-name">${mon.mo_ta_mon.ten
            }</div>
                                    ${optionsHtml}
                                </td>
                                <td>${mon.so_luong}</td>
                                <td style="text-align: right">
                                    ${itemTotal.toLocaleString("vi-VN")}
                                </td>
                            </tr>
                        `;
          tbody.insertAdjacentHTML("beforeend", row);
        });
      }
    });
  }

  // Cập nhật Summary
  const dt = data.tong_tien;
  document.getElementById("subTotal").innerText =
    dt.toLocaleString("vi-VN");
  document.getElementById("discountAmount").innerText =
    "- " + data.tien_giam_gia.toLocaleString("vi-VN");

  const taxPercent = dt.ti_le_thue ? Math.round(dt.ti_le_thue * 100) : 0;
  document.getElementById(
    "taxAmount"
  ).parentElement.innerHTML = `<span>VAT (${taxPercent}%):</span> <span id="taxAmount">${data.tien_thue.toLocaleString(
    "vi-VN"
  )}</span>`;

  document.getElementById("finalTotal").innerText =
    data.tien_cuoi_cung.toLocaleString("vi-VN");

  // Cập nhật badge trạng thái
  const statusBadge = document.getElementById("paymentStatus");
  statusBadge.className = "status-badge status-success";
  statusBadge.innerText = "ĐÃ THANH TOÁN";
}
