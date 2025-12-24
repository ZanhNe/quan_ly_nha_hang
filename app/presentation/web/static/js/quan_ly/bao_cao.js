/**
 * Báo cáo Tổng quan - JavaScript Module
 * Xử lý biểu đồ và tương tác
 */

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initDatePickers();
    initFilterButton();
    initCharts();
});

// ========================================
// DATE PICKERS
// ========================================
function initDatePickers() {
    const options = {
        dateFormat: 'Y-m-d',
        locale: {
            firstDayOfWeek: 1
        }
    };

    flatpickr('#tu-ngay', options);
    flatpickr('#den-ngay', options);
}

// ========================================
// FILTER
// ========================================
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

// ========================================
// CHARTS
// ========================================
function initCharts() {
    initRevenueChart();
    initHourlyChart();
}

function initRevenueChart() {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;

    const dataScript = document.getElementById('chart-data');
    if (!dataScript) return;

    const data = JSON.parse(dataScript.textContent || '[]');
    
    if (data.length === 0) {
        canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu</p></div>';
        return;
    }

    const labels = data.map(d => formatDate(d.ngay));
    const revenues = data.map(d => d.doanh_thu);
    const orders = data.map(d => d.so_don);

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Doanh thu (đ)',
                    data: revenues,
                    backgroundColor: 'rgba(255, 105, 180, 0.7)',
                    borderColor: '#FF69B4',
                    borderWidth: 1,
                    borderRadius: 8,
                    yAxisID: 'y'
                },
                {
                    label: 'Số đơn',
                    data: orders,
                    type: 'line',
                    borderColor: '#4299E1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#4299E1',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `Doanh thu: ${formatMoney(context.raw)} đ`;
                            }
                            return `Số đơn: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatMoney(value) + ' đ'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false
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

    // Fill all 24 hours
    const hourlyData = new Array(24).fill(0);
    data.forEach(d => {
        hourlyData[d.gio] = d.doanh_thu;
    });

    const labels = hourlyData.map((_, i) => `${i}h`);

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: hourlyData,
                backgroundColor: hourlyData.map((_, i) => {
                    // Peak hours highlight
                    if (i >= 11 && i <= 13) return 'rgba(255, 105, 180, 0.8)';
                    if (i >= 18 && i <= 20) return 'rgba(255, 105, 180, 0.8)';
                    return 'rgba(255, 105, 180, 0.4)';
                }),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: ctx => formatMoney(ctx.raw) + ' đ'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatMoney(value)
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 0,
                        callback: function(val, index) {
                            // Show only every 3rd hour
                            return index % 3 === 0 ? this.getLabelForValue(val) : '';
                        }
                    }
                }
            }
        }
    });
}

// ========================================
// UTILITIES
// ========================================
function formatMoney(amount) {
    if (!amount) return '0';
    return new Intl.NumberFormat('vi-VN').format(amount);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

