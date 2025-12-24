import { phieuBep } from './phieu_cho_bep.js'

// Cấu hình cơ bản
const socket = io('http://127.0.0.1:5000', {
    transports: ['websocket'], // dùng WebSocket ngay từ đầu (bỏ qua Long-polling) cho nhanh
    autoConnect: true,         // Tự động kết nối ngay khi khởi tạo
});

// Lắng nghe sự kiện hệ thống
socket.on('connect', () => {
    console.log('Đã kết nối thành công! ID của tôi là:', socket.id);
});

socket.on('disconnect', (reason) => {
    console.log('Mất kết nối vì:', reason);
    if (reason === "io server disconnect") {
        // Nếu server chủ động đá client, client sẽ không tự kết nối lại
        // Phải gọi thủ công:
        socket.connect();
    }
});

socket.on('gui_phieu', (data) => {
    phieuBep.nhanThemPhieu(data);
});