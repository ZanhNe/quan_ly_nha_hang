/**
 * Admin - Quản lý Khu vực JS (Refactored)
 */

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        addBtn: document.getElementById('btnAdd'),
        btnSave: document.getElementById('btnSave'),
        btnCancel: document.getElementById('btnCancel'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        formModal: document.getElementById('formModal'),
        dataForm: document.getElementById('dataForm'),
        modalTitle: document.getElementById('modalTitle'),

        editId: document.getElementById('editId'),
        ten: document.getElementById('ten'),

        tableBody: document.querySelector('.data-table tbody')
    };

    let isEditMode = false;

    function openModal(mode = 'add', data = null) {
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa khu vực' : 'Thêm khu vực';

        if (!isEditMode) {
            elements.dataForm.reset();
            elements.editId.value = '';
        } else {
            elements.editId.value = data.id;
            elements.ten.value = data.ten;
        }

        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = { ten: elements.ten.value.trim() };
        if (!payload.ten) return alert('Vui lòng nhập tên khu vực');

        try {
            if (isEditMode) {
                await AdminAPI.put(`/api/admin/khu-vuc/${elements.editId.value}`, payload);
            } else {
                await AdminAPI.post('/api/admin/khu-vuc', payload);
            }
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Xóa khu vực này?')) {
            try {
                await AdminAPI.delete(`/api/admin/khu-vuc/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    if (elements.addBtn) elements.addBtn.addEventListener('click', () => openModal('add'));
    if (elements.btnSave) elements.btnSave.addEventListener('click', handleSave);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const deleteBtn = e.target.closest('.btn-delete');

            if (editBtn) openModal('edit', { id: editBtn.dataset.id, ten: editBtn.dataset.ten });
            if (deleteBtn) handleDelete(deleteBtn.dataset.id);
        });
    }

    if (elements.formModal) {
        elements.formModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
