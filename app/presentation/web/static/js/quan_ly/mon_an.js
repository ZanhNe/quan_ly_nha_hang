/**
 * Thống kê Món ăn - JavaScript Module
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
    initTopDishesChart();
    initCategoryChart();
}

function initTopDishesChart() {
    const canvas = document.getElementById('topDishesChart');
    if (!canvas) return;

    const dataScript = document.getElementById('top-mon-data');
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent || '[]');
    
    if (data.length === 0) {
        canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu món ăn</p></div>';
        return;
    }

    // Top 10
    const topData = data.slice(0, 10);
    const labels = topData.map(d => truncateText(d.ten, 20));
    const quantities = topData.map(d => d.so_luong);

    // Colors gradient pink to light
    const colors = topData.map((_, i) => {
        const hue = 330; // Pink hue
        const saturation = 80 - (i * 5);
        const lightness = 55 + (i * 3);
        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    });

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Số lượng bán',
                data: quantities,
                backgroundColor: colors,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(ctx) {
                            // Show full name in tooltip
                            return topData[ctx[0].dataIndex].ten;
                        },
                        label: ctx => `Số lượng: ${ctx.raw} phần`
                    }
                }
            },
            scales: {
                x: { beginAtZero: true },
                y: {
                    ticks: {
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;

    const dataScript = document.getElementById('thong-ke-nhom-data');
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent || '[]');
    
    if (data.length === 0) {
        canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu danh mục</p></div>';
        return;
    }

    const labels = data.map(d => d.ten);
    const revenues = data.map(d => d.doanh_thu);

    // Sakura-inspired color palette
    const colors = [
        '#FF69B4', '#FF85C1', '#FFA6D0', '#FFC0DD', '#FFD9EC',
        '#E8B4CB', '#D190AA', '#BA6B89', '#A34668', '#8C2147'
    ];

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: revenues,
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((ctx.raw / total) * 100).toFixed(1);
                            return `${ctx.label}: ${formatMoney(ctx.raw)} đ (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatMoney(amount) {
    if (!amount) return '0';
    return new Intl.NumberFormat('vi-VN').format(amount);
}

