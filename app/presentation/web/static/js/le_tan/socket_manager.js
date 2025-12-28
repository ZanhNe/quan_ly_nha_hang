import { updateTable } from './danh_dau.js'


// Kết nối SocketIO cho Lễ tân
const socket = io('http://127.0.0.1:5000', {
  transports: ['websocket'], // dùng luôn websocket cho khỏe
  autoConnect: true,
});

// Lắng nghe sự kiện hệ thống
socket.on('connect', () => {
  console.log('Connect ngon lành! ID:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.log('Mất kết nối vì:', reason);
  if (reason === "io server disconnect") {
    // Nếu server chủ động đá client, client sẽ không tự kết nối lại
    // Phải gọi thủ công:
    socket.connect();
  }
});

socket.on('chon_ban', (data) => {
  // Cập nhật trạng thái bàn realtime khi có máy khác chọn
  updateTable(data);
});

