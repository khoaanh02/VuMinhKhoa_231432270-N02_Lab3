# -*- coding: utf-8 -*-
"""
Script tạo bộ hình ảnh minh họa chất lượng cao cho Báo cáo Lab Hệ thống Nhúng:
1. 01_rtos_architecture.png       - Kiến trúc FreeRTOS Dual-Core (Core 0 & Core 1, data Queue, data Alert)
2. 02_semaphore_vs_queue.png      - Cơ chế giao tiếp giữa các Task: Semaphore và Queue
3. 03_wokwi_circuit_normal.png    - Sơ đồ mạch và mô phỏng Wokwi ở trạng thái bình thường
4. 04_wokwi_circuit_alarm.png     - Mô phỏng Wokwi khi vượt ngưỡng Gas & Nhiệt độ (Quạt & Bơm BẬT)
5. 05_web_dashboard_normal.png    - Giao diện Web/App hiển thị 2 thẻ số, 2 biểu đồ, 2 nút điều khiển (Auto)
6. 06_web_dashboard_manual.png    - Giao diện Web/App khi Cảnh báo & Điều khiển bằng 2 nút Button (Manual)
"""

import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

OUT_DIR = r"d:\KI 1 NAM 4\HỆ THỐNG NHÚNG\Lab_RTOS_BaoChay\images"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def draw_box(ax, x, y, w, h, title, subtitle="", bg="#1e293b", border="#38bdf8",
             title_color="#ffffff", sub_color="#cbd5e1", title_size=11, sub_size=9, radius=0.02):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=bg, edgecolor=border, linewidth=2.0
    )
    ax.add_patch(patch)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.65, title, color=title_color,
                fontsize=title_size, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, y + h * 0.30, subtitle, color=sub_color,
                fontsize=sub_size, ha="center", va="center")
    else:
        ax.text(x + w / 2, y + h / 2, title, color=title_color,
                fontsize=title_size, fontweight="bold", ha="center", va="center")


def arrow(ax, x1, y1, x2, y2, color="#38bdf8", label="", label_offset=(0, 0.02)):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45", color=color, lw=2.2)
    )
    if label:
        mx, my = (x1 + x2) / 2 + label_offset[0], (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, color=color, fontsize=8.8, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#0f172a", edgecolor=color, lw=1))


# ==============================================================================
# HÌNH 1: SƠ ĐỒ KIẾN TRÚC HỆ THỐNG FREERTOS TRÊN ESP32 (CORE 0 & CORE 1)
# ==============================================================================
def make_img1_rtos_architecture():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=180)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.95,
            "KIẾN TRÚC ĐA NHIỆM FREERTOS TRÊN ESP32 (DUAL-CORE) & GIAO TIẾP HÀNG ĐỢI QUEUE",
            color="#ffffff", fontsize=14, fontweight="bold", ha="center")
    ax.text(0.5, 0.91,
            "Đề tài: Thiết kế Mạch báo cháy gia đình | Sinh viên: Vũ Minh Khoa - 231432270",
            color="#94a3b8", fontsize=10, ha="center")

    # Khối Cảm biến bên trái
    draw_box(ax, 0.03, 0.62, 0.17, 0.18,
             "CẢM BIẾN KHÍ GAS\nMQ-2",
             "Ngõ ra Analog: GPIO 34\nĐo khói / LPG (0-1000 ppm)",
             bg="#1e293b", border="#f59e0b", title_color="#fde047")

    draw_box(ax, 0.03, 0.36, 0.17, 0.18,
             "CẢM BIẾN NHIỆT ĐỘ\nDS18B20",
             "Giao tiếp 1-Wire: GPIO 4\nĐo nhiệt độ (-55 đến 125°C)",
             bg="#1e293b", border="#38bdf8", title_color="#7dd3fc")

    # Khung CORE 1
    core1_rect = FancyBboxPatch((0.24, 0.10), 0.44, 0.75,
                                boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor="#111827", edgecolor="#22c55e", linewidth=2.2, linestyle="--")
    ax.add_patch(core1_rect)
    ax.text(0.46, 0.825, "ESP32 - CORE 1 (Application CPU)", color="#4ade80",
            fontsize=11.5, fontweight="bold", ha="center")

    # Task đọc data (Core 1)
    draw_box(ax, 0.27, 0.56, 0.38, 0.21,
             "TASK 1: “Task đọc data” (TaskReadData)",
             "• Chạy trên Core 1 (Priority = 2, Chu kỳ = 1000 ms)\n"
             "• Đọc ADC MQ-2 (GPIO 34) & Nhiệt độ DS18B20 (GPIO 4)\n"
             "• Hiển thị dữ liệu qua Serial Monitor (UART0 115200 bps)\n"
             "• Gửi dữ liệu vào “data Queue” và “data Alert”",
             bg="#1e293b", border="#4ade80", title_color="#86efac", sub_size=8.6)

    # Hàng đợi data Alert (Queue)
    draw_box(ax, 0.31, 0.39, 0.30, 0.10,
             "Hàng đợi: “data Alert” (Queue FIFO)",
             "10 phần tử × sizeof(SensorData_t)",
             bg="#312e81", border="#a855f7", title_color="#e9d5ff", sub_size=8.5)

    # Task cảnh báo (Core 1)
    draw_box(ax, 0.27, 0.13, 0.38, 0.20,
             "TASK 2: “Task cảnh báo” (TaskAlertControl)",
             "• Chạy trên Core 1 (Priority = 3 - Ưu tiên cao nhất)\n"
             "• Đọc dữ liệu từ hàng đợi “data Alert”\n"
             "• Gas ≥ 400 ppm → BẬT QUẠT (GPIO 18)\n"
             "• Nhiệt độ ≥ 50 °C → BẬT MÁY BƠM (GPIO 19)",
             bg="#1e293b", border="#ef4444", title_color="#fca5a5", sub_size=8.6)

    # Hàng đợi data Queue (giữa Core 1 và Core 0)
    draw_box(ax, 0.71, 0.60, 0.26, 0.12,
             "Hàng đợi: “data Queue” (Queue FIFO)",
             "Truyền dữ liệu Liên nhân (Core 1 → Core 0)\n10 phần tử × sizeof(SensorData_t)",
             bg="#312e81", border="#facc15", title_color="#fef08a", sub_size=8.3)

    # Khung CORE 0
    core0_rect = FancyBboxPatch((0.71, 0.26), 0.26, 0.29,
                                boxstyle="round,pad=0.01,rounding_size=0.02",
                                facecolor="#111827", edgecolor="#38bdf8", linewidth=2.2, linestyle="--")
    ax.add_patch(core0_rect)
    ax.text(0.84, 0.525, "ESP32 - CORE 0 (Protocol CPU)", color="#38bdf8",
            fontsize=10.5, fontweight="bold", ha="center")

    draw_box(ax, 0.725, 0.28, 0.23, 0.21,
             "TASK 3: “Task truyền data”",
             "• Chạy trên Core 0 (Priority = 2)\n"
             "• Kết nối Wi-Fi (Wokwi-GUEST)\n"
             "• Đọc “data Queue” → Gửi MQTT\n"
             "• Nhận lệnh nút nhấn Manual",
             bg="#1e293b", border="#38bdf8", title_color="#7dd3fc", sub_size=8.4)

    # Cơ cấu chấp hành & Web/App
    draw_box(ax, 0.03, 0.12, 0.17, 0.20,
             "CƠ CẤU CHẤP HÀNH\n& SERIAL MONITOR",
             "• Quạt (Fan): GPIO 18\n• Máy bơm (Pump): GPIO 19\n• Còi báo cháy: GPIO 5",
             bg="#1e293b", border="#f43f5e", title_color="#fda4af", sub_size=8.5)

    draw_box(ax, 0.71, 0.05, 0.26, 0.16,
             "MQTT BROKER & GIAO DIỆN WEB/APP",
             "• 2 thẻ HTML class hiển thị Số (Gas, Nhiệt)\n"
             "• 2 biểu đồ Realtime Chart.js\n"
             "• 2 nút <button> điều khiển Bơm & Quạt",
             bg="#064e3b", border="#10b981", title_color="#6ee7b7", sub_size=8.3)

    # Các mũi tên luồng dữ liệu
    arrow(ax, 0.20, 0.70, 0.27, 0.69, "#f59e0b", "ADC")
    arrow(ax, 0.20, 0.46, 0.27, 0.62, "#38bdf8", "1-Wire")
    arrow(ax, 0.46, 0.56, 0.46, 0.49, "#a855f7", "xQueueSend")
    arrow(ax, 0.46, 0.39, 0.46, 0.33, "#a855f7", "xQueueReceive")
    arrow(ax, 0.65, 0.66, 0.71, 0.66, "#facc15", "xQueueSend")
    arrow(ax, 0.84, 0.60, 0.84, 0.49, "#facc15", "xQueueReceive")
    arrow(ax, 0.27, 0.22, 0.20, 0.22, "#ef4444", "GPIO 18, 19")
    arrow(ax, 0.84, 0.28, 0.84, 0.21, "#10b981", "Publish / Sub MQTT")

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "01_rtos_architecture.png")
    plt.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("Saved:", out_path)


# ==============================================================================
# HÌNH 2: CƠ CHẾ GIAO TIẾP GIỮA CÁC TASK: SEMAPHORE VÀ QUEUE
# ==============================================================================
def make_img2_semaphore_vs_queue():
    fig, ax = plt.subplots(figsize=(14, 7.2), dpi=180)
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.94,
            "CƠ CHẾ GIAO TIẾP VÀ ĐỒNG BỘ GIỮA CÁC TASK TRONG FREERTOS",
            color="#ffffff", fontsize=14, fontweight="bold", ha="center")

    # Nửa trái: QUEUE (Hàng đợi)
    left_bg = FancyBboxPatch((0.03, 0.08), 0.45, 0.80,
                             boxstyle="round,pad=0.01,rounding_size=0.02",
                             facecolor="#131c31", edgecolor="#38bdf8", linewidth=2)
    ax.add_patch(left_bg)
    ax.text(0.255, 0.84, "1. HÀNG ĐỢI (QUEUE - CƠ CHẾ FIFO)", color="#38bdf8",
            fontsize=12, fontweight="bold", ha="center")

    draw_box(ax, 0.06, 0.60, 0.14, 0.15, "Task Đọc Data\n(Producer)",
             "Core 1", bg="#1e293b", border="#4ade80", title_size=9.5)
    draw_box(ax, 0.31, 0.60, 0.14, 0.15, "Task Truyền/Cảnh Báo\n(Consumer)",
             "Core 0 / Core 1", bg="#1e293b", border="#f59e0b", title_size=9.5)

    # Vẽ các ô FIFO ở giữa
    fifo_y = 0.42
    for idx, txt in enumerate(["Mẫu #4", "Mẫu #3", "Mẫu #2", "Mẫu #1"]):
        bx = 0.08 + idx * 0.088
        draw_box(ax, bx, fifo_y, 0.082, 0.10, txt, "SensorData_t",
                 bg="#312e81", border="#a855f7", title_size=8.5, sub_size=7.2, radius=0.01)

    arrow(ax, 0.13, 0.60, 0.13, 0.52, "#4ade80", "xQueueSend()")
    arrow(ax, 0.38, 0.52, 0.38, 0.60, "#f59e0b", "xQueueReceive()")

    queue_notes = (
        "• Nguyên lý: Vào trước - Ra trước (First-In, First-Out).\n"
        "• Truyền dữ liệu thực bằng cách SAO CHÉP GIÁ TRỊ (Copy by Value).\n"
        "• An toàn đa nhân (Thread-safe & Multicore-safe giữa Core 0 & Core 1).\n"
        "• Hỗ trợ cơ chế Chặn (Blocking): Task nhận tự ngủ khi Queue rỗng.\n"
        "• Ứng dụng trong bài Lab: “data Queue” và “data Alert”."
    )
    ax.text(0.06, 0.22, queue_notes, color="#e2e8f0", fontsize=9.2, va="center", linespacing=1.55)

    # Nửa phải: SEMAPHORE & MUTEX (Cờ hiệu)
    right_bg = FancyBboxPatch((0.52, 0.08), 0.45, 0.80,
                              boxstyle="round,pad=0.01,rounding_size=0.02",
                              facecolor="#131c31", edgecolor="#f43f5e", linewidth=2)
    ax.add_patch(right_bg)
    ax.text(0.745, 0.84, "2. CỜ HIỆU (SEMAPHORE & MUTEX)", color="#fda4af",
            fontsize=12, fontweight="bold", ha="center")

    draw_box(ax, 0.55, 0.60, 0.14, 0.15, "MQTT Callback /\nISR Sự kiện",
             "Phát cờ hiệu", bg="#1e293b", border="#38bdf8", title_size=9.5)
    draw_box(ax, 0.80, 0.60, 0.14, 0.15, "Task Cảnh Báo /\nTài nguyên chung",
             "Chờ cờ hiệu / Khóa", bg="#1e293b", border="#ef4444", title_size=9.5)

    draw_box(ax, 0.66, 0.42, 0.17, 0.11, "SEMAPHORE / MUTEX",
             "Token (0 hoặc 1)", bg="#4c1d95", border="#f43f5e", title_size=9.2, sub_size=8)

    arrow(ax, 0.62, 0.60, 0.69, 0.53, "#38bdf8", "xSemaphoreGive()")
    arrow(ax, 0.80, 0.53, 0.86, 0.60, "#ef4444", "xSemaphoreTake()")

    sem_notes = (
        "• Không truyền dữ liệu dung lượng lớn, chỉ truyền TÍN HIỆU / QUYỀN TRUY CẬP.\n"
        "• Binary Semaphore: Đồng bộ sự kiện (đánh thức Task ngay khi có lệnh).\n"
        "• Counting Semaphore: Quản lý tài nguyên có số lượng hữu hạn.\n"
        "• Mutex (Mutual Exclusion): Bảo vệ vùng nhớ dùng chung, có kế thừa ưu tiên.\n"
        "• Ứng dụng trong bài Lab: stateMutex, serialMutex và controlSem."
    )
    ax.text(0.55, 0.22, sem_notes, color="#e2e8f0", fontsize=9.2, va="center", linespacing=1.55)

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "02_semaphore_vs_queue.png")
    plt.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("Saved:", out_path)


# ==============================================================================
# HÌNH 3 & 4: MÔ PHỎNG MẠCH BÁO CHÁY TRÊN WOKWI (BÌNH THƯỜNG & KHI BÁO CHÁY)
# ==============================================================================
def make_wokwi_figure(is_alarm=False):
    fig, ax = plt.subplots(figsize=(14, 8.2), dpi=180)
    fig.patch.set_facecolor("#18181b")
    ax.set_facecolor("#1e1e24")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Thanh tiêu đề Wokwi Simulator
    header = Rectangle((0, 0.92), 1, 0.08, facecolor="#090d16", edgecolor="#334155")
    ax.add_patch(header)
    status_str = "DANG CHAY MO PHONG (BAO DONG CHAY!)" if is_alarm else "DANG CHAY MO PHONG (TRANG THAI AN TOAN)"
    status_col = "#ef4444" if is_alarm else "#22c55e"
    ax.text(0.02, 0.96, "WOKWI SIMULATOR  |  Project: VU_MINH_KHOA_231432270_RTOS_BAO_CHAY",
            color="#ffffff", fontsize=11, fontweight="bold", va="center")
    ax.text(0.98, 0.96, status_str, color=status_col, fontsize=10.5, fontweight="bold", ha="right", va="center")

    # Khu vực vẽ mạch (y từ 0.34 đến 0.90)
    canvas = Rectangle((0.02, 0.34), 0.96, 0.56, facecolor="#27272a", edgecolor="#3f3f46", lw=1.5)
    ax.add_patch(canvas)

    # Cảm biến MQ-2
    gas_val_str = "620 ppm (ADC: 2540) - VUOT NGUONG!" if is_alarm else "245 ppm (ADC: 1003) - An toan"
    mq2_border = "#ef4444" if is_alarm else "#f59e0b"
    draw_box(ax, 0.05, 0.66, 0.22, 0.19,
             "CẢM BIẾN KHÍ GAS MQ-2",
             f"VCC -> 5V | GND -> GND\nAOUT -> GPIO 34 | DOUT -> GPIO 35\nGiá trị: {gas_val_str}",
             bg="#18181b", border=mq2_border, title_color="#fde047", sub_size=8.4)

    # Cảm biến nhiệt DS18B20
    temp_val_str = "64.5 °C - VUOT NGUONG!" if is_alarm else "31.5 °C - An toan"
    temp_border = "#ef4444" if is_alarm else "#38bdf8"
    draw_box(ax, 0.05, 0.39, 0.22, 0.21,
             "CẢM BIẾN NHIỆT DS18B20",
             f"VCC -> 3.3V | GND -> GND\nDQ -> GPIO 4 (Kéo lên R=4.7kΩ)\nNhiệt độ: {temp_val_str}",
             bg="#18181b", border=temp_border, title_color="#7dd3fc", sub_size=8.4)

    # Board ESP32 ở trung tâm
    draw_box(ax, 0.37, 0.40, 0.24, 0.45,
             "ESP32-DevKitC V4\n(Dual-Core FreeRTOS)",
             "• Core 0: TaskTransmitData (Wi-Fi/MQTT)\n"
             "• Core 1: TaskReadData (MQ2, DS18B20)\n"
             "• Core 1: TaskAlertControl (Quạt, Bơm)\n\n"
             "Chân kết nối:\n"
             "  GPIO 34 <-- MQ-2 AOUT\n"
             "  GPIO 4  <-- DS18B20 DQ\n"
             "  GPIO 18 --> QUẠT (FAN)\n"
             "  GPIO 19 --> MÁY BƠM (PUMP)\n"
             "  GPIO 5  --> CÒI BÁO ĐỘNG",
             bg="#0f172a", border="#60a5fa", title_color="#ffffff", sub_size=8.2)

    # Cơ cấu chấp hành bên phải: Quạt (GPIO 18), Máy bơm (GPIO 19), Còi (GPIO 5)
    fan_bg = "#083344" if is_alarm else "#18181b"
    fan_border = "#06b6d4" if is_alarm else "#52525b"
    fan_txt = "TRẠNG THÁI: ĐANG BẬT (HIGH - 3.3V)" if is_alarm else "TRẠNG THÁI: ĐANG TẮT (LOW - 0V)"
    draw_box(ax, 0.70, 0.71, 0.25, 0.15,
             "QUẠT HÚT KHÓI / GAS (GPIO 18)",
             f"Qua R = 220Ω -> LED Xanh / Relay 1\n{fan_txt}",
             bg=fan_bg, border=fan_border, title_color="#67e8f9", sub_size=8.4)

    pump_bg = "#450a0a" if is_alarm else "#18181b"
    pump_border = "#ef4444" if is_alarm else "#52525b"
    pump_txt = "TRẠNG THÁI: ĐANG BẬT (HIGH - 3.3V)" if is_alarm else "TRẠNG THÁI: ĐANG TẮT (LOW - 0V)"
    draw_box(ax, 0.70, 0.53, 0.25, 0.15,
             "MÁY BƠM CHỮA CHÁY (GPIO 19)",
             f"Qua R = 220Ω -> LED Đỏ / Relay 2\n{pump_txt}",
             bg=pump_bg, border=pump_border, title_color="#fca5a5", sub_size=8.4)

    bz_bg = "#3b0764" if is_alarm else "#18181b"
    bz_border = "#c084fc" if is_alarm else "#52525b"
    bz_txt = "CÒI ĐANG KÊU BÁO ĐỘNG (2000 Hz)" if is_alarm else "CÒI TẮT (Bình thường)"
    draw_box(ax, 0.70, 0.36, 0.25, 0.14,
             "CÒI BÁO CHÁY BUZZER (GPIO 5)",
             bz_txt,
             bg=bz_bg, border=bz_border, title_color="#e9d5ff", sub_size=8.4)

    # Đường dây nối
    arrow(ax, 0.27, 0.75, 0.37, 0.70, "#f59e0b", "GPIO 34 (Analog)")
    arrow(ax, 0.27, 0.49, 0.37, 0.54, "#38bdf8", "GPIO 4 (1-Wire)")
    arrow(ax, 0.61, 0.76, 0.70, 0.78, "#06b6d4", "GPIO 18")
    arrow(ax, 0.61, 0.60, 0.70, 0.60, "#ef4444", "GPIO 19")
    arrow(ax, 0.61, 0.45, 0.70, 0.43, "#c084fc", "GPIO 5")

    # Khu vực Serial Monitor ở dưới (y từ 0.02 đến 0.32)
    serial_box = Rectangle((0.02, 0.02), 0.96, 0.30, facecolor="#090d16", edgecolor="#334155", lw=1.5)
    ax.add_patch(serial_box)
    ax.text(0.035, 0.29, "SERIAL MONITOR (115200 baud) - Kết quả hoạt động đa nhiệm FreeRTOS trên ESP32:",
            color="#38bdf8", fontsize=9.8, fontweight="bold")

    if not is_alarm:
        serial_lines = [
            "[RTOS] Da khoi tao thanh cong 3 Task va 2 Queue (data Queue, data Alert)!",
            "[TaskTransmitData - Core 0] WiFi da ket noi! IP: 10.10.0.2 | MQTT Broker connected (broker.emqx.io)",
            "[TaskReadData - Core 1] Mau #12 | Gas MQ-2: 245.0 ppm (ADC: 1003, 24.5%) | Nhiet do: 31.5 C",
            "[TaskAlertControl - Core 1] Che do: AUTO | Canh bao Gas: An toan | Canh bao Nhiet: An toan => QUAT: TAT (OFF) | MAY BOM: TAT (OFF)",
            "[TaskTransmitData - Core 0] Da gui MQTT Telemetry: {\"sampleId\":12,\"gasAdc\":1003,\"gas\":245.0,\"temperature\":31.5,\"fan\":false,\"pump\":false}",
        ]
        line_color = "#86efac"
    else:
        serial_lines = [
            "[TaskReadData - Core 1] Mau #28 | Gas MQ-2: 620.0 ppm (ADC: 2540, 62.0%) | Nhiet do: 64.5 C",
            "[TaskAlertControl - Core 1] Che do: AUTO | Canh bao Gas: NGUY HIEM! | Canh bao Nhiet: NGUY HIEM! => QUAT: BAT (ON) | MAY BOM: BAT (ON)",
            "[TaskTransmitData - Core 0] Da gui MQTT Telemetry: {\"sampleId\":28,\"gasAdc\":2540,\"gas\":620.0,\"temperature\":64.5,\"fan\":true,\"pump\":true}",
            "[MQTT-RX] Nhan lenh Web: cmd=setPump | Mode=MANUAL | Quat=ON | MayBom=ON",
            "[TaskTransmitData - Core 0] Dong bo trang thai co cau chap hanh len Web Dashboard thanh cong!",
        ]
        line_color = "#fca5a5"

    for i, line in enumerate(serial_lines):
        ax.text(0.035, 0.24 - i * 0.045, line, color=line_color,
                fontsize=8.6, fontfamily="monospace")

    plt.tight_layout()
    fname = "04_wokwi_circuit_alarm.png" if is_alarm else "03_wokwi_circuit_normal.png"
    out_path = os.path.join(OUT_DIR, fname)
    plt.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("Saved:", out_path)


# ==============================================================================
# HÌNH 5 & 6: GIAO DIỆN WEB/APP (BÌNH THƯỜNG & CẢNH BÁO / MANUAL)
# ==============================================================================
def make_web_dashboard_figure(is_alarm=False):
    fig = plt.figure(figsize=(14, 8.6), dpi=180)
    fig.patch.set_facecolor("#0f172a")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Header bar
    draw_box(ax, 0.03, 0.90, 0.94, 0.075,
             "HỆ THỐNG BÁO CHÁY GIA ĐÌNH (ESP32 FREERTOS & MQTT WEB DASHBOARD)",
             "Sinh viên: Vũ Minh Khoa | MSV: 231432270 | MQTT Broker: broker.emqx.io (Đã kết nối)",
             bg="#1e293b", border="#334155", title_size=11.5, sub_size=8.8)

    # 2 Thẻ HTML class hiển thị dữ liệu số (Gas & Nhiệt độ)
    if not is_alarm:
        gas_num, temp_num = "245.0 ppm", "31.5 °C"
        gas_sub = "Thẻ HTML: class='sensor-card gas-card' | ADC: 1003/4095 | Trạng thái: BÌNH THƯỜNG"
        temp_sub = "Thẻ HTML: class='sensor-card temp-card' | GPIO 4 (1-Wire) | Trạng thái: BÌNH THƯỜNG"
        c_border_g, c_border_t = "#f59e0b", "#38bdf8"
    else:
        gas_num, temp_num = "620.0 ppm", "64.5 °C"
        gas_sub = "Thẻ HTML: class='sensor-card gas-card' | ADC: 2540/4095 | CẢNH BÁO RÒ KHÍ GAS (≥ 400 ppm)!"
        temp_sub = "Thẻ HTML: class='sensor-card temp-card' | GPIO 4 (1-Wire) | CẢNH BÁO NHIỆT ĐỘ CAO (≥ 50 °C)!"
        c_border_g, c_border_t = "#ef4444", "#ef4444"

    draw_box(ax, 0.03, 0.72, 0.455, 0.16,
             f"NỒNG ĐỘ KHÍ GAS / KHÓI (MQ-2):  {gas_num}",
             gas_sub, bg="#1e293b", border=c_border_g, title_color="#fde047", title_size=12, sub_size=8.5)

    draw_box(ax, 0.515, 0.72, 0.455, 0.16,
             f"NHIỆT ĐỘ PHÒNG (DS18B20):  {temp_num}",
             temp_sub, bg="#1e293b", border=c_border_t, title_color="#7dd3fc", title_size=12, sub_size=8.5)

    # 2 Biểu đồ thời gian thực (Chart.js)
    ax_g = fig.add_axes([0.06, 0.38, 0.41, 0.28], facecolor="#131c31")
    ax_t = fig.add_axes([0.545, 0.38, 0.41, 0.28], facecolor="#131c31")

    t_steps = ["10:01", "10:02", "10:03", "10:04", "10:05", "10:06", "10:07", "10:08"]
    if not is_alarm:
        g_vals = [220, 228, 235, 240, 238, 242, 246, 245]
        t_vals = [30.5, 30.8, 31.0, 31.2, 31.3, 31.4, 31.5, 31.5]
    else:
        g_vals = [235, 250, 310, 420, 510, 560, 605, 620]
        t_vals = [31.2, 33.0, 38.5, 46.0, 52.5, 58.0, 62.0, 64.5]

    ax_g.plot(t_steps, g_vals, marker="o", color="#f59e0b", lw=2.4, label="Nồng độ Gas (ppm)")
    ax_g.axhline(400, color="#ef4444", linestyle="--", lw=1.5, label="Ngưỡng bật Quạt (400 ppm)")
    ax_g.set_ylim(0, 800)
    ax_g.set_title("Biểu đồ Thời gian thực: Nồng độ Khí Gas (ppm)", color="#ffffff", fontsize=10, fontweight="bold")
    ax_g.tick_params(colors="#cbd5e1", labelsize=8)
    ax_g.grid(True, color="#334155", alpha=0.4)
    ax_g.legend(loc="upper left", fontsize=8, facecolor="#1e293b", labelcolor="#ffffff")

    ax_t.plot(t_steps, t_vals, marker="s", color="#38bdf8", lw=2.4, label="Nhiệt độ (°C)")
    ax_t.axhline(50, color="#ef4444", linestyle="--", lw=1.5, label="Ngưỡng bật Bơm (50 °C)")
    ax_t.set_ylim(20, 80)
    ax_t.set_title("Biểu đồ Thời gian thực: Nhiệt độ Môi trường (°C)", color="#ffffff", fontsize=10, fontweight="bold")
    ax_t.tick_params(colors="#cbd5e1", labelsize=8)
    ax_t.grid(True, color="#334155", alpha=0.4)
    ax_t.legend(loc="upper left", fontsize=8, facecolor="#1e293b", labelcolor="#ffffff")

    # Khu vực dưới: 2 Nút <button> điều khiển Máy bơm & Quạt (Chế độ Manual)
    mode_str = "CHẾ ĐỘ ĐIỀU KHIỂN: MANUAL (ĐIỀU KHIỂN BẰNG 2 NÚT BUTTON TRÊN WEB)" if is_alarm else "CHẾ ĐỘ ĐIỀU KHIỂN: AUTO (TỰ ĐỘNG THEO TASK CẢNH BÁO RTOS)"
    draw_box(ax, 0.03, 0.04, 0.94, 0.27, "", "", bg="#1e293b", border="#475569")
    ax.text(0.5, 0.275, mode_str, color="#38bdf8", fontsize=10.5, fontweight="bold", ha="center")

    fan_btn_txt = "NÚT <button> QUẠT (GPIO 18): ĐANG BẬT (ON) - Nhấn để Tắt" if is_alarm else "NÚT <button> QUẠT (GPIO 18): ĐANG TẮT (OFF) - Nhấn để Bật (Manual)"
    pump_btn_txt = "NÚT <button> MÁY BƠM (GPIO 19): ĐANG BẬT (ON) - Nhấn để Tắt" if is_alarm else "NÚT <button> MÁY BƠM (GPIO 19): ĐANG TẮT (OFF) - Nhấn để Bật (Manual)"

    draw_box(ax, 0.06, 0.07, 0.41, 0.16,
             "CƠ CẤU CHẤP HÀNH 1: QUẠT HÚT KHÍ GAS (FAN)",
             fan_btn_txt + "\nMQTT Topic: fire_alarm_vmk_231432270/control -> {\"cmd\":\"setFan\",\"state\":true}",
             bg="#083344" if is_alarm else "#0f172a",
             border="#06b6d4", title_color="#67e8f9", title_size=10, sub_size=8.3)

    draw_box(ax, 0.53, 0.07, 0.41, 0.16,
             "CƠ CẤU CHẤP HÀNH 2: MÁY BƠM CHỮA CHÁY (PUMP)",
             pump_btn_txt + "\nMQTT Topic: fire_alarm_vmk_231432270/control -> {\"cmd\":\"setPump\",\"state\":true}",
             bg="#450a0a" if is_alarm else "#0f172a",
             border="#ef4444", title_color="#fca5a5", title_size=10, sub_size=8.3)

    fname = "06_web_dashboard_manual.png" if is_alarm else "05_web_dashboard_normal.png"
    out_path = os.path.join(OUT_DIR, fname)
    plt.savefig(out_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("Saved:", out_path)


if __name__ == "__main__":
    make_img1_rtos_architecture()
    make_img2_semaphore_vs_queue()
    make_wokwi_figure(is_alarm=False)
    make_wokwi_figure(is_alarm=True)
    make_web_dashboard_figure(is_alarm=False)
    make_web_dashboard_figure(is_alarm=True)
    print("ALL 6 IMAGES GENERATED SUCCESSFULLY!")
