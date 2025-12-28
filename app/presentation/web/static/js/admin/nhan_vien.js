// --- Quản lý Nhân viên (Admin) ---

document.addEventListener('DOMContentLoaded', function () {
    // --- Các phần tử DOM ---
    const elements = {
        addBtn: document.getElementById('btnAdd'),
        filterRole: document.getElementById('filterRole'),
        searchInput: document.getElementById('searchInput'),
        vaiTroSelect: document.getElementById('vaiTro'),
        btnSave: document.getElementById('btnSave'),
        btnCancel: document.getElementById('btnCancel'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        formModal: document.getElementById('formModal'),
        employeeForm: document.getElementById('employeeForm'),
        modalTitle: document.getElementById('modalTitle'),

        // Các trường nhập liệu của form
        editId: document.getElementById('editId'),
        hoTen: document.getElementById('hoTen'),
        tenTaiKhoan: document.getElementById('tenTaiKhoan'),
        email: document.getElementById('email'),
        matKhau: document.getElementById('matKhau'),
        accountFields: document.getElementById('accountFields'),
        khuVucGroup: document.getElementById('khuVucGroup'),
        khuVucSelect: document.getElementById('khuVucId'),

        tableBody: document.getElementById('tableBody')
    };

    let isEditMode = false;

    // --- Logic xử lý ---

    function openModal(mode = 'add', data = null) {
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa nhân viên' : 'Thêm nhân viên';

        if (!isEditMode) {
            elements.employeeForm.reset();
            elements.editId.value = '';
            elements.accountFields.style.display = 'block';
            elements.khuVucGroup.style.display = 'none';
            // Đặt các trường bắt buộc cho chế độ thêm mới
            elements.tenTaiKhoan.required = true;
            elements.email.required = true;
            elements.matKhau.required = true;
            elements.vaiTroSelect.required = true;
        } else {
            elements.editId.value = data.id;
            elements.hoTen.value = data.hoten;
            elements.accountFields.style.display = 'none';

            // Bỏ yêu cầu bắt buộc cho các trường ẩn khi ở chế độ chỉnh sửa
            elements.tenTaiKhoan.required = false;
            elements.email.required = false;
            elements.matKhau.required = false;
            elements.vaiTroSelect.required = false;

            // Xử lý trường khu vực nếu có
            if (data.khuvuc) {
                elements.khuVucGroup.style.display = 'block';
                elements.khuVucSelect.value = data.khuvuc;
            } else {
                elements.khuVucGroup.style.display = 'none';
            }
        }

        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = {
            ho_ten: elements.hoTen.value.trim()
        };

        if (!payload.ho_ten) {
            alert('Vui lòng nhập họ tên');
            return;
        }

        try {
            if (isEditMode) {
                if (elements.khuVucSelect.value) {
                    payload.khu_vuc_id = parseInt(elements.khuVucSelect.value);
                }
                await AdminAPI.put(`/api/admin/nhan-vien/${elements.editId.value}`, payload);
            } else {
                payload.ten_tai_khoan = elements.tenTaiKhoan.value.trim();
                payload.email = elements.email.value.trim();
                payload.mat_khau = elements.matKhau.value;
                payload.vai_tro = elements.vaiTroSelect.value;

                if (payload.vai_tro === 'PHUCVU' && elements.khuVucSelect.value) {
                    payload.khu_vuc_id = parseInt(elements.khuVucSelect.value);
                }

                if (!payload.ten_tai_khoan || !payload.email || !payload.mat_khau || !payload.vai_tro) {
                    alert('Vui lòng điền đầy đủ các trường bắt buộc');
                    return;
                }

                await AdminAPI.post('/api/admin/nhan-vien', payload);
            }

            AdminUI.reload();
        } catch (err) {
            // Lỗi đã được AdminAPI xử lý hiện thông báo rồi
        }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Bạn có chắc muốn xóa nhân viên này?')) {
            try {
                await AdminAPI.delete(`/api/admin/nhan-vien/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // --- Listeners ---

    if (elements.addBtn) {
        elements.addBtn.addEventListener('click', () => openModal('add'));
    }

    if (elements.btnSave) {
        elements.btnSave.addEventListener('click', handleSave);
    }

    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);

    if (elements.vaiTroSelect) {
        elements.vaiTroSelect.addEventListener('change', function () {
            elements.khuVucGroup.style.display = (this.value === 'PHUCVU') ? 'block' : 'none';
        });
    }

    if (elements.filterRole) {
        elements.filterRole.addEventListener('change', function () {
            const val = this.value;
            window.location.href = window.location.pathname + (val ? `?vai_tro=${val}` : '');
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

    // Delegate edit/delete events for safety
    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const deleteBtn = e.target.closest('.btn-delete');

            if (editBtn) {
                openModal('edit', {
                    id: editBtn.dataset.id,
                    hoten: editBtn.dataset.hoten,
                    khuvuc: editBtn.dataset.khuvuc
                });
            } else if (deleteBtn) {
                handleDelete(deleteBtn.dataset.id);
            }
        });
    }

    // Close modal on overlay click
    if (elements.formModal) {
        elements.formModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
