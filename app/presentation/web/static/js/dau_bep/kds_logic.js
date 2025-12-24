const kds = {
    ticket: {},

    init: function () {
        const el = document.getElementById('ticket-raw');
        if (el) {
            try {
                this.ticket = JSON.parse(el.textContent);
                this.updateCounters();
            } catch (e) { console.error(e); }
        }
    },

    updateCounters: function () {
        // Đếm số món Done
        const doneItems = document.querySelectorAll('.item-row.is-done').length;
        document.getElementById('doneCounter').innerText = doneItems + " / " + this.ticket.ds_mon_ghi.length;
    },

    updateStatus: function (monId, newStatus) {
        if (!confirm(`Xác nhận trạng thái: ${newStatus}?`)) return;

        // Gọi APIs
        fetch(`http://127.0.0.1:5000/api/v1/mon-ghi/${monId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trang_thai: newStatus })
        })
            .then(res => res.json())
            .then(data => {
                window.location.reload();
            })
            .catch(err => {
                console.error(err);
                alert("Lỗi kết nối server!");
            });
    }
};

document.addEventListener('DOMContentLoaded', () => kds.init());