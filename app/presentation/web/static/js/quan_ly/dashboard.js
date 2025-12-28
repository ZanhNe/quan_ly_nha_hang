// --- Dashboard Quản lý ---
// Xử lý các yêu cầu hủy món, phê duyệt, từ chối...

// --- Quản lý State ---
const state = {
    pendingRequests: [],
    currentAction: null, // { type: 'approve' | 'reject', ycId: number }
};

// --- Các phần tử giao diện (DOM) ---
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Modal
    modal: document.getElementById('confirmModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalMessage: document.getElementById('modalMessage'),
    modalDetails: document.getElementById('modalDetails'),
    modalConfirm: document.getElementById('modalConfirm'),
    modalCancel: document.getElementById('modalCancel'),
    modalClose: document.getElementById('modalClose'),

    // Counters
    pendingCount: document.getElementById('pending-count'),
    tabPendingCount: document.getElementById('tab-pending-count'),
};

// --- Khởi tạo trang ---
document.addEventListener('DOMContentLoaded', () => {
    initializeData();
    setupTabNavigation();
    setupRequestActions();
    setupModal();
});

// Đổ data yêu cầu từ JSON vào state
function initializeData() {
    const dataElement = document.getElementById('yeu-cau-data');
    if (dataElement) {
        try {
            state.pendingRequests = JSON.parse(dataElement.textContent);
            console.log('Loaded requests:', state.pendingRequests);
        } catch (e) {
            console.error('Error parsing request data:', e);
            state.pendingRequests = [];
        }
    }
}

// --- Chuyển đổi giữa các Tab ---
function setupTabNavigation() {
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.disabled) return;

            const targetTab = btn.dataset.tab;

            // Update active tab button
            elements.tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update active tab content
            elements.tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `tab-${targetTab}`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// ========================================
// XỬ LÝ CÁC HÀNH ĐỘNG YÊU CẦU
// ========================================
function setupRequestActions() {
    document.querySelectorAll('.btn-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = btn.dataset.action;
            const ycId = btn.dataset.ycId;

            if (action === 'approve') {
                showConfirmModal('approve', ycId);
            } else if (action === 'reject') {
                showConfirmModal('reject', ycId);
            }
        });
    });
}

// ========================================
// XỬ LÝ HỘP THOẠI XÁC NHẬN (MODAL)
// ========================================
function setupModal() {
    // Xử lý đóng modal
    elements.modalCancel?.addEventListener('click', hideModal);
    elements.modalClose?.addEventListener('click', hideModal);
    elements.modal?.addEventListener('click', (e) => {
        if (e.target === elements.modal) hideModal();
    });

    // Xử lý xác nhận hành động
    elements.modalConfirm?.addEventListener('click', handleConfirmAction);

    // Đóng modal khi nhấn phím ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.modal?.classList.contains('show')) {
            hideModal();
        }
    });
}

// Hiển thị hộp thoại xác nhận
function showConfirmModal(action, ycId) {
    state.currentAction = { type: action, ycId: parseInt(ycId) };

    const request = state.pendingRequests.find(r => r.id === state.currentAction.ycId);

    if (action === 'approve') {
        elements.modalTitle.textContent = '✅ Xác nhận Chấp thuận';
        elements.modalMessage.textContent = 'Bạn có chắc chắn muốn CHẤP THUẬN yêu cầu này?';
        elements.modalConfirm.className = 'btn-modal btn-confirm approve';
        elements.modalConfirm.textContent = 'Chấp thuận';
    } else {
        elements.modalTitle.textContent = '❌ Xác nhận Từ chối';
        elements.modalMessage.textContent = 'Bạn có chắc chắn muốn TỪ CHỐI yêu cầu này?';
        elements.modalConfirm.className = 'btn-modal btn-confirm reject';
        elements.modalConfirm.textContent = 'Từ chối';
    }

    // Hiển thị chi tiết yêu cầu
    if (request) {
        elements.modalDetails.innerHTML = `
            <strong>Yêu cầu #${request.id}</strong><br>
            Lý do: ${request.ly_do || 'Không có lý do'}
        `;
    }

    elements.modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // Ngăn cuộn trang khi modal mở
}

// Ẩn hộp thoại xác nhận
function hideModal() {
    elements.modal?.classList.remove('show');
    document.body.style.overflow = ''; // Cho phép cuộn trang trở lại
    state.currentAction = null;
}

// ========================================
// XỬ LÝ GỌI API
// ========================================
async function handleConfirmAction() {
    if (!state.currentAction) return;

    const { type, ycId } = state.currentAction;
    const card = document.querySelector(`.request-card[data-yc-id="${ycId}"]`);
    const approveBtn = card?.querySelector('.btn-approve');
    const rejectBtn = card?.querySelector('.btn-reject');

    // Hiển thị trạng thái đang tải và ẩn modal
    hideModal();
    if (approveBtn) approveBtn.classList.add('loading');
    if (rejectBtn) rejectBtn.classList.add('loading');
    if (card) card.classList.add('processing');

    try {
        const endpoint = type === 'approve'
            ? `/api/v1/yeu-cau/${ycId}/chap-thuan`
            : `/api/v1/yeu-cau/${ycId}/tu-choi`;

        const response = await fetch(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (response.ok) {
            handleActionSuccess(type, ycId, card);
        } else {
            handleActionError(data.message || 'Có lỗi xảy ra', card, approveBtn, rejectBtn);
        }
    } catch (error) {
        console.error('Lỗi khi xử lý yêu cầu:', error);
        handleActionError('Lỗi kết nối máy chủ', card, approveBtn, rejectBtn);
    }
}

// Xử lý khi hành động thành công
function handleActionSuccess(type, ycId, card) {
    // Cập nhật giao diện thẻ yêu cầu
    if (card) {
        card.classList.remove('processing');
        card.classList.add(type === 'approve' ? 'approved' : 'rejected');

        // Cập nhật huy hiệu trạng thái
        const statusBadge = card.querySelector('.request-status');
        if (statusBadge) {
            statusBadge.className = `request-status ${type === 'approve' ? 'status-approved' : 'status-rejected'}`;
            statusBadge.innerHTML = `
                <span class="status-dot"></span>
                ${type === 'approve' ? 'Đã chấp thuận' : 'Đã từ chối'}
            `;
        }

        // Ẩn các nút hành động
        const actionsContainer = card.querySelector('.request-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = `
                <div style="text-align: center; width: 100%; color: ${type === 'approve' ? '#38A169' : '#E53E3E'}; font-weight: 600;">
                    ${type === 'approve' ? '✅ Đã chấp thuận' : '❌ Đã từ chối'}
                </div>
            `;
        }
    }

    // Cập nhật bộ đếm yêu cầu đang chờ
    updatePendingCount(-1);

    // Hiển thị thông báo thành công
    showNotification(
        type === 'approve' ? 'Đã chấp thuận yêu cầu!' : 'Đã từ chối yêu cầu!',
        type === 'approve' ? 'success' : 'info'
    );

    // Xóa yêu cầu khỏi state
    state.pendingRequests = state.pendingRequests.filter(r => r.id !== ycId);

    // Làm mờ và xóa thẻ yêu cầu sau một khoảng thời gian
    setTimeout(() => {
        if (card) {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';

            setTimeout(() => {
                card.remove();
                checkEmptyState(); // Kiểm tra trạng thái rỗng sau khi xóa thẻ
            }, 500);
        }
    }, 2000);
}

// Xử lý khi hành động thất bại
function handleActionError(message, card, approveBtn, rejectBtn) {
    // Xóa trạng thái đang tải
    if (approveBtn) approveBtn.classList.remove('loading');
    if (rejectBtn) rejectBtn.classList.remove('loading');
    if (card) card.classList.remove('processing');

    // Hiển thị thông báo lỗi
    showNotification(message, 'error');
}

// ========================================
// CÁC HÀM TIỆN ÍCH
// ========================================
// Cập nhật số lượng yêu cầu đang chờ
function updatePendingCount(delta) {
    const currentCount = parseInt(elements.pendingCount?.textContent || '0');
    const newCount = Math.max(0, currentCount + delta);

    if (elements.pendingCount) {
        elements.pendingCount.textContent = newCount;
    }
    if (elements.tabPendingCount) {
        elements.tabPendingCount.textContent = newCount;
    }
}

// Kiểm tra và hiển thị trạng thái rỗng nếu không còn yêu cầu nào
function checkEmptyState() {
    const requestGrid = document.querySelector('.request-grid');
    const remainingCards = document.querySelectorAll('.request-card');

    if (remainingCards.length === 0 && requestGrid) {
        const tabContent = document.getElementById('tab-pending');
        if (tabContent) {
            tabContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🎉</div>
                    <h3 class="empty-title">Không có yêu cầu nào đang chờ</h3>
                    <p class="empty-text">Tất cả yêu cầu đã được xử lý. Bạn có thể nghỉ ngơi một chút!</p>
                </div>
            `;
        }
    }
}

// Hiển thị thông báo (sử dụng SweetAlert2 nếu có)
function showNotification(message, type = 'info') {
    // Sử dụng SweetAlert2 nếu thư viện có sẵn
    if (typeof Swal !== 'undefined') {
        const icons = {
            success: 'success',
            error: 'error',
            info: 'info',
            warning: 'warning'
        };

        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: icons[type] || 'info',
            title: message,
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
        });
    } else {
        // Fallback to console
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// ========================================
// SOCKET.IO INTEGRATION (Optional)
// ========================================
function setupSocketIO() {
    if (typeof io === 'undefined') return;

    const socket = io('http://localhost:5000', { transports: ['websocket'] });

    socket.on('connect', () => {
        console.log('Socket connected for Manager dashboard');
        socket.emit('join_room', { room: 'manager_room' });
    });

    // Listen for new requests
    socket.on('new_request', (data) => {
        console.log('New request received:', data);
        // Optionally refresh the page or add the new request dynamically
        showNotification('Có yêu cầu mới cần xử lý!', 'info');
        updatePendingCount(1);
    });
}

// Initialize socket if needed
// setupSocketIO();

