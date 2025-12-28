/**
 * Quản lý Khuyến mãi (Admin)
 */

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        addBtn: document.getElementById('btnAdd'),
        filterHoatDong: document.getElementById('filterHoatDong'),
        btnSave: document.getElementById('btnSave'),
        btnCancel: document.getElementById('btnCancel'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        formModal: document.getElementById('formModal'),
        dataForm: document.getElementById('dataForm'),
        modalTitle: document.getElementById('modalTitle'),

        // Fields
        editId: document.getElementById('editId'),
        ten: document.getElementById('ten'),
        moTa: document.getElementById('moTa'),
        loai: document.getElementById('loai'),
        tiLe: document.getElementById('tiLe'),
        soTienGiam: document.getElementById('soTienGiam'),
        giaTriToiThieu: document.getElementById('giaTriToiThieu'),
        tiLeGroup: document.getElementById('tiLeGroup'),
        soTienGiamGroup: document.getElementById('soTienGiamGroup'),
        thuTuUuTien: document.getElementById('thuTuUuTien'),
        tuDongApDung: document.getElementById('tuDongApDung'),

        tableBody: document.getElementById('tableBody')
    };

    let isEditMode = false;

    function toggleLoai() {
        // Ẩn/hiện các trường nhập liệu tùy thuộc vào loại giảm giá (phần trăm hoặc tiền mặt)
        if (elements.loai.value === 'phan_tram') {
            elements.tiLeGroup.style.display = 'block';
            elements.soTienGiamGroup.style.display = 'none';
        } else {
            elements.tiLeGroup.style.display = 'none';
            elements.soTienGiamGroup.style.display = 'block';
        }
    }

    function openModal(mode = 'add', data = null) {
        // Mở modal để thêm mới hoặc chỉnh sửa thông tin khuyến mãi
        isEditMode = (mode === 'edit');
        elements.modalTitle.textContent = isEditMode ? 'Sửa khuyến mãi' : 'Thêm khuyến mãi';

        if (!isEditMode) {
            elements.dataForm.reset();
            elements.editId.value = '';
        } else {
            elements.editId.value = data.id;
            elements.ten.value = data.ten;
            elements.moTa.value = data.mo_ta || '';
            elements.loai.value = data.loai;
            elements.tiLe.value = data.ti_le || '';
            elements.soTienGiam.value = data.so_tien_giam || '';
            elements.giaTriToiThieu.value = data.gia_tri_don_hang_toi_thieu || 0;
            elements.thuTuUuTien.value = data.thu_tu_uu_tien || 0;
            elements.tuDongApDung.checked = data.tu_dong_ap_dung || false;
        }
        toggleLoai();
        elements.formModal.classList.add('show');
    }

    function closeModal() {
        elements.formModal.classList.remove('show');
    }

    async function handleSave() {
        const payload = {
            ten: elements.ten.value.trim(),
            mo_ta: elements.moTa.value.trim(),
            loai: elements.loai.value,
            gia_tri_don_hang_toi_thieu: parseFloat(elements.giaTriToiThieu.value) || 0,
            thu_tu_uu_tien: parseInt(elements.thuTuUuTien.value) || 0,
            tu_dong_ap_dung: elements.tuDongApDung.checked
        };

        if (payload.loai === 'phan_tram') {
            payload.ti_le = parseFloat(elements.tiLe.value);
            payload.so_tien_giam = null;
        } else {
            payload.so_tien_giam = parseFloat(elements.soTienGiam.value);
            payload.ti_le = null;
        }

        if (!payload.ten) {
            alert('Vui lòng nhập tên khuyến mãi');
            return;
        }

        try {
            if (isEditMode) {
                await AdminAPI.put(`/api/admin/khuyen-mai/${elements.editId.value}`, payload);
            } else {
                await AdminAPI.post('/api/admin/khuyen-mai', payload);
            }
            AdminUI.reload();
        } catch (err) { }
    }

    async function toggleStatus(id, activate) {
        const action = activate ? 'kich-hoat' : 'vo-hieu-hoa';
        try {
            await AdminAPI.put(`/api/admin/khuyen-mai/${id}/${action}`);
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleDelete(id) {
        if (AdminUI.showConfirm('Xóa vĩnh viễn khuyến mãi này?')) {
            try {
                await AdminAPI.delete(`/api/admin/khuyen-mai/${id}`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.addBtn) elements.addBtn.addEventListener('click', () => openModal('add'));
    if (elements.btnSave) elements.btnSave.addEventListener('click', handleSave);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);
    if (elements.loai) elements.loai.addEventListener('change', toggleLoai);

    if (elements.filterHoatDong) {
        elements.filterHoatDong.addEventListener('change', function () {
            const val = this.value;
            window.location.search = val ? `hoat_dong=${val}` : '';
        });
    }

    if (elements.tableBody) {
        elements.tableBody.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit');
            const toggleBtn = e.target.closest('.btn-toggle');
            const deleteBtn = e.target.closest('.btn-delete');

            if (editBtn) {
                const data = JSON.parse(editBtn.dataset.km);
                openModal('edit', data);
            } else if (toggleBtn) {
                toggleStatus(toggleBtn.dataset.id, toggleBtn.dataset.activate === 'true');
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
