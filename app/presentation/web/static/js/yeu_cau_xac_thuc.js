const btnResend = document.getElementById("btnResend");
const spinner = btnResend.querySelector(".spinner");
const btnText = btnResend.querySelector("span");
const toast = document.getElementById("toast");

// Logic đếm ngược (Cooldown) để tránh Spam
let countdown = 0;

btnResend.addEventListener("click", () => {
  if (countdown > 0) return;

  // 1. UI Loading
  btnResend.disabled = true;
  btnText.innerText = "Đang gửi...";
  spinner.style.display = "block";

  // 2. Gọi API Resend (Giả lập)
  fetch("/api/resend-verification", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // Nếu cần gửi email cụ thể thì body: JSON.stringify({email: '...'})
    // Nhưng thường backend tự lấy current_user.email
  })
    .then((res) => {
      if (res.ok) {
        showSuccess();
      } else {
        alert("Có lỗi xảy ra, vui lòng thử lại sau.");
        resetBtn();
      }
    })
    .catch((err) => {
      console.error(err);
      // Giả lập thành công để test giao diện
      showSuccess();
    });
});

function showSuccess() {
  // Hiển thị Toast thông báo
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);

  // Bắt đầu đếm ngược 60s
  startCooldown(60);
}

function startCooldown(seconds) {
  countdown = seconds;
  spinner.style.display = "none";
  btnResend.disabled = true;

  const interval = setInterval(() => {
    countdown--;
    btnText.innerText = `Gửi lại sau ${countdown}s`;

    if (countdown <= 0) {
      clearInterval(interval);
      resetBtn();
    }
  }, 1000);
}

function resetBtn() {
  btnResend.disabled = false;
  btnText.innerText = "Gửi lại email xác thực";
  spinner.style.display = "none";
}
