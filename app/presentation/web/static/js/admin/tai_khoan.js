/// --- Quản lý Nhân viên (Admin) ---

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        filterTrangThai: document.getElementById('filterTrangThai'),
        searchInput: document.getElementById('searchInput'),
        tableBody: document.getElementById('tableBody')
    };

    function applyFilters() {
        // Áp dụng bộ lọc trạng thái và tìm kiếm, sau đó reload trang
        const params = new URLSearchParams(window.location.search);
        if (elements.filterTrangThai.value) {
            params.set('trang_thai', elements.filterTrangThai.value);
        } else {
            params.delete('trang_thai');
        }

        if (elements.searchInput.value.trim()) {
            params.set('search', elements.searchInput.value.trim());
        } else {
            params.delete('search');
        }

        window.location.search = params.toString();
    }

    async function handleLock(id) {
        if (AdminUI.showConfirm('Khóa tài khoản này?')) {
            try {
                await AdminAPI.put(`/api/admin/tai-khoan/${id}/khoa`);
                AdminUI.reload();
            } catch (err) {
                // Lỗi đã được AdminAPI xử lý thông báo
            }
        }
    }

    async function handleUnlock(id) {
        if (AdminUI.showConfirm('Mở khóa tài khoản này?')) {
            try {
                await AdminAPI.put(`/api/admin/tai-khoan/${id}/mo-khoa`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Xóa tài khoản này? Hành động này không thể hoàn tác!')) {
            try {
                await AdminAPI.delete(`/api/admin/tai-khoan/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.filterTrangThai) {
        elements.filterTrangThai.addEventListener('change', applyFilters);
    }

    if (elements.searchInput) {
        elements.searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') applyFilters();
        });
    }

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const lockBtn = e.target.closest('.btn-lock');
            const unlockBtn = e.target.closest('.btn-unlock');

            if (lockBtn) handleLock(lockBtn.dataset.id);
            if (unlockBtn) handleUnlock(unlockBtn.dataset.id);

            const deleteBtn = e.target.closest('.btn-delete');
            if (deleteBtn) handleDelete(deleteBtn.dataset.id);
        });
    }
});
