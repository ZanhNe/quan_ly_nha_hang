// const pos = {
//     dsMon: [],      // Danh sách thực đơn (để tra cứu options)
//     monGhi: [],          // Danh sách món trong phiếu
//     ttPhieu: {},    // Info phiếu hiện tại
//     prefix: 'http://127.0.0.1:5000',
//     // State tạm của Modal
//     monMenuHienTai: null, // Món đang edit trong modal (clone từ dsMon)
//     soLuongMonMenuHienTai: 1,

//     init: function() {
//         // Load Data from HTML
//         try {
//             this.ttPhieu = JSON.parse(document.getElementById('ticket-data').textContent);
//             this.dsMon = JSON.parse(document.getElementById('menu-data').textContent).ds_mo_ta_mon;
//             this.monGhi = this.ttPhieu.ds_mon_ghi; // Load món cũ nếu có

//             // Nếu phiếu đã khóa (Sent), disable các nút tương tác (logic renderCart lo)
//             this.renderCart();
//         } catch (e) { console.error("Init Error:", e); }
//     },

//     // --- 1. MODAL LOGIC ---

//     openModal: function(menuId) {
//         if (this.ttPhieu.trang_thai !== 'DANGGHI') return alert("Phiếu đã khóa!");

//         // Tìm món trong thực đơn
//         const monMenu = this.dsMon.find(i => i.id === menuId);
//         if (!monMenu) return;

//         // Reset state modal
//         this.monMenuHienTai = monMenu;
//         this.soLuongMonMenuHienTai = 1;

//         // Render UI Modal
//         document.getElementById('modalImg').src = monMenu.hinh || 'https://via.placeholder.com/150';
//         document.getElementById('modalName').innerText = monMenu.ten;
//         document.getElementById('modalBasePrice').innerText = monMenu.gia.toLocaleString() + 'đ';
//         document.getElementById('modalNote').value = '';
//         document.getElementById('modalQty').innerText = '1';

//         // Render Option Groups
//         this.renderOptionGroups(monMenu.ds_nhom_tuy_chon || []);

//         // Show Modal
//         document.getElementById('itemModal').classList.add('show');
//         this.calculateModalTotal();
//     },

//     renderOptionGroups: function(groups) {
//         const container = document.getElementById('modalOptionsContainer');
//         container.innerHTML = '';

//         groups.forEach(group => {
//             const groupDiv = document.createElement('div');
//             groupDiv.className = 'opt-group';

//             // Header Group (vd: Topping - Chọn tối đa 2)
//             let hint = group.loai === 'radio' ? '(Chọn 1)' : '(Chọn nhiều)';
//             groupDiv.innerHTML = `<div class="opt-title">${group.ten} <small>${hint}</small></div>`;

//             const listDiv = document.createElement('div');
//             listDiv.className = 'opt-list';

//             group.ds_tuy_chon.forEach(opt => {
//                 const inputType = group.loai === 'radio' ? 'radio' : 'checkbox';
//                 const inputName = `opt_grp_${group.id}`; // Group radio bằng name

//                 listDiv.innerHTML += `
//                     <label class="opt-item">
//                         <input type="${inputType}" name="${inputName}" value="${opt.id}" 
//                                data-price="${opt.gia}" data-name="${opt.ten}"
//                                onchange="pos.calculateModalTotal()">
//                         <div>
//                             <div>${opt.ten}</div>
//                             ${opt.gia > 0 ? `<div class="opt-price">+${opt.gia.toLocaleString()}đ</div>` : ''}
//                         </div>
//                     </label>
//                 `;
//             });

//             groupDiv.appendChild(listDiv);
//             container.appendChild(groupDiv);
//         });
//     },

//     adjustModalQty: function(delta) {
//         let newQty = this.soLuongMonMenuHienTai + delta;
//         if (newQty < 1) newQty = 1;
//         this.soLuongMonMenuHienTai = newQty;
//         document.getElementById('modalQty').innerText = newQty;
//         this.calculateModalTotal();
//     },

//     // Tính tổng tiền realtime trong modal
//     calculateModalTotal: function() {
//         if (!this.monMenuHienTai) return;

//         let unitPrice = this.monMenuHienTai.gia; // Giá gốc

//         // Cộng giá Options đang check
//         const checkedInputs = document.querySelectorAll('#modalOptionsContainer input:checked');
//         checkedInputs.forEach(input => {
//             unitPrice += parseInt(input.getAttribute('data-price') || 0);
//         });

//         const total = unitPrice * this.soLuongMonMenuHienTai;
//         document.getElementById('modalTotalPrice').innerText = total.toLocaleString() + 'đ';
//     },

//     closeModal: function() {
//         document.getElementById('itemModal').classList.remove('show');
//         this.monMenuHienTai = null;
//     },

//     // --- 2. ADD TO CART LOGIC ---

//     addItemFromModal: function() {
//         if (!this.monMenuHienTai) return;

//         // 1. Thu thập Options đã chọn
//         const selectedOptions = [];
//         const checkedInputs = document.querySelectorAll('#modalOptionsContainer input:checked');
//         checkedInputs.forEach(input => {
//             selectedOptions.push({
//                 tuy_chon_id: parseInt(input.value),
//                 ten: input.getAttribute('data-name'),
//                 gia: parseInt(input.getAttribute('data-price'))
//             });
//         });

//         // 2. Lấy Note
//         const ghi_chu = document.getElementById('modalNote').value.trim();

//         // 3. Tạo Object Item mới
//         const newItem = {
//             // Tạo ID tạm thời (Date.now) để phân biệt các món giống nhau nhưng khác topping
//             temp_id: Date.now(), 
//             mo_ta_mon_id: this.monMenuHienTai.id,
//             phieu_mon_id: this.ttPhieu.id,
//             ten: this.monMenuHienTai.ten,
//             gia: this.monMenuHienTai.gia,
//             so_luong: this.soLuongMonMenuHienTai,
//             ghi_chu: ghi_chu,
//             ds_tuy_chon: selectedOptions
//         };

//         // 3. Logic Gộp Món (Generate Signature)
//         const signature = this.generateSignature(newItem);

//         // Tìm xem trong giỏ đã có món nào giống hệt chưa
//         const existingItem = this.monGhi.find(item => this.generateSignature(item) === signature);

//         if (existingItem) {
//             existingItem.so_luong += newItem.so_luong; // Cộng dồn số lượng
//         } else {
//             this.monGhi.push(newItem); // Thêm mới
//         }

//         this.renderCart();
//         this.closeModal();
//     },

//     // --- 3. RENDER CART LOGIC ---

//     renderCart: function() {
//         const container = document.getElementById('monGhiContainer');
//         const totalEl = document.getElementById('totalAmount');
//         container.innerHTML = '';

//         let grandTotal = 0;

//         if (this.monGhi.length === 0) {
//             container.innerHTML = '<div style="text-align:center; padding:20px; color:#A0AEC0;">Chưa có món nào</div>';
//             totalEl.innerText = '0đ';
//             return;
//         }

//         this.monGhi.forEach((item, index) => {
//             // Tính giá item: (Base + Option) * Qty
//             let itemUnitPrice = item?.mo_ta_mon ? item.mo_ta_mon.gia : item.gia;
//             let optionsHtml = '';

//             if (item.ds_tuy_chon && item.ds_tuy_chon.length > 0) {
//                 item.ds_tuy_chon.forEach(opt => {
//                     itemUnitPrice += opt.gia;
//                     optionsHtml += `<span style="display:inline-block; background:#EDF2F7; padding:2px 6px; border-radius:4px; margin-right:4px;">+ ${opt.ten}</span>`;
//                 });
//             }

//             const itemTotal = itemUnitPrice * item.so_luong;
//             grandTotal += itemTotal;

//             // Nút xóa (chỉ hiện khi DANGGHI)
//             const removeBtn = this.ttPhieu.trang_thai === 'DANGGHI' ? 
//                 `<button onclick="pos.removeItem(${index})" style="color:#E53E3E; background:none; border:none; cursor:pointer; font-size:1.2em;">&times;</button>` : '';

//             // Note HTML
//             const ghi_chuHtml = item.ghi_chu ? `<div class="item-ghi_chu">📝 ${item.ghi_chu}</div>` : '';

//             const html = `
//                 <div class="monGhi-item">
//                     <div style="font-weight:700; color:var(--primary-color); width:30px; text-align:center;">${item.so_luong}x</div>
//                     <div class="monGhi-item-details">
//                         <div class="item-name">${item?.mo_ta_mon ? item.mo_ta_mon.ten : item.ten}</div>
//                         <div class="item-options">${optionsHtml}</div>
//                         ${ghi_chuHtml}
//                     </div>
//                     <div style="text-align:right;">
//                         <div class="item-price">${itemTotal.toLocaleString()}đ</div>
//                         ${removeBtn}
//                     </div>
//                 </div>
//             `;
//             container.innerHTML += html;
//         });

//         totalEl.innerText = grandTotal.toLocaleString() + 'đ';
//     },

//     // Tạo chữ ký duy nhất cho món: ID + Note + SortedOptionIDs
//     generateSignature: function(item) {
//         const id = item.thuc_don_id;
//         const ghi_chu = (item.ghi_chu || '').toLowerCase().trim();

//         // Lấy list ID topping và sort
//         let optIds = '';
//         if (item.selected_options && item.selected_options.length > 0) {
//             optIds = item.selected_options.map(o => o.id).sort((a,b) => a-b).join(',');
//         }

//         return `${id}|${ghi_chu}|${optIds}`;
//     },

//     removeItem: function(index) {
//         if (!confirm("Xóa món này khỏi phiếu?")) return;
//         this.monGhi.splice(index, 1);
//         this.renderCart();
//     },


//     submitTicket: async function() {
//         if (this.monGhi.length === 0) return alert("Chưa chọn món nào!");
//         if (!confirm("Xác nhận gửi xuống bếp?")) return;


//         const payload = {
//             ds_mon_ghi: this.monGhi
//         };

//         try {
//             const response = await fetch(`${this.prefix}/api/v1/phieu-mon/${this.ttPhieu.id}/mon-ghi`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-type': 'application/json'
//                 },
//                 credentials: 'include',
//                 body: JSON.stringify(payload)
//             });

//             if (!response.ok) {
//             const errorData = await response.json();
//             const errMsg = errorData.message;
//             throw new Error(errMsg);
//         }

//             const data = await response.json();

//             Swal.fire({
//                 icon: 'success',
//                 title: 'Thành công!',
//                 text: 'Gửi phiếu cho bếp thành công!',
//                 timer: 2000,              // Tự tắt sau 2 giây
//                 showConfirmButton: false  // Không cần nút bấm
//             });

//             console.log(data);

//         } catch (error) {
//             Swal.fire({
//                 icon: 'error',               
//                 title: 'Úi chà!',            
//                 text: error.message,         
//                 confirmButtonText: 'Đóng'    
//             });
//         }

//     }
// };

// document.addEventListener('DOMContentLoaded', () => pos.init());





const pos = {
    // Dữ liệu chính
    groupFoods: [],
    ticketInfo: {}, // Thông tin phiếu (lấy ID phiếu, ID bàn...)
    cart: [],       // Món Ghi (Local state)

    // State của Modal
    currentDish: null, // Món đang chọn (Object MoTaMon)
    modalQty: 1,

    init: function () {
        const ticketEl = document.getElementById('ticket-data');
        const thucDonEl = document.getElementById('thucdon-data');
        if (ticketEl) {
            try {
                this.groupFoods = JSON.parse(thucDonEl.textContent).ds_nhom_mon;
                this.ticketInfo = JSON.parse(ticketEl.textContent);

                // Load các món đã ghi trước đó (Server trả về ds_mon_ghi)
                // Lưu ý: Backend cần trả về ds_mon_ghi đúng cấu trúc ta cần hoặc ta phải map lại
                this.cart = this.ticketInfo.ds_mon_ghi || [];

                this.renderCart();
            } catch (e) {
                console.error("Init Error:", e);
            }
        }
    },

    // ============================================================
    // 1. MENU FILTER (Tab Category)
    // ============================================================
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

    // ============================================================
    // 2. MODAL LOGIC
    // ============================================================
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

    // ============================================================
    // 3. CART LOGIC & PAYLOAD CONSTRUCTION
    // ============================================================

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

    // ============================================================
    // 4. RENDER CART UI
    // ============================================================
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

    // ============================================================
    // 4.1 CANCEL REQUEST MODAL
    // ============================================================
    openCancelModal: function(monGhiId, dishName, currentStatus) {
        document.getElementById('cancelMonGhiId').value = monGhiId;
        document.getElementById('cancelModalDishName').innerText = dishName;
        document.getElementById('cancelReason').value = '';
        document.getElementById('cancelRequestModal').classList.add('show');
    },

    closeCancelModal: function() {
        document.getElementById('cancelRequestModal').classList.remove('show');
    },

    submitCancelRequest: async function() {
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

    // ============================================================
    // 5. SUBMIT TO BACKEND
    // ============================================================
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