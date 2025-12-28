
window.AdminAPI = {
    async request(url, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `Lỗi hệ thống (${response.status})`);
            }

            return result;
        } catch (error) {
            console.error(`AdminAPI Error [${method} ${url}]:`, error);
            alert(`Lỗi: ${error.message}`);
            throw error;
        }
    },

    async get(url) { return this.request(url, 'GET'); },
    async post(url, data) { return this.request(url, 'POST', data); },
    async put(url, data) { return this.request(url, 'PUT', data); },
    async delete(url) { return this.request(url, 'DELETE'); }
};

window.AdminUI = {
    toggleModal(modalId, show = true) {
        const modal = document.getElementById(modalId);
        if (modal) {
            if (show) modal.classList.add('show');
            else modal.classList.remove('show');
        }
    },

    showConfirm(message) {
        return confirm(message);
    },

    reload() {
        window.location.reload();
    }
};
