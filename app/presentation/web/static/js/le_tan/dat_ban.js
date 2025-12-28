// ============================================================
// ĐẶT BÀN - Table Reservation JavaScript Module
// ============================================================

// ============================================================
// 1. KHỞI TẠO DỮ LIỆU & ELEMENTS
// ============================================================
const dataElement = document.getElementById("table-data-json");
const dsKhuVuc = JSON.parse(dataElement.textContent);

let serverTableData = dsKhuVuc.reduce((acc, val) => [...acc, ...val.ds_ban], []);
let selectedTableIds = [];
let currentFocusedTable = null;

// Cache DOM elements
const els = {
    // Overlay & Drawer
    drawer: document.getElementById("drawer"),
    overlay: document.getElementById("overlay"),
    closeBtn: document.getElementById("btn-close"),

    // Tabs
    tabDetails: document.getElementById("tabDetails"),
    tabBooking: document.getElementById("tabBooking"),
    contentDetails: document.getElementById("contentDetails"),
    contentBooking: document.getElementById("contentBooking"),

    // Details Tab
    focusTableName: document.getElementById("focusTableName"),
    timelineList: document.getElementById("timelineList"),

    // Booking Tab
    selectedTablesText: document.getElementById("selectedTablesText"),
    bookingForm: document.getElementById("bookingForm"),

    // Form Fields
    tenKhach: document.getElementById("tenKhach"),
    sdt: document.getElementById("sdt"),
    soLuong: document.getElementById("soLuong"),
    tgDen: document.getElementById("tgDen"),
    ghiChu: document.getElementById("ghiChu"),

    // Footer
    selectionCount: document.getElementById("selectionCount"),
    errorMsg: document.getElementById("errorMsg"),
    btnSubmit: document.getElementById("btnSubmit"),

    // Container
    zonesContainer: document.getElementById("allZonesContainer"),
};

// Set minimum datetime to now
const now = new Date();
now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
els.tgDen.min = now.toISOString().slice(0, 16);

// ============================================================
// 2. EVENT LISTENERS
// ============================================================

// Click on table cards (Event Delegation)
els.zonesContainer.addEventListener("click", (e) => {
    const tableEl = e.target.closest(".table");
    if (tableEl) {
        handleTableClick(tableEl.dataset.tableId, tableEl.dataset.khuVucId);
    }
});

// Close drawer
els.closeBtn.addEventListener("click", closeDrawer);
els.overlay.addEventListener("click", closeDrawer);

// Tab switching
els.tabDetails.addEventListener("click", () => switchTab("details"));
els.tabBooking.addEventListener("click", () => switchTab("booking"));

// Form submission
els.btnSubmit.addEventListener("click", handleSubmit);

// ============================================================
// 3. TABLE CLICK HANDLER
// ============================================================

function handleTableClick(tableId, khuVucId) {
    const ban = serverTableData.find((t) => t.id === +tableId);
    if (!ban) return;

    // Update drawer content
    renderDrawerContent(ban);
    openDrawer();

    // Don't allow selecting occupied tables
    if (ban.trang_thai === "COKHACH") {
        showError("Bàn này đang có khách, không thể đặt!");
        return;
    }

    // Validate same zone for multi-table selection
    if (selectedTableIds.length > 0) {
        const firstSelectedTable = serverTableData.find(
            (t) => t.id === +selectedTableIds[0]
        );
        if (firstSelectedTable && firstSelectedTable.khu_vuc_id !== ban.khu_vuc_id) {
            showError("Chỉ được chọn các bàn cùng khu vực!");
            return;
        }
    }

    // Toggle selection
    const tableDiv = document.getElementById("table-" + tableId);

    if (selectedTableIds.includes(tableId)) {
        // Deselect
        selectedTableIds = selectedTableIds.filter((id) => id !== tableId);
        tableDiv.classList.remove("is-selected");
    } else {
        // Select
        selectedTableIds.push(tableId);
        tableDiv.classList.add("is-selected");
    }

    hideError();
    updateUI();
}

// ============================================================
// 4. DRAWER CONTENT RENDERING
// ============================================================

function renderDrawerContent(ban) {
    currentFocusedTable = ban;
    els.focusTableName.innerText = `${ban.ten} (${ban.so_ghe} người)`;

    let htmlContent = "";

    // Case 1: Table is occupied
    if (ban.trang_thai === "COKHACH") {
        htmlContent = `
      <div class="timeline-item">
        <div class="timeline-time">Hiện tại</div>
        <div class="timeline-content" style="background: #FFF5F5; border-color: #FEB2B2;">
          <strong style="color: #C53030;">🍽️ Đang phục vụ khách</strong>
          <div style="font-size: 0.9em; color: #555; margin-top: 4px;">
            Vui lòng đợi khách thanh toán xong.
          </div>
        </div>
      </div>
    `;
    }
    // Case 2: Empty table with no bookings
    else if (
        ban.trang_thai === "TRONG" &&
        (!ban.ds_khung_gio || ban.ds_khung_gio.length === 0)
    ) {
        htmlContent = `
      <div class="timeline-empty">
        <div class="timeline-empty-icon">✅</div>
        <p class="timeline-empty-text">Bàn trống hoàn toàn</p>
        <p class="timeline-empty-sub">Không có lịch đặt trước.</p>
      </div>
    `;
    }
    // Case 3: Has bookings
    else if (ban.ds_khung_gio && ban.ds_khung_gio.length > 0) {
        // Current status
        if (ban.trang_thai === "TRONG") {
            htmlContent += `
        <div class="timeline-item">
          <div class="timeline-time">Hiện tại</div>
          <div class="timeline-content" style="background: #F0FFF4; border-color: #9AE6B4;">
            <strong style="color: #2F855A;">✅ Đang trống</strong>
            <div style="font-size: 0.85em; color: #555;">Có thể đặt bàn (lưu ý các khung giờ bên dưới)</div>
          </div>
        </div>
      `;
        }

        // List all bookings
        ban.ds_khung_gio.forEach((khung_gio) => {
            const startTime = formatDateTime(khung_gio.tg_bat_dau);
            const endTime = formatDateTime(khung_gio.tg_ket_thuc_du_kien);
            const bookingType = khung_gio.type === "khung_gio_dat_ban" ? "📅 Đặt trước" : "🍽️ Phiên ăn";

            htmlContent += `
        <div class="timeline-item">
          <div class="timeline-time">${startTime}</div>
          <div class="timeline-content">
            <strong>${bookingType}</strong>
            <div style="font-size: 0.85em; color: #666;">
              Đến ${endTime}
            </div>
          </div>
        </div>
      `;
        });
    }

    els.timelineList.innerHTML = htmlContent;
}

const formatLocal = (date) => {
    const offset = date.getTimezoneOffset() * 60000;
    const localTime = new Date(date - offset);
    return localTime.toISOString().slice(0, 19); // Lấy "YYYY-MM-DDTHH:mm:ss"
};

// ============================================================
// 5. UI UPDATE FUNCTIONS
// ============================================================

function updateUI() {
    // Update selection count
    els.selectionCount.textContent = selectedTableIds.length;

    // Update selected tables text
    if (selectedTableIds.length === 0) {
        els.selectedTablesText.textContent = "Chưa chọn";
        els.btnSubmit.disabled = true;
        els.btnSubmit.querySelector(".btn-text").textContent = "Chọn bàn để đặt";
    } else {
        const selectedNames = selectedTableIds.map((id) => {
            const ban = serverTableData.find((t) => t.id === +id);
            return ban ? ban.ten : id;
        });
        els.selectedTablesText.textContent = selectedNames.join(", ");
        els.btnSubmit.disabled = false;
        els.btnSubmit.querySelector(".btn-text").textContent = `Xác nhận đặt ${selectedTableIds.length} bàn`;
    }

    // Check for time conflicts
    checkTimeConflicts();
}

function checkTimeConflicts() {
    let hasWarning = false;
    const currentTime = new Date();

    selectedTableIds.forEach((id) => {
        const ban = serverTableData.find((t) => t.id === +id);
        if (ban?.ds_khung_gio && ban.ds_khung_gio.length > 0) {
            const nextBooking = new Date(ban.ds_khung_gio[0].tg_bat_dau);
            const hoursDiff = (nextBooking - currentTime) / (1000 * 60 * 60);

            if (hoursDiff <= 1 && hoursDiff >= 0) {
                hasWarning = true;
            }
        }
    });

    if (hasWarning && selectedTableIds.length > 0) {
        els.btnSubmit.classList.add("warning");
        showError("⚠️ Một số bàn có lịch đặt trong vòng 1 giờ tới!");
    } else {
        els.btnSubmit.classList.remove("warning");
    }
}

function switchTab(tab) {
    if (tab === "details") {
        els.tabDetails.classList.add("active");
        els.tabBooking.classList.remove("active");
        els.contentDetails.classList.add("active");
        els.contentBooking.classList.remove("active");
    } else {
        els.tabDetails.classList.remove("active");
        els.tabBooking.classList.add("active");
        els.contentDetails.classList.remove("active");
        els.contentBooking.classList.add("active");
    }
}

function openDrawer() {
    els.drawer.classList.add("open");
    els.overlay.classList.add("show");
}

function closeDrawer() {
    els.drawer.classList.remove("open");
    els.overlay.classList.remove("show");
}

function showError(message) {
    els.errorMsg.textContent = message;
    els.errorMsg.classList.add("show");
}

function hideError() {
    els.errorMsg.classList.remove("show");
}

// ============================================================
// 6. FORM SUBMISSION
// ============================================================

async function handleSubmit() {
    if (selectedTableIds.length === 0) {
        showError("Vui lòng chọn ít nhất 1 bàn!");
        return;
    }

    // Validate form
    const tenKhach = els.tenKhach.value.trim();
    const sdt = els.sdt.value.trim();
    const soLuong = parseInt(els.soLuong.value);
    const tgDen = els.tgDen.value;

    if (!tenKhach) {
        showError("Vui lòng nhập tên khách hàng!");
        els.tenKhach.focus();
        switchTab("booking");
        return;
    }

    if (!sdt || sdt.length < 10 || sdt.length > 11) {
        showError("Số điện thoại phải có 10-11 số!");
        els.sdt.focus();
        switchTab("booking");
        return;
    }

    if (!soLuong || soLuong < 1) {
        showError("Vui lòng nhập số lượng khách!");
        els.soLuong.focus();
        switchTab("booking");
        return;
    }

    if (!tgDen) {
        showError("Vui lòng chọn thời gian đến!");
        els.tgDen.focus();
        switchTab("booking");
        return;
    }

    const selectedTime = new Date(tgDen);
    if (selectedTime < new Date()) {
        showError("Thời gian đến không được ở trong quá khứ!");
        els.tgDen.focus();
        switchTab("booking");
        return;
    }

    // Prepare data matching DatBanCreateSchema
    const requestData = {
        khach_hang: {
            ten: tenKhach,
            sdt: sdt,
            so_luong: soLuong,
        },
        ds_ban: selectedTableIds.map((id) => ({ id: +id })),
        tg_den: formatLocal(new Date(tgDen)),
    };

    console.log(requestData);

    // Confirm
    const tableNames = selectedTableIds.map((id) => {
        const ban = serverTableData.find((t) => t.id === +id);
        return ban ? ban.ten : id;
    }).join(", ");

    if (!confirm(`Xác nhận đặt bàn ${tableNames} cho ${tenKhach}?`)) {
        return;
    }

    // Submit
    els.btnSubmit.disabled = true;
    els.btnSubmit.querySelector(".btn-text").textContent = "Đang xử lý...";

    try {
        const response = await fetch("/api/v1/ban/dat-ban", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify(requestData),
        });

        const data = await response.json();

        if (response.ok) {
            alert("✅ Đặt bàn thành công!");
            resetForm();
            closeDrawer();
            // Reload to update table status
            window.location.reload();
        } else {
            showError(data.message || "Có lỗi xảy ra, vui lòng thử lại!");
        }
    } catch (error) {
        console.error("Error:", error);
        showError("Lỗi kết nối server!");
    } finally {
        els.btnSubmit.disabled = false;
        updateUI();
    }
}

function resetForm() {
    els.bookingForm.reset();
    selectedTableIds.forEach((id) => {
        const tableDiv = document.getElementById("table-" + id);
        if (tableDiv) {
            tableDiv.classList.remove("is-selected");
        }
    });
    selectedTableIds = [];
    updateUI();
    hideError();
}

// ============================================================
// 7. HELPER FUNCTIONS
// ============================================================

function formatDateTime(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleTimeString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

// ============================================================
// 8. RESERVATION LIST & CONFIRMATION MODAL
// ============================================================

// Additional DOM elements for reservations
const reservationEls = {
    reservationList: document.getElementById("reservationList"),
    btnRefresh: document.getElementById("btnRefreshReservations"),
    confirmModal: document.getElementById("confirmModal"),
    modalBody: document.getElementById("modalBody"),
    btnCloseModal: document.getElementById("btnCloseModal"),
    btnCancelConfirm: document.getElementById("btnCancelConfirm"),
    btnConfirmArrival: document.getElementById("btnConfirmArrival"),
};

let reservationData = [];
let selectedReservation = null;

// Event listeners for reservations
reservationEls.btnRefresh.addEventListener("click", fetchReservations);
reservationEls.btnCloseModal.addEventListener("click", closeConfirmModal);
reservationEls.btnCancelConfirm.addEventListener("click", closeConfirmModal);
reservationEls.btnConfirmArrival.addEventListener("click", handleConfirmArrival);

// Click on reservation list (Event Delegation)
reservationEls.reservationList.addEventListener("click", (e) => {
    const card = e.target.closest(".reservation-card");
    if (card) {
        const datBanId = card.dataset.datBanId;
        openConfirmModal(datBanId);
    }
});

// Fetch reservation list
async function fetchReservations() {
    reservationEls.reservationList.innerHTML = `<div class="loading-placeholder">Đang tải...</div>`;

    try {
        const response = await fetch("/api/v1/dat-ban/active", {
            credentials: "include",
        });

        if (response.ok) {
            reservationData = await response.json();
            renderReservationList();
        } else {
            reservationEls.reservationList.innerHTML = `<div class="empty-reservation">Lỗi khi tải dữ liệu!</div>`;
        }
    } catch (error) {
        console.error("Error fetching reservations:", error);
        reservationEls.reservationList.innerHTML = `<div class="empty-reservation">Không thể kết nối server!</div>`;
    }
}

// Render reservation list
function renderReservationList() {
    if (!reservationData || reservationData.length === 0) {
        reservationEls.reservationList.innerHTML = `
            <div class="empty-reservation">
                <p>✨ Không có đặt bàn nào đang chờ xác nhận.</p>
            </div>
        `;
        return;
    }

    let html = "";
    reservationData.forEach((datBan) => {
        const tgDen = new Date(datBan.khung_gio?.tg_bat_dau);
        const time = tgDen.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
        const date = tgDen.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" });

        const tableNames = datBan.ds_ban_dat?.map(b => b.ten).join(", ") || "N/A";
        const tableBadges = datBan.ds_ban_dat?.map(b => `<span class="table-badge">${b.ten}</span>`).join("") || "";

        html += `
            <div class="reservation-card" data-dat-ban-id="${datBan.id}">
                <div class="reservation-time">
                    <div class="time">${time}</div>
                    <div class="date">${date}</div>
                </div>
                <div class="reservation-info">
                    <div class="reservation-customer">👤 ${datBan.ten_khach}</div>
                    <div class="reservation-details">
                        <span>📱 ${datBan.sdt}</span>
                        <span>👥 ${datBan.so_luong} người</span>
                    </div>
                    <div class="reservation-tables">${tableBadges}</div>
                </div>
                <button class="reservation-action">Xem</button>
            </div>
        `;
    });

    reservationEls.reservationList.innerHTML = html;
}

// Open confirmation modal
function openConfirmModal(datBanId) {
    selectedReservation = reservationData.find(r => r.id === +datBanId);
    if (!selectedReservation) return;

    const tgDen = new Date(selectedReservation.khung_gio?.tg_bat_dau);
    const formattedTime = tgDen.toLocaleString("vi-VN");
    const tableNames = selectedReservation.ds_ban_dat?.map(b => b.ten).join(", ") || "N/A";

    reservationEls.modalBody.innerHTML = `
        <div class="modal-info-row">
            <span class="modal-info-icon">👤</span>
            <span class="modal-info-label">Khách hàng:</span>
            <span class="modal-info-value">${selectedReservation.ten_khach}</span>
        </div>
        <div class="modal-info-row">
            <span class="modal-info-icon">📱</span>
            <span class="modal-info-label">SĐT:</span>
            <span class="modal-info-value">${selectedReservation.sdt}</span>
        </div>
        <div class="modal-info-row">
            <span class="modal-info-icon">👥</span>
            <span class="modal-info-label">Số lượng:</span>
            <span class="modal-info-value">${selectedReservation.so_luong} người</span>
        </div>
        <div class="modal-info-row">
            <span class="modal-info-icon">🕐</span>
            <span class="modal-info-label">Giờ hẹn:</span>
            <span class="modal-info-value">${formattedTime}</span>
        </div>
        <div class="modal-info-row">
            <span class="modal-info-icon">🪑</span>
            <span class="modal-info-label">Bàn đặt:</span>
            <span class="modal-info-value">${tableNames}</span>
        </div>
    `;

    reservationEls.confirmModal.classList.add("show");
}

// Close confirmation modal
function closeConfirmModal() {
    reservationEls.confirmModal.classList.remove("show");
    selectedReservation = null;
}

// Handle arrival confirmation
async function handleConfirmArrival() {
    if (!selectedReservation) return;

    const datBanId = selectedReservation.id;

    reservationEls.btnConfirmArrival.disabled = true;
    reservationEls.btnConfirmArrival.innerHTML = "Đang xử lý...";

    try {
        const response = await fetch(`/api/v1/dat-ban/${datBanId}/xac-nhan`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "✅ Xác nhận khách đến thành công!");
            closeConfirmModal();
            // Reload page to reflect changes
            window.location.reload();
        } else {
            alert("❌ Lỗi: " + (data.message || "Không thể xác nhận"));
        }
    } catch (error) {
        console.error("Error confirming arrival:", error);
        alert("❌ Lỗi kết nối server!");
    } finally {
        reservationEls.btnConfirmArrival.disabled = false;
        reservationEls.btnConfirmArrival.innerHTML = `<span class="btn-icon">✅</span> Xác nhận khách đến`;
    }
}

// ============================================================
// 9. INITIALIZATION
// ============================================================

// Initialize UI
updateUI();

// Fetch reservations on page load
fetchReservations();
