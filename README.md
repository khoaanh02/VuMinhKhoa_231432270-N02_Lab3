# 🔥 Thiết kế mạch báo cháy gia đình sử dụng ESP32, FreeRTOS và MQTT

> **Học phần:** Hệ thống Nhúng  
> **Sinh viên thực hiện:** Vũ Minh Khoa  
> **Mã sinh viên:** 231432270  
> **Lớp:** Điện Tử và Tin Học Công Nghiệp 1 - K64  

---

## 📌 Tổng quan Dự án

Hệ thống báo cháy gia đình sử dụng vi điều khiển **ESP32** chạy hệ điều hành thời gian thực **FreeRTOS** trên cả 2 nhân (**Core 0** và **Core 1**):
- Thu thập nồng độ khí gas/khói từ cảm biến **MQ-2 (`GPIO 34`)** và nhiệt độ môi trường từ cảm biến **DS18B20 (`GPIO 4`)**.
- Giao tiếp liên tác vụ an toàn thông qua 2 hàng đợi FreeRTOS: **`data Queue`** và **`data Alert`**, kết hợp với **Mutex / Binary Semaphore**.
- Tự động điều khiển **Quạt hút khí gas (`GPIO 18`)** khi nồng độ khí gas vượt ngưỡng (`≥ 400 ppm`) và **Máy bơm chữa cháy (`GPIO 19`)** khi nhiệt độ vượt ngưỡng (`≥ 50 °C`).
- Truyền dữ liệu thời gian thực lên **MQTT Broker (`broker.emqx.io`)** và hiển thị trực quan trên **Giao diện Web/App (`web_dashboard/index.html`)** gồm:
  - **2 thẻ HTML (`class="sensor-card"` / `class="gas-value"` / `class="temp-value"`)** hiển thị số liệu Nồng độ khí gas và Nhiệt độ.
  - **2 biểu đồ thời gian thực (Chart.js)** cập nhật trực tiếp Nồng độ khí gas và Nhiệt độ.
  - **2 nút `<button>`** điều khiển bật/tắt **Máy bơm** và **Quạt** ở chế độ **Manual**.


## 🚀 Hướng dẫn Chạy và Kiểm thử

### 1. Chạy mạch mô phỏng trên Wokwi
1. Truy cập [https://wokwi.com/projects/480213745557716993](https://wokwi.com/projects/new/esp32).

### 2. Mở Giao diện Web/App
1. Mở trực tiếp file `d:\KI 1 NAM 4\HỆ THỐNG NHÚNG\Lab_RTOS_BaoChay\web_dashboard\index.html` trên trình duyệt (Chrome / Edge / Firefox).
 nút kịch bản kiểm thử nhanh ngay trên giao diện Web hoặc nhấn **2 nút `<button>` Quạt & Máy bơm** để điều khiển ở chế độ **Manual**.

---
