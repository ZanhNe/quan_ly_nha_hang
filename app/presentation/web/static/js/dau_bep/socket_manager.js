import { phieuBep } from './phieu_cho_bep.js'

// Kết nối SocketIO cho Bếp
const socket = io('http://127.0.0.1:5000', {
    transports: ['websocket'], // dùng luôn websocket cho nó tít
    autoConnect: true,
});

// Lắng nghe sự kiện hệ thống
socket.on('connect', () => {
    console.log('Connect thành công! ID:', socket.id);
});

socket.on('disconnect', (reason) => {
    console.log('Mất kết nối vì:', reason);
    if (reason === "io server disconnect") {
        // Nếu server chủ động đá client, client sẽ không tự kết nối lại
        // Nếu máy chủ chủ động ngắt kết nối, client sẽ không tự động kết nối lại
        // Cần gọi hàm kết nối thủ công:
        socket.connect();
    }
});

socket.on('gui_phieu', (data) => {
    // Nhận sự kiện có phiếu mới
    phieuBep.nhanThemPhieu(data);
});