import { headerJS } from '../header.js'

// Kết nối SocketIO đến server
const socket = io('http://127.0.0.1:5000', {
    transports: ['websocket'], // dùng luôn WebSocket cho nó nhanh, bỏ qua polling
    autoConnect: true,         // Tự động kết nối luôn
});

// Lắng nghe sự kiện hệ thống
socket.on('connect', () => {
    console.log('Connect thành công! Socket ID:', socket.id);
    console.log('Kết nối thành công! Socket ID:', socket.id);
});

socket.on('disconnect', (reason) => {
    console.log('Mất kết nối vì:', reason);
    if (reason === "io server disconnect") {
        // Nếu máy chủ chủ động ngắt kết nối, client sẽ không tự động kết nối lại
        // Cần phải gọi hàm kết nối thủ công:
        socket.connect();
    }
});

socket.on('hoan_thanh_phieu', (data) => {
    // Nhận thông báo khi bếp hoàn thành món ăn
    headerJS.appendNewNotification(data);
    headerJS.playSound()
});
