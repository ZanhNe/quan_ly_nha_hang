/// --- Quản lý Món ăn (Admin) ---

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        addBtn: document.getElementById('btnAdd'),
        filterNhomMon: document.getElementById('filterNhomMon'),
        searchInput: document.getElementById('searchInput'),
        btnSave: document.getElementById('btnSave'),
        btnCancel: document.getElementById('btnCancel'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        formModal: document.getElementById('formModal'),
        dataForm: document.getElementById('dataForm'),
        modalTitle: document.getElementById('modalTitle'),

        // Fields
        editId: document.getElementById('editId'),
        ten: document.getElementById('ten'),
        nhomMonId: document.getElementById('nhomMonId'),
        gia: document.getElementById('gia'),
        hinh: document.getElementById('hinh'),

        tableBody: document.getElementById('tableBody')
    };

    let isEditMode = false;

    function openModal(mode = 'add', data = null) {
        // Mở modal để thêm mới hoặc cập nhật thông tin món ăn
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa món ăn' : 'Thêm món ăn';

        if (!isEditMode) {
            elements.dataForm.reset();
            elements.editId.value = '';
        } else {
            elements.editId.value = data.id;
            elements.ten.value = data.ten;
            elements.nhomMonId.value = data.nhommon;
            elements.gia.value = data.gia;
            elements.hinh.value = data.hinh || '';
        }

        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = {
            ten: elements.ten.value.trim(),
            nhom_mon_id: parseInt(elements.nhomMonId.value),
            gia: parseFloat(elements.gia.value),
            hinh: elements.hinh.value.trim()
        };

        if (!payload.ten || isNaN(payload.nhom_mon_id) || isNaN(payload.gia)) {
            alert('Vui lòng điền đầy đủ các thông tin cần thiết');
            return;
        }

        try {
            if (isEditMode) {
                await AdminAPI.put(`/api/admin/mon/${elements.editId.value}`, payload);
            } else {
                await AdminAPI.post('/api/admin/mon', payload);
            }
            AdminUI.reload();
        } catch (err) { }
    }

    async function toggleStatus(id, newStatus) {
        try {
            await AdminAPI.put(`/api/admin/mon/${id}/trang-thai`, { trang_thai: newStatus });
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Xóa món này (soft delete)?')) {
            try {
                await AdminAPI.delete(`/api/admin/mon/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.addBtn) elements.addBtn.addEventListener('click', () => openModal('add'));
    if (elements.btnSave) elements.btnSave.addEventListener('click', handleSave);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);

    if (elements.filterNhomMon) {
        elements.filterNhomMon.addEventListener('change', function () {
            const val = this.value;
            window.location.search = val ? `nhom_mon_id=${val}` : '';
        });
    }

    if (elements.searchInput) {
        elements.searchInput.addEventListener('keyup', function () {
            const q = this.value.toLowerCase();
            document.querySelectorAll('#tableBody tr[data-name]').forEach(row => {
                const name = row.dataset.name.toLowerCase();
                row.style.display = name.includes(q) ? '' : 'none';
            });
        });
    }

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const toggleBtn = e.target.closest('.btn-toggle');
            const deleteBtn = e.target.closest('.btn-delete');

            if (editBtn) {
                openModal('edit', {
                    id: editBtn.dataset.id,
                    ten: editBtn.dataset.ten,
                    nhommon: editBtn.dataset.nhommon,
                    gia: editBtn.dataset.gia,
                    hinh: editBtn.dataset.hinh
                });
            } else if (toggleBtn) {
                toggleStatus(toggleBtn.dataset.id, toggleBtn.dataset.trangThai);
            } else if (deleteBtn) {
                handleDelete(deleteBtn.dataset.id);
            }
        });
    }

    if (elements.formModal) {
        elements.formModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
