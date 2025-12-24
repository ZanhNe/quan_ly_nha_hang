
const headerJS = {
    // State
    page: 1, // Trang hiện tại (đã load trang 1 từ SSR)
    limit: 5,
    isLoading: false,
    els: {
        iconBtn: document.querySelector('.icon-btn'),
        btnLoadMoreNotify: document.querySelector('#btnLoadMoreNotify'),
        userTrigger: document.querySelector('.user-trigger'),
    },
    audio: null,

    init: function () {
        if (typeof NOTIFY_SOUND_URL !== 'undefined') {
            this.audio = new Audio(NOTIFY_SOUND_URL);
        }
        else {
            // Fallback (dự phòng) nếu quên khai báo
            this.audio = new Audio('/static/sounds/notification.mp3');
        }
        // Đóng dropdown khi click ra ngoài
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#notifyWrapper')) {
                document.getElementById('notifyDropdown').classList.remove('show');
            }
            if (!e.target.closest('#userWrapper')) {
                document.getElementById('userDropdown').classList.remove('show');
            }
        });

        this.els.iconBtn.addEventListener('click', (e) => {
            this.toggleNotify();
        });

        if (this.els.btnLoadMoreNotify) {
            this.els.btnLoadMoreNotify.addEventListener(('click'), (e) => {
                this.loadMoreNotify();
            });
        }

        this.els.userTrigger.addEventListener('click', (e) => {
            this.toggleUser();
        })
    },

    toggleNotify: function () {
        const dd = document.getElementById('notifyDropdown');
        dd.classList.toggle('show');
        // Đóng user dropdown nếu đang mở
        document.getElementById('userDropdown').classList.remove('show');
    },

    toggleUser: function () {
        const dd = document.getElementById('userDropdown');
        dd.classList.toggle('show');
        // Đóng notify dropdown nếu đang mở
        document.getElementById('notifyDropdown').classList.remove('show');
    },

    // Logic Load More (CSR)
    loadMoreNotify: function () {
        if (this.isLoading) return;

        const btn = document.getElementById('btnLoadMoreNotify');
        btn.innerText = 'Đang tải...';
        this.isLoading = true;

        // Trang tiếp theo
        const nextPage = this.page + 1;

        // Fetch API
        fetch(`/api/notifications?page=${nextPage}&limit=${this.limit}`)
            .then(res => res.json())
            .then(data => {
                // data.notifications: Array of objects
                // data.has_more: boolean

                if (data.notifications.length > 0) {
                    this.appendNotifications(data.notifications);
                    this.page = nextPage;
                }

                if (!data.has_more) {
                    btn.innerText = 'Đã hết thông báo';
                    btn.disabled = true;
                    btn.style.color = '#ccc';
                    btn.style.cursor = 'default';
                } else {
                    btn.innerText = 'Xem thêm tin cũ';
                }
            })
            .catch(err => {
                console.error(err);
                btn.innerText = 'Lỗi, thử lại';
            })
            .finally(() => {
                this.isLoading = false;
            });
    },

    appendNotifications: function (list) {
        const container = document.getElementById('notifyList');

        list.forEach(noti => {
            const li = document.createElement('li');
            li.className = `notify-item ${noti.is_read ? '' : 'unread'}`;

            // Icon logic (đơn giản hóa)
            const icon = noti.type.includes('order') ? '🍲' : '📢';

            li.innerHTML = `
                <a href="${noti.link || '#'}">
                    <div class="notify-icon">${icon}</div>
                    <div class="notify-content">
                        <p class="notify-text">${noti.message}</p>
                        <span class="notify-time">${noti.created_at_human}</span>
                    </div>
                </a>
            `;
            container.appendChild(li);
        });
    },
    appendNewNotification: function (noti) {
        const container = document.getElementById('notifyList');
        const notifyCount = document.getElementById('notifyCount');
        const iconBtn = document.querySelector('.icon-btn');


        if (notifyCount) {
            const unreadCount = +notifyCount.textContent + 1;
            notifyCount.textContent = unreadCount;

            const li = document.createElement('li');
            li.className = `notify-item ${noti.da_doc ? '' : 'unread'}`;

            // Icon logic (đơn giản hóa)
            const icon = noti.phan_loai.includes('HOANTHANHPHIEU') ? '✅' : '📢';

            const innerHTML = `
            <li class="notify-item ${noti.da_doc ? '' : 'unread'}">
                        <a href="${noti.link || '#'}">
                    <div class="notify-icon">${icon}</div>
                    <div class="notify-content">
                        <p class="notify-text">${noti.noi_dung}</p>
                        <span class="notify-time">${noti.ngay_tao}</span>
                    </div>
                </a>
                    </li>
            `;
            container.insertAdjacentHTML('afterbegin', innerHTML);
            container.lastElementChild.remove();
        } else {
            iconBtn.innerHTML = `🔔 <span class="badge-count" id="notifyCount">1</span>`
            const empty = document.querySelector('.empty-state');
            empty.remove();

            // Icon logic (đơn giản hóa)
            const icon = noti.phan_loai.includes('HOANTHANHPHIEU') ? '✅' : '📢';

            const innerHTML = `
            <li class="notify-item ${noti.da_doc ? '' : 'unread'}">
                        <a href="${noti.link || '#'}">
                    <div class="notify-icon">${icon}</div>
                    <div class="notify-content">
                        <p class="notify-text">${noti.noi_dung}</p>
                        <span class="notify-time">${noti.ngay_tao}</span>
                    </div>
                </a>
            </li>
            `;
            container.insertAdjacentHTML('afterbegin', innerHTML);
        }


    },
    playSound: function () {
        if (this.audio) {
            // Reset về đầu (để nếu tin đến dồn dập thì nó vẫn kêu lại từ đầu)
            this.audio.currentTime = 0;

            // Play và xử lý lỗi chặn Auto-play
            this.audio.play().catch(error => {
                console.warn("Trình duyệt chặn phát tiếng do người dùng chưa tương tác trang web.");
            });
        }
    },
};

// Init
document.addEventListener('DOMContentLoaded', () => headerJS.init());

export { headerJS };