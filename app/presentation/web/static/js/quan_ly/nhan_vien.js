// --- Thống kê Hiệu suất Nhân viên ---

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
    initStaffChart();
}

let staffChartInstance = null;

// function initStaffChart() {
//     const canvas = document.getElementById('staffChart');
//     if (!canvas) return;

//     const dataScript = document.getElementById('nhan-vien-data');

//     if (!dataScript) return;

//     const data = JSON.parse(dataScript.textContent || '[]');
//     console.log(data);

//     if (data.length === 0) {
//         canvas.parentElement.innerHTML = '<div class="empty-panel"><span>📭</span><p>Chưa có dữ liệu nhân viên</p></div>';
//         return;
//     }

//     // Lấy top 10 nhân viên
//     const topData = data.slice(0, 10);
//     const labels = topData.map(d => d.ho_ten);
//     const revenues = topData.map(d => d.doanh_thu);
//     const sessions = topData.map(d => d.so_phien);

//     // Colors gradient
//     const colors = topData.map((_, i) => {
//         const opacity = 1 - (i * 0.08);
//         return `rgba(255, 105, 180, ${opacity})`;
//     });

//     new Chart(canvas, {
//         type: 'bar',
//         data: {
//             labels: labels,
//             datasets: [
//                 {
//                     label: 'Doanh thu (đ)',
//                     data: revenues,
//                     backgroundColor: colors,
//                     borderRadius: 8,
//                     yAxisID: 'y'
//                 },
//                 {
//                     label: 'Số phiên',
//                     data: sessions,
//                     type: 'line',
//                     borderColor: '#4299E1',
//                     backgroundColor: 'transparent',
//                     borderWidth: 3,
//                     pointRadius: 5,
//                     pointBackgroundColor: '#4299E1',
//                     tension: 0.3,
//                     yAxisID: 'y1'
//                 }
//             ]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             indexAxis: 'y',
//             interaction: {
//                 mode: 'index',
//                 intersect: false
//             },
//             plugins: {
//                 legend: {
//                     position: 'top',
//                     labels: { usePointStyle: true, padding: 20 }
//                 },
//                 tooltip: {
//                     callbacks: {
//                         label: function (ctx) {
//                             if (ctx.datasetIndex === 0) {
//                                 return `Doanh thu: ${formatMoney(ctx.raw)} đ`;
//                             }
//                             return `Số phiên: ${ctx.raw}`;
//                         }
//                     }
//                 }
//             },
//             scales: {
//                 y: {
//                     type: 'linear',
//                     position: 'bottom',
//                     beginAtZero: true,
//                     ticks: {
//                         callback: value => formatMoney(value) + ' đ'
//                     }
//                 },
//                 y1: {
//                     type: 'linear',
//                     position: 'top',
//                     beginAtZero: true,
//                     grid: { drawOnChartArea: false }
//                 }
//             }
//         }
//     });
// }

function initStaffChart() {
    const canvas = document.getElementById('staffChart');
    if (!canvas) return;

    const dataScript = document.getElementById('nhan-vien-data');

    // Kiểm tra xem thẻ chứa data có tồn tại không
    if (!dataScript) return;

    let data = [];
    try {
        data = JSON.parse(dataScript.textContent || '[]');
    } catch (e) {
        console.error("Lỗi parse JSON:", e);
        return;
    }

    // Nếu không có dữ liệu nhân viên thì báo rỗng
    if (data.length === 0) {
        if (canvas.parentElement) {
            canvas.parentElement.innerHTML = '<div class="empty-panel" style="text-align:center; padding: 20px;"><span>📭</span><p>Chưa có dữ liệu nhân viên</p></div>';
        }
        return;
    }

    // --- XỬ LÝ DỮ LIỆU ---
    // Lấy top 10
    const topData = data.slice(0, 10);
    const labels = topData.map(d => d.ho_ten);
    const revenues = topData.map(d => d.doanh_thu);
    const sessions = topData.map(d => d.so_phien);

    // Tạo màu (Gradient hồng)
    const colors = topData.map((_, i) => `rgba(255, 105, 180, ${0.8 - (i * 0.05)})`);

    // --- HỦY BIỂU ĐỒ CŨ (Quan trọng) ---
    // Sử dụng biến module 'staffChartInstance' thay vì window
    if (staffChartInstance) {
        staffChartInstance.destroy();
    }

    // --- TẠO BIỂU ĐỒ MỚI ---
    // Gán vào biến module để quản lý cho lần sau
    staffChartInstance = new Chart(canvas, {
        type: 'bar', // Loại chính là Bar
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Doanh thu',
                    data: revenues,
                    backgroundColor: colors,
                    borderRadius: 4,
                    order: 2, // Nằm dưới
                    yAxisID: 'y' // Trục trái
                },
                {
                    label: 'Số phiên',
                    data: sessions,
                    type: 'line', // Loại phụ là Line
                    borderColor: '#4299E1',
                    backgroundColor: '#4299E1',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#4299E1',
                    tension: 0.3,
                    order: 1, // Nằm trên
                    yAxisID: 'y1' // Trục phải
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // Đã ẩn trục dọc để biểu đồ đứng thẳng (chuẩn cho dạng Cột + Đường kết hợp)
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { usePointStyle: true, padding: 15 }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#000',
                    bodyColor: '#000',
                    borderColor: '#ddd',
                    borderWidth: 1,
                    callbacks: {
                        label: function (ctx) {
                            if (ctx.dataset.yAxisID === 'y') {
                                return `Doanh thu: ${formatMoney(ctx.raw)} đ`;
                            }
                            return `Số phiên: ${ctx.raw}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: { display: true, text: 'Doanh thu (VNĐ)' },
                    ticks: {
                        callback: value => formatMoney(value)
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: { display: true, text: 'Số phiên' },
                    grid: {
                        drawOnChartArea: false
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

