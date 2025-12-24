/**
 * Báo cáo Doanh thu - JavaScript Module
 */

document.addEventListener('DOMContentLoaded', () => {
    initDatePickers();
    initFilterButton();
    initCharts();
});

function initDatePickers() {
    const options = {
        dateFormat: 'Y-m-d',
        locale: { firstDayOfWeek: 1 }
    };
    flatpickr('#tu-ngay', options);
    flatpickr('#den-ngay', options);
}

function initFilterButton() {
    const btnFilter = document.getElementById('btn-filter');
    if (btnFilter) {
        btnFilter.addEventListener('click', () => {
            const tuNgay = document.getElementById('tu-ngay').value;
            const denNgay = document.getElementById('den-ngay').value;
            
            const url = new URL(window.location.href);
            url.searchParams.set('tu_ngay', tuNgay);
            url.searchParams.set('den_ngay', denNgay);
            
            window.location.href = url.toString();
        });
    }
}

function initCharts() {
    initRevenueChart();
    initHourlyChart();
}

function initRevenueChart() {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;

    const dataScript = document.getElementById('chi-tiet-ngay-data');
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent || '[]');
    
    if (data.length === 0) {
        canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu</p></div>';
        return;
    }

    const labels = data.map(d => formatDate(d.ngay));
    const revenues = data.map(d => d.doanh_thu);

    // Calculate gradient
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, 'rgba(255, 105, 180, 0.4)');
    gradient.addColorStop(1, 'rgba(255, 105, 180, 0.05)');

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: revenues,
                borderColor: '#FF69B4',
                backgroundColor: gradient,
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: '#FF69B4',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => 'Doanh thu: ' + formatMoney(ctx.raw) + ' đ'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatMoney(value) + ' đ'
                    }
                }
            }
        }
    });
}

function initHourlyChart() {
    const canvas = document.getElementById('hourlyChart');
    if (!canvas) return;

    const dataScript = document.getElementById('thong-ke-gio-data');
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent || '[]');
    
    if (data.length === 0) {
        canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu</p></div>';
        return;
    }

    const hourlyData = new Array(24).fill(0);
    data.forEach(d => { hourlyData[d.gio] = d.so_don; });

    const labels = hourlyData.map((_, i) => `${i}h`);

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Số đơn',
                data: hourlyData,
                backgroundColor: hourlyData.map((_, i) => {
                    if (i >= 11 && i <= 13) return 'rgba(66, 153, 225, 0.8)';
                    if (i >= 18 && i <= 20) return 'rgba(66, 153, 225, 0.8)';
                    return 'rgba(66, 153, 225, 0.4)';
                }),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true },
                x: {
                    ticks: {
                        maxRotation: 0,
                        callback: function(val, index) {
                            return index % 3 === 0 ? this.getLabelForValue(val) : '';
                        }
                    }
                }
            }
        }
    });
}

function formatMoney(amount) {
    if (!amount) return '0';
    return new Intl.NumberFormat('vi-VN').format(amount);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

