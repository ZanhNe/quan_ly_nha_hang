const pos = {
    // Data chính
    groupFoods: [],
    ticketInfo: {}, // Info phiếu (bàn nào, ID phiếu là gì...)
    cart: [],       // Danh sách món đang chọn (Local state)

    // State của Modal chọn món
    currentDish: null, // Món đang mở modal
    modalQty: 1,

    init: function () {
        const ticketEl = document.getElementById('ticket-data');
        const thucDonEl = document.getElementById('thucdon-data');
        if (ticketEl) {
            try {
                this.groupFoods = JSON.parse(thucDonEl.textContent).ds_nhom_mon;
                this.ticketInfo = JSON.parse(ticketEl.textContent);

                // Load lại các món đã ghi trước đó (nếu có)
                this.cart = this.ticketInfo.ds_mon_ghi || [];

                this.renderCart();
            } catch (e) {
                console.error("Lỗi khi khởi tạo POS:", e);
            }
        }
    },

    // --- 1. Lọc thực đơn theo nhóm (Tab) ---
    filterCategory: function (categoryName) {
        const sections = document.querySelectorAll('.menu-section');
        const tabs = document.querySelectorAll('.cat-tab');

        // Update UI Tabs
        tabs.forEach(tab => {
            if (tab.innerText.trim() === categoryName || (categoryName === 'all' && tab.innerText === 'Tất cả')) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Filter Items
        sections.forEach(sec => {
            if (categoryName === 'all' || sec.dataset.category === categoryName) {
                sec.style.display = 'block';
            } else {
                sec.style.display = 'none';
            }
        });
    },

    // --- 2. Xử lý Modal chọn món & Topping ---
    openModal: function (dishId) {
        // dish ở đây là object MoTaMon
        if (this.ticketInfo.trang_thai !== 'DANGGHI') {
            alert("Phiếu này đã khóa, không thể thêm món!");
            return;
        }

        console.log(this.groupFoods)

        let dish = undefined;

        this.groupFoods.forEach((group) => {
            if (dish !== undefined) return;
            dish = group.ds_mo_ta_mon.find((mon) => mon.id === +dishId)
            console.log(dish);
        })



        if (!dish) {
            console.error("Không tìm thấy món có ID:", dishId);
            return;
        }

        this.currentDish = dish;
        this.modalQty = 1;

        // Reset UI Modal
        document.getElementById('modalImg').src = dish.hinh || 'https://via.placeholder.com/150';
        document.getElementById('modalName').innerText = dish.ten;
        document.getElementById('modalBasePrice').innerText = dish.gia.toLocaleString() + 'đ';
        document.getElementById('modalNote').value = '';
        document.getElementById('modalQty').innerText = '1';

        // Render Option Groups (Nhóm Tùy Chọn)
        this.renderOptionGroups(dish.ds_nhom_tuy_chon || []);

        document.getElementById('itemModal').classList.add('show');
        this.calculateModalTotal();
    },

    renderOptionGroups: function (groups) {
        const container = document.getElementById('modalOptionsContainer');
        container.innerHTML = '';

        groups.forEach(group => {
            // group là NhomTuyChonOutSchema
            const wrapper = document.createElement('div');
            wrapper.className = 'opt-group';

            // Xác định loại input (radio/checkbox) dựa trên field 'loai' của schema
            // Giả sử loai: 'Single' -> radio, 'Multiple' -> checkbox
            const inputType = (group.loai && group.loai.toLowerCase().includes('multi')) ? 'checkbox' : 'radio';
            const hint = inputType === 'radio' ? '(Chọn 1)' : '(Chọn nhiều)';

            wrapper.innerHTML = `<div class="opt-title">${group.ten} <small>${hint}</small></div>`;

            const list = document.createElement('div');
            list.className = 'opt-list';

            if (group.ds_tuy_chon) {
                group.ds_tuy_chon.forEach(opt => {
                    // opt là TuyChonMonOutSchema
                    const nameAttr = `grp_${group.ten}`; // Gom nhóm input bằng tên nhóm tùy chọn

                    list.innerHTML += `
                        <label class="opt-label">
                            <input type="${inputType}" name="${nameAttr}" value="${opt.id}"
                                   data-name="${opt.ten}" data-price="${opt.gia}"
                                   onchange="pos.calculateModalTotal()">
                            <div>
                                <div>${opt.ten}</div>
                                ${opt.gia > 0 ? `<div class="opt-price-add">+${opt.gia.toLocaleString()}</div>` : ''}
                            </div>
                        </label>
                    `;
                });
            }
            wrapper.appendChild(list);
            container.appendChild(wrapper);
        });
    },

    adjustModalQty: function (delta) {
        let newQty = this.modalQty + delta;
        if (newQty < 1) newQty = 1;
        this.modalQty = newQty;
        document.getElementById('modalQty').innerText = newQty;
        this.calculateModalTotal();
    },

    calculateModalTotal: function () {
        if (!this.currentDish) return;

        let unitPrice = this.currentDish.gia;

        // Cộng giá Options được chọn
        const checkedInputs = document.querySelectorAll('#modalOptionsContainer input:checked');
        checkedInputs.forEach(input => {
            unitPrice += parseInt(input.getAttribute('data-price') || 0);
        });

        const total = unitPrice * this.modalQty;
        document.getElementById('modalTotalPrice').innerText = total.toLocaleString() + 'đ';
    },

    closeModal: function () {
        document.getElementById('itemModal').classList.remove('show');
        this.currentDish = null;
    },

    // --- 3. Quản lý giỏ hàng & chuẩn bị Data gửi lên BE ---

    addItemFromModal: function () {
        if (!this.currentDish) return;

        // A. Thu thập Option (ds_tuy_chon)
        // Cấu trúc yêu cầu: { tuy_chon_id, gia, so_luong }
        const ds_tuy_chon = [];
        const checkedInputs = document.querySelectorAll('#modalOptionsContainer input:checked');

        checkedInputs.forEach(input => {
            ds_tuy_chon.push({
                tuy_chon_id: parseInt(input.value),
                ten: input.getAttribute('data-name'), // Lưu thêm tên để hiển thị UI
                gia: parseInt(input.getAttribute('data-price') || 0),
                so_luong: 1 // Mặc định option số lượng 1 theo yêu cầu
            });
        });

        const note = document.getElementById('modalNote').value.trim();

        // B. Tạo Object MonGhi (Khớp với Payload BE yêu cầu)
        const newItem = {
            temp_id: Date.now(), // ID tạm để FE phân biệt
            mo_ta_mon_id: this.currentDish.id, // ID gốc từ MoTaMon
            phieu_mon_id: this.ticketInfo.id,
            ten: this.currentDish.ten,
            gia: this.currentDish.gia,
            so_luong: this.modalQty,
            ghi_chu: note,
            ds_tuy_chon: ds_tuy_chon
        };

        // C. Logic Gộp món (Deep Compare)
        // Nếu trùng MoTaMon + Note + Options -> Cộng dồn số lượng
        const signature = this.generateSignature(newItem);
        const existingItem = this.cart.find(item => this.generateSignature(item) === signature);

        if (existingItem) {
            existingItem.so_luong += newItem.so_luong;
        } else {
            this.cart.push(newItem);
        }

        this.renderCart();
        this.closeModal();
    },

    // Tạo chữ ký để so sánh trùng món
    generateSignature: function (item) {
        const id = item.mo_ta_mon_id;
        const note = (item.ghi_chu || '').toLowerCase().trim();

        // Lấy list ID option, sort để đảm bảo thứ tự
        let optIds = '';
        if (item.ds_tuy_chon && item.ds_tuy_chon.length > 0) {
            optIds = item.ds_tuy_chon
                .map(o => o.tuy_chon_id)
                .sort((a, b) => a - b)
                .join(',');
        }

        return `${id}|${note}|${optIds}`;
    },

    removeItem: function (index) {
        if (confirm("Xóa món này?")) {
            this.cart.splice(index, 1);
            this.renderCart();
        }
    },

    // --- 4. Render giao diện giỏ hàng ---
    renderCart: function () {
        const container = document.getElementById('cartContainer');
        const totalEl = document.getElementById('totalAmount');
        const countEl = document.getElementById('cartCount');

        container.innerHTML = '';
        let grandTotal = 0;
        let totalQty = 0;

        if (this.cart.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding:30px; color:#A0AEC0;">Chưa có món nào</div>';
            totalEl.innerText = '0đ';
            countEl.innerText = '0';
            return;
        }

        const isSentToKitchen = this.ticketInfo.trang_thai === 'DAGUI';

        this.cart.forEach((item, index) => {
            let unitPrice = item?.mo_ta_mon ? item.mo_ta_mon.gia : item.gia;
            let optHtml = '';

            if (item.ds_tuy_chon) {
                item.ds_tuy_chon.forEach(opt => {
                    unitPrice += opt.gia;
                    optHtml += `<span style="margin-right:5px; background:#EDF2F7; padding:2px 6px; border-radius:4px;">+ ${opt.ten}</span>`;
                });
            }

            const lineTotal = unitPrice * item.so_luong;
            grandTotal += lineTotal;
            totalQty += item.so_luong;

            const noteHtml = item.ghi_chu ? `<div class="cart-item-note">📝 ${item.ghi_chu}</div>` : '';

            // Status Badge cho món đã gửi bếp
            let statusBadge = '';
            let actionBtn = '';

            if (isSentToKitchen && item.trang_thai) {
                const statusMap = {
                    'CHUANAU': { text: '⏳ Chờ nấu', color: '#F6AD55', bg: '#FFFAF0' },
                    'HOANTHANH': { text: '✅ Đã xong', color: '#48BB78', bg: '#F0FFF4' },
                    'HUY': { text: '❌ Đã hủy', color: '#E53E3E', bg: '#FFF5F5' },
                    'HAOTON': { text: '⚠️ Hao tổn', color: '#DD6B20', bg: '#FFFAF0' },
                    'TAMNGUNG': { text: '🔄 Chờ duyệt', color: '#805AD5', bg: '#FAF5FF' }
                };
                const status = statusMap[item.trang_thai] || { text: item.trang_thai, color: '#718096', bg: '#F7FAFC' };
                statusBadge = `<span style="font-size: 0.75em; padding: 2px 8px; border-radius: 4px; background: ${status.bg}; color: ${status.color};">${status.text}</span>`;

                // Chỉ cho phép yêu cầu hủy nếu món đang CHUANAU hoặc HOANTHANH
                if (item.trang_thai === 'CHUANAU' || item.trang_thai === 'HOANTHANH') {
                    actionBtn = `<button onclick="pos.openCancelModal(${item.id}, '${(item?.mo_ta_mon ? item.mo_ta_mon.ten : item.ten).replace(/'/g, "\\'")}', '${item.trang_thai}')" 
                        style="font-size: 0.75em; padding: 4px 8px; border: 1px solid #E53E3E; border-radius: 4px; background: white; color: #E53E3E; cursor: pointer; margin-top: 5px;">
                        🚫 Yêu cầu hủy
                    </button>`;
                }
            }

            // Nút xóa (chỉ hiện khi Draft)
            const removeBtn = (this.ticketInfo.trang_thai === 'DANGGHI' || !this.ticketInfo.trang_thai) ?
                `<button onclick="pos.removeItem(${index})" class="cart-item-remove">&times;</button>` : '';

            const html = `
                <div class="cart-item" style="${isSentToKitchen ? 'border-left: 3px solid #4299E1;' : ''}">
                    <div class="cart-item-qty">${item.so_luong}x</div>
                    <div class="cart-item-info">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div class="cart-item-name">${item?.mo_ta_mon ? item.mo_ta_mon.ten : item.ten}</div>
                            ${statusBadge}
                        </div>
                        <div class="cart-item-opts">${optHtml}</div>
                        ${noteHtml}
                        ${actionBtn}
                    </div>
                    <div class="cart-item-price">${lineTotal.toLocaleString()}</div>
                    ${removeBtn}
                </div>
            `;
            container.innerHTML += html;
        });

        totalEl.innerText = grandTotal.toLocaleString() + 'đ';
        countEl.innerText = totalQty;
    },

    // --- 4.1 Modal yêu cầu hủy món (cho Quản lý duyệt) ---
    openCancelModal: function (monGhiId, dishName, currentStatus) {
        document.getElementById('cancelMonGhiId').value = monGhiId;
        document.getElementById('cancelModalDishName').innerText = dishName;
        document.getElementById('cancelReason').value = '';
        document.getElementById('cancelRequestModal').classList.add('show');
    },

    closeCancelModal: function () {
        document.getElementById('cancelRequestModal').classList.remove('show');
    },

    submitCancelRequest: async function () {
        const monGhiId = document.getElementById('cancelMonGhiId').value;
        const lyDo = document.getElementById('cancelReason').value.trim();

        if (!lyDo) {
            alert('Vui lòng nhập lý do hủy món!');
            return;
        }

        if (!confirm('Xác nhận gửi yêu cầu hủy món đến Quản lý?')) return;

        try {
            const response = await fetch(`http://127.0.0.1:5000/api/v1/mon-ghi/${monGhiId}/yeu-cau`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ ly_do: lyDo })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.message || 'Có lỗi xảy ra');
            }

            const data = await response.json();

            // Cập nhật trạng thái món trong cart local
            this.cart = this.cart.map(item => {
                if (item.id === parseInt(monGhiId)) {
                    return { ...item, trang_thai: 'TAMNGUNG' };
                }
                return item;
            });

            this.renderCart();
            this.closeCancelModal();

            // Thông báo thành công
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: 'Đã gửi yêu cầu!',
                    text: 'Yêu cầu hủy món đã được gửi đến Quản lý.',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                alert('Đã gửi yêu cầu hủy món thành công!');
            }

            // Emit socket event nếu có (để notify Manager)
            if (typeof socket !== 'undefined') {
                socket.emit('new_cancel_request', data);
            }

        } catch (error) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi!',
                    text: error.message,
                    confirmButtonText: 'Đóng'
                });
            } else {
                alert('Lỗi: ' + error.message);
            }
        }
    },

    // --- 5. Gửi phiếu xuống bếp ---
    submitTicket: function () {
        if (this.cart.length === 0) return alert("Vui lòng chọn món!");
        if (!confirm("Xác nhận gửi thực đơn này xuống bếp?")) return;

        // Chuẩn bị Payload y hệt yêu cầu
        // Lưu ý: cart hiện tại đã có cấu trúc giống MonGhi, nhưng ta cần bọc vào object cha
        const payload = {
            ds_mon_ghi: this.cart
        };

        // Gửi Fetch API
        // Giả sử URL: /api/tickets/<phieu_id>/submit
        fetch(`http://127.0.0.1:5000/api/v1/phieu-mon/${this.ticketInfo.id}/mon-ghi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => {
                if (res.ok) {
                    alert("Đã gửi bếp thành công!");

                } else {
                    return res.json().then(err => { throw new Error(err.message || 'Lỗi server'); });
                }
            })
            .catch(err => {
                alert("Lỗi: " + err.message);
            });
    }
};

// Init logic khi trang load
document.addEventListener('DOMContentLoaded', () => pos.init());