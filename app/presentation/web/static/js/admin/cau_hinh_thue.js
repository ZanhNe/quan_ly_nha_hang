/**
 * Admin - Quản lý Cấu hình Thuế JS (Refactored)
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
        tiLe: document.getElementById('tiLe'),

        tableBody: document.querySelector('.data-table tbody')
    };

    let isEditMode = false;

    function openModal(mode = 'add', data = null) {
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa cấu hình thuế' : 'Thêm cấu hình thuế';

        if (!isEditMode) {
            elements.dataForm.reset();
            elements.editId.value = '';
        } else {
            elements.editId.value = data.id;
            elements.ten.value = data.ten;
            elements.tiLe.value = data.tile;
        }

        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = {
            ten: elements.ten.value.trim(),
            ti_le: parseFloat(elements.tiLe.value)
        };

        if (!payload.ten || isNaN(payload.ti_le)) {
            alert('Vui lòng điền đầy đủ thông tin');
            return;
        }

        try {
            if (isEditMode) {
                await AdminAPI.put(`/api/admin/cau-hinh-thue/${elements.editId.value}`, payload);
            } else {
                await AdminAPI.post('/api/admin/cau-hinh-thue', payload);
            }
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleActivate(id) {
        try {
            await AdminAPI.put(`/api/admin/cau-hinh-thue/${id}/kich-hoat`);
            AdminUI.reload();
        } catch (err) { }
    }

    // Listeners
    if (elements.addBtn) elements.addBtn.addEventListener('click', () => openModal('add'));
    if (elements.btnSave) elements.btnSave.addEventListener('click', handleSave);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const activateBtn = e.target.closest('.btn-activate');

            if (editBtn) {
                openModal('edit', {
                    id: editBtn.dataset.id,
                    ten: editBtn.dataset.ten,
                    tile: editBtn.dataset.tile
                });
            } else if (activateBtn) {
                handleActivate(activateBtn.dataset.id);
            }
        });
    }

    if (elements.formModal) {
        elements.formModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
