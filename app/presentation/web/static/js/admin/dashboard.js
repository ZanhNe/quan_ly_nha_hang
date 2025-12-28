/**
 * Admin Dashboard - Pending Approvals JS (Refactored)
 */

document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        approvalModal: document.getElementById('approvalModal'),
        approvalUserName: document.getElementById('approvalUserName'),
        approveBtn: document.getElementById('approveBtn'),
        btnCloseModal: document.getElementById('btnCloseModal'),
        btnCancel: document.getElementById('btnCancel'),
        pendingGrid: document.querySelector('.pending-grid')
    };

    let currentTaiKhoanId = null;
    let selectedRole = null;

    function openApprovalModal(id, name) {
        currentTaiKhoanId = id;
        elements.approvalUserName.textContent = name;
        selectedRole = null;
        document.querySelectorAll('.role-option').forEach(el => el.classList.remove('selected'));
        elements.approveBtn.disabled = true;

        elements.approvalModal.classList.add('show');
    }

    function closeApprovalModal() {
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
        if (AdminUI.showConfirm('Từ chối tài khoản này (sẽ bị khóa)?')) {
            try {
                await AdminAPI.put(`/api/admin/tai-khoan/${id}/tu-choi`);
                AdminUI.reload();
            } catch (err) { }
        }
    }

    // Listeners
    if (elements.pendingGrid) {
        elements.pendingGrid.addEventListener('click', function (e) {
            const approveBtn = e.target.closest('.btn-approve-pending');
            const rejectBtn = e.target.closest('.btn-reject-pending');

            if (approveBtn) openApprovalModal(approveBtn.dataset.id, approveBtn.dataset.name);
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
    if (elements.btnCloseModal) elements.btnCloseModal.addEventListener('click', closeApprovalModal);
    if (elements.btnCancel) elements.btnCancel.addEventListener('click', closeApprovalModal);

    if (elements.approvalModal) {
        elements.approvalModal.addEventListener('click', function (e) {
            if (e.target === this) closeApprovalModal();
        });
    }
});
