/**
 * Admin - Quản lý Bàn JS (Refactored)
 */

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        addBtn: document.getElementById('btnAdd'),
        filterKhuVuc: document.getElementById('filterKhuVuc'),
        filterTrangThai: document.getElementById('filterTrangThai'),
        btnSave: document.getElementById('btnSave'),
        btnCancel: document.getElementById('btnCancel'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        formModal: document.getElementById('formModal'),
        dataForm: document.getElementById('dataForm'),
        modalTitle: document.getElementById('modalTitle'),

        editId: document.getElementById('editId'),
        ten: document.getElementById('ten'),
        khuVucId: document.getElementById('khuVucId'),
        soGhe: document.getElementById('soGhe'),

        tableBody: document.getElementById('tableBody')
    };

    let isEditMode = false;

    function openModal(mode = 'add', data = null) {
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa bàn' : 'Thêm bàn';

        if (!isEditMode) {
            elements.dataForm.reset();
            elements.editId.value = '';
        } else {
            elements.editId.value = data.id;
            elements.ten.value = data.ten;
            elements.khuVucId.value = data.khuvuc;
            elements.soGhe.value = data.soghe;
        }

        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = {
            ten: elements.ten.value.trim(),
            khu_vuc_id: parseInt(elements.khuVucId.value),
            so_ghe: parseInt(elements.soGhe.value)
        };

        if (!payload.ten || !payload.khu_vuc_id || isNaN(payload.so_ghe)) {
            alert('Vui lòng nhập đầy đủ thông tin');
            return;
        }

        try {
            if (isEditMode) {
                await AdminAPI.put(`/api/admin/ban/${elements.editId.value}`, payload);
            } else {
                await AdminAPI.post('/api/admin/ban', payload);
            }
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Xóa bàn này?')) {
            try {
                await AdminAPI.delete(`/api/admin/ban/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    async function handleReset(id) {
        if (AdminUI.showConfirm('Reset trạng thái bàn về TRỐNG?')) {
            try {
                // API is PUT according to admin_api.py
                await AdminAPI.put(`/api/admin/ban/${id}/reset`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.addBtn) elements.addBtn.addEventListener('click', () => openModal('add'));
    if (elements.btnSave) elements.btnSave.addEventListener('click', handleSave);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);

    const applyFilters = () => {
        const params = new URLSearchParams(window.location.search);
        if (elements.filterKhuVuc.value) params.set('khu_vuc_id', elements.filterKhuVuc.value);
        else params.delete('khu_vuc_id');

        if (elements.filterTrangThai.value) params.set('trang_thai', elements.filterTrangThai.value);
        else params.delete('trang_thai');

        window.location.search = params.toString();
    };

    if (elements.filterKhuVuc) elements.filterKhuVuc.addEventListener('change', applyFilters);
    if (elements.filterTrangThai) elements.filterTrangThai.addEventListener('change', applyFilters);

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const deleteBtn = e.target.closest('.btn-delete');
            const resetBtn = e.target.closest('.btn-reset');

            if (editBtn) {
                openModal('edit', {
                    id: editBtn.dataset.id,
                    ten: editBtn.dataset.ten,
                    khuvuc: editBtn.dataset.khuvuc,
                    soghe: editBtn.dataset.soghe
                });
            } else if (deleteBtn) {
                handleDelete(deleteBtn.dataset.id);
            } else if (resetBtn) {
                handleReset(resetBtn.dataset.id);
            }
        });
    }

    if (elements.formModal) {
        elements.formModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
