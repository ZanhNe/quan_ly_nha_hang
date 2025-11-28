// ============================================================
// 1. KHỞI TẠO DỮ LIỆU & TRẠNG THÁI (STATE)
// ============================================================
// 1. Tìm thẻ chứa dữ liệu
const dataElement = document.getElementById("table-data-json");
// Nhận dữ liệu từ Flask (Jinja2 convert sang JSON Object)
const dsKhuVuc = JSON.parse(dataElement.textContent);

let serverTableData = dsKhuVuc.reduce((acc, val) => {
  return [...acc, ...val.ds_ban];
}, []);

console.log(serverTableData);
// Mảng lưu trữ ID các bàn đang được chọn
let selectedTableIds = [];

// Lấy các Element tĩnh để dùng lại (đỡ phải query nhiều lần)
const els = {
  drawer: document.getElementById("drawer"),
  overlay: document.getElementById("overlay"),
  drawerTitle: document.getElementById("drawerTitle"),
  focusTableName: document.getElementById("focusTableName"),
  timelineList: document.getElementById("timelineList"),
  selectionSummary: document.getElementById("selectionSummary"),
  btnAction: document.getElementById("btnAction"),
  errorMsg: document.getElementById("errorMsg"),
};

// ============================================================
// 2. HÀM XỬ LÝ SỰ KIỆN CHÍNH (HANDLE CLICK)
// ============================================================

function handleTableClick(tableId) {
  // Tìm object bàn tương ứng trong dữ liệu gốc

  const ban = serverTableData.find((t) => t.id === +tableId);
  if (!ban) return;

  // --- A. CẬP NHẬT GIAO DIỆN DRAWER (Xem chi tiết) ---
  renderDrawerContent(ban);
  openDrawer();

  // --- B. LOGIC CHỌN BÀN (Multi-select) ---

  // 1. Nếu bàn đang có khách hoặc đã giữ chỗ -> Không cho chọn để đánh dấu mới
  if (ban.trang_thai === "COKHACH" || ban.trang_thai === "GIUCHO") {
    return;
  }

  // 2. Toggle chọn/bỏ chọn
  const tableDiv = document.getElementById("table-" + tableId);

  if (selectedTableIds.includes(tableId)) {
    // Đang chọn -> Bỏ chọn
    selectedTableIds = selectedTableIds.filter((id) => id !== tableId);
    tableDiv.classList.remove("is-selected");
  } else {
    // Chưa chọn -> Thêm vào danh sách
    selectedTableIds.push(tableId);
    tableDiv.classList.add("is-selected");
  }

  // --- C. CẬP NHẬT NÚT BẤM ---
  updateFooterButton();
}

// ============================================================
// 3. HÀM RENDER NỘI DUNG DRAWER (Cái bạn đang cần)
// ============================================================

function renderDrawerContent(ban) {
  // 1. Cập nhật tiêu đề
  els.drawerTitle.innerText = `Chi tiết ${ban.id}`;
  els.focusTableName.innerText = ban.ten;

  // 2. Xóa nội dung cũ
  els.timelineList.innerHTML = "";
  let htmlContent = "";

  // 3. Tạo HTML mới dựa trên trạng thái bàn

  // TRƯỜNG HỢP 1: Bàn đang có khách
  if (ban.trang_thai === "COKHACH") {
    htmlContent += `
                <div class="timeline-item">
                    <div class="timeline-time">Hiện tại</div>
                    <div class="timeline-content" style="background: #FFF5F5; border-color: #FEB2B2;">
                        <strong style="color: #C53030;">Đang phục vụ khách</strong>
                        <div style="font-size: 0.9em; color: #555; margin-top: 4px;">
                            Vui lòng đợi khách thanh toán.
                        </div>
                    </div>
                </div>
            `;
  }
  // TRƯỜNG HỢP 2: Bàn trống và KHÔNG có booking nào
  else if (
    ban.trang_thai === "TRONG" &&
    (!ban.ds_khung_gio || ban.ds_khung_gio.length === 0)
  ) {
    htmlContent += `
                <div style="text-align: center; padding: 20px; background: #F0FFF4; border: 1px dashed #48BB78; border-radius: 8px;">
                    <div style="font-size: 1.5em;">✅</div>
                    <strong style="color: #2F855A;">Bàn trống</strong>
                    <p style="margin: 5px 0 0; font-size: 0.9em; color: #555;">
                        Không có lịch đặt trước trong thời gian tới.
                    </p>
                </div>
            `;
  }
  // TRƯỜNG HỢP 3: Có Booking (Bất kể đang trống hay bận)
  else {
    // Render từng booking ra timeline
    ban.ds_khung_gio.forEach((khung_gio) => {
      htmlContent += `
                    <div class="timeline-item">
                        <div class="timeline-time">${khung_gio.tg_bat_dau}</div>
                        <div class="timeline-content">
                            <strong>Đặt trước</strong>
                        
                        </div>
                    </div>
                `;
    });

    // Nếu bàn đang trống nhưng có booking, thêm dòng thông báo hiện tại
    if (ban.trang_thai === "TRONG") {
      htmlContent =
        `
                    <div class="timeline-item">
                        <div class="timeline-time">Hiện tại</div>
                        <div class="timeline-content" style="background: #F0FFF4;">
                            <strong style="color: #2F855A;">Đang trống</strong>
                            <div style="font-size: 0.85em;">Có thể xếp khách vãng lai (cân nhắc khung giờ)</div>
                        </div>
                    </div>
                ` + htmlContent;
    }
  }

  // 4. Gán HTML vào DOM
  els.timelineList.innerHTML = htmlContent;
}

// ============================================================
// 4. HÀM LOGIC NÚT BẤM & VALIDATION (Client-side)
// ============================================================

function updateFooterButton() {
  // 1. Nếu chưa chọn bàn nào
  if (selectedTableIds.length === 0) {
    els.selectionSummary.innerText = "Chưa chọn bàn nào";
    els.btnAction.innerText = "Chọn bàn để tiếp tục";
    els.btnAction.disabled = true;
    els.btnAction.style.background = ""; // Reset về default CSS
    if (els.errorMsg) els.errorMsg.style.display = "none";
    return;
  }

  // 2. Cập nhật text
  els.selectionSummary.innerText = `Đang chọn: ${selectedTableIds.join(", ")}`;
  els.btnAction.disabled = false;

  // 3. Kiểm tra "Xung đột giờ giấc" (Warning Logic)
  let hasWarning = false;
  const currentHour = new Date().getHours(); // Lấy giờ hiện tại của máy tính

  selectedTableIds.forEach((id) => {
    const t = serverTableData.find((x) => x.id === id);
    // Logic: Nếu có booking và giờ booking - giờ hiện tại <= 1 tiếng
    if (t?.ds_khung_gio && t.ds_khung_gio.length > 0) {
      const bookTimeStr = t.ds_khung_gio[0].tg_bat_dau; // Ví dụ "19:00"
      const bookHour = parseInt(bookTimeStr.split("T")[1].split(":")[0]); //2025-11-23T09:38:04 --> Lọc T trước, sau đó lọc :

      if (bookHour - currentHour <= 1 && bookHour - currentHour >= 0) {
        hasWarning = true;
      }
    }
  });

  // 4. Thay đổi màu nút dựa trên Warning
  if (hasWarning) {
    els.btnAction.style.background = "var(--color-warning)"; // Màu vàng (định nghĩa trong CSS base)
    els.btnAction.innerText = `⚠️ Xác nhận (${selectedTableIds.length} bàn)`;
    if (els.errorMsg) {
      els.errorMsg.style.display = "block";
      els.errorMsg.innerText = "Lưu ý: Có bàn sắp đến giờ khách đặt!";
    }
  } else {
    els.btnAction.style.background = "var(--primary-color)"; // Màu hồng chính
    els.btnAction.innerText = `Xác nhận (${selectedTableIds.length} bàn)`;
    if (els.errorMsg) els.errorMsg.style.display = "none";
  }
}

// ============================================================
// 5. CÁC HÀM TIỆN ÍCH KHÁC (DRAWER, SUBMIT)
// ============================================================

function openDrawer() {
  els.drawer.classList.add("open");
  els.overlay.classList.add("show");
}

function closeDrawer() {
  els.drawer.classList.remove("open");
  els.overlay.classList.remove("show");
}

// Đóng Drawer khi click ra ngoài overlay
els.overlay.addEventListener("click", closeDrawer);

// SỰ KIỆN GỬI DỮ LIỆU (Khi bấm nút Xác nhận)
els.btnAction.addEventListener("click", function () {
  if (selectedTableIds.length === 0) return;

  const confirmMsg = `Bạn có chắc chắn muốn đánh dấu khách cho bàn: ${selectedTableIds.join(
    ", "
  )}?`;
  if (!confirm(confirmMsg)) return;

  data = selectedTableIds.map((val) => {
    return { id: +val };
  });
  // Gửi dữ liệu về Flask bằng Fetch API
  fetch("http://localhost:5000/api/v1/bans", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Nếu có CSRF token thì thêm vào đây
      // 'X-CSRFToken': '{{ csrf_token() }}'
    },
    body: JSON.stringify({ table_ids: data }),
  })
    .then((response) => {
      if (response.ok) {
        // Thành công -> Reload trang để cập nhật trạng thái mới từ Server
        console.log("Thành công");
        return response.json();
      } else {
        alert("Có lỗi xảy ra, vui lòng thử lại!");
      }
    })
    .then((data) => {
      serverTableData = [...serverTableData.filter((ban) => {
        return data.every((ban_data) => ban_data.id !== ban.id);
      }), ...data].sort((ban_1, ban_2) => ban_1.id - ban_2.id);

      data.forEach((ban) => {
        const banEl = document.querySelector(`#table-${ban.id}`);
        banEl.classList.remove('is-selected');
        banEl.classList.remove('status-trong');
        banEl.classList.add('status-cokhach');
        const tagEl = banEl.querySelector('.warning-tag');

        if (tagEl) {
          tagEl.classList.toggle('dang-an');
        tagEl.textContent = 'Đang ăn';
        }
        else {
          banEl.insertAdjacentHTML('beforeend', '<div class="warning-tag dang-an">Đang ăn</div>')
        }

      })
      selectedTableIds = [];
      closeDrawer();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Lỗi kết nối server!");
    });
});
