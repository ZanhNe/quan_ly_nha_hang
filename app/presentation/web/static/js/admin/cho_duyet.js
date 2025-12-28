/**
 * Admin - Duyệt tài khoản JS (Refactored)
 */

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        approvalModal: document.getElementById('approvalModal'),
        approvalUserName: document.getElementById('approvalUserName'),
        approveBtn: document.getElementById('approveBtn'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        btnCancel: document.getElementById('btnCancel'),
        container: document.querySelector('.pending-grid')
    };

    let currentTaiKhoanId = null;
    let selectedRole = null;

    function openModal(id, name) {
        currentTaiKhoanId = id;
        elements.approvalUserName.textContent = name;
        selectedRole = null;
        document.querySelectorAll('.role-option').forEach(el => el.classList.remove('selected'));
        elements.approveBtn.disabled = true;
        elements.approvalModal.classList.add('show');
    }

    function closeModal() {
        elements.approvalModal.classList.remove('show');
    }

    async function handleApprove() {
        if (!currentTaiKhoanId || !selectedRole) return;
        try {
            await AdminAPI.put(`/api/admin/tai-khoan/${currentTaiKhoanId}/duyet`, { vai_tro: selectedRole });
            AdminUI.reload();
        } catch (err) { }
    }

    async function handleReject(id) {
        if (AdminUI.showConfirm('Từ chối tài khoản này?')) {
            try {
                await AdminAPI.put(`/api/admin/tai-khoan/${id}/tu-choi`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.container) {
        elements.container.addEventListener('click', function (e) {
            const approveBtn = e.target.closest('.btn-approve-pending');
            const rejectBtn = e.target.closest('.btn-reject-pending');

            if (approveBtn) openModal(approveBtn.dataset.id, approveBtn.dataset.name);
            if (rejectBtn) handleReject(rejectBtn.dataset.id);
        });
    }

    document.querySelectorAll('.role-option').forEach(opt => {
        opt.addEventListener('click', function () {
            document.querySelectorAll('.role-option').forEach(el => el.classList.remove('selected'));
            this.classList.add('selected');
            selectedRole = this.dataset.role;
            elements.approveBtn.disabled = false;
        });
    });

    if (elements.approveBtn) elements.approveBtn.addEventListener('click', handleApprove);
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeModal);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeModal);

    if (elements.approvalModal) {
        elements.approvalModal.addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
    }
});
