/**
 * Quản Lý Dashboard - JavaScript Module
 * Xử lý logic tương tác cho trang dashboard của Quản lý
 */

// ========================================
// STATE MANAGEMENT
// ========================================
const state = {
    pendingRequests: [],
    currentAction: null, // { type: 'approve' | 'reject', ycId: number }
};

// ========================================
// DOM ELEMENTS
// ========================================
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

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initializeData();
    setupTabNavigation();
    setupRequestActions();
    setupModal();
});

/**
 * Load dữ liệu yêu cầu từ JSON được inject vào page
 */
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

// ========================================
// TAB NAVIGATION
// ========================================
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
// REQUEST ACTIONS
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
// MODAL HANDLING
// ========================================
function setupModal() {
    // Close modal handlers
    elements.modalCancel?.addEventListener('click', hideModal);
    elements.modalClose?.addEventListener('click', hideModal);
    elements.modal?.addEventListener('click', (e) => {
        if (e.target === elements.modal) hideModal();
    });
    
    // Confirm action handler
    elements.modalConfirm?.addEventListener('click', handleConfirmAction);
    
    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.modal?.classList.contains('show')) {
            hideModal();
        }
    });
}

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
    
    // Show request details
    if (request) {
        elements.modalDetails.innerHTML = `
            <strong>Yêu cầu #${request.id}</strong><br>
            Lý do: ${request.ly_do || 'Không có lý do'}
        `;
    }
    
    elements.modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function hideModal() {
    elements.modal?.classList.remove('show');
    document.body.style.overflow = '';
    state.currentAction = null;
}

// ========================================
// API HANDLERS
// ========================================
async function handleConfirmAction() {
    if (!state.currentAction) return;
    
    const { type, ycId } = state.currentAction;
    const card = document.querySelector(`.request-card[data-yc-id="${ycId}"]`);
    const approveBtn = card?.querySelector('.btn-approve');
    const rejectBtn = card?.querySelector('.btn-reject');
    
    // Show loading state
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
        console.error('Error processing request:', error);
        handleActionError('Lỗi kết nối server', card, approveBtn, rejectBtn);
    }
}

function handleActionSuccess(type, ycId, card) {
    // Update card UI
    if (card) {
        card.classList.remove('processing');
        card.classList.add(type === 'approve' ? 'approved' : 'rejected');
        
        // Update status badge
        const statusBadge = card.querySelector('.request-status');
        if (statusBadge) {
            statusBadge.className = `request-status ${type === 'approve' ? 'status-approved' : 'status-rejected'}`;
            statusBadge.innerHTML = `
                <span class="status-dot"></span>
                ${type === 'approve' ? 'Đã chấp thuận' : 'Đã từ chối'}
            `;
        }
        
        // Hide action buttons
        const actionsContainer = card.querySelector('.request-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = `
                <div style="text-align: center; width: 100%; color: ${type === 'approve' ? '#38A169' : '#E53E3E'}; font-weight: 600;">
                    ${type === 'approve' ? '✅ Đã chấp thuận' : '❌ Đã từ chối'}
                </div>
            `;
        }
    }
    
    // Update counters
    updatePendingCount(-1);
    
    // Show success notification
    showNotification(
        type === 'approve' ? 'Đã chấp thuận yêu cầu!' : 'Đã từ chối yêu cầu!',
        type === 'approve' ? 'success' : 'info'
    );
    
    // Remove from state
    state.pendingRequests = state.pendingRequests.filter(r => r.id !== ycId);
    
    // Fade out card after a delay
    setTimeout(() => {
        if (card) {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                card.remove();
                checkEmptyState();
            }, 500);
        }
    }, 2000);
}

function handleActionError(message, card, approveBtn, rejectBtn) {
    // Remove loading states
    if (approveBtn) approveBtn.classList.remove('loading');
    if (rejectBtn) rejectBtn.classList.remove('loading');
    if (card) card.classList.remove('processing');
    
    // Show error notification
    showNotification(message, 'error');
}

// ========================================
// UTILITY FUNCTIONS
// ========================================
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

function showNotification(message, type = 'info') {
    // Use SweetAlert2 if available
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

