# -*- coding: utf-8 -*-
"""
Script tạo Báo cáo Word (.docx) đầy đủ, chi tiết cho Bài Lab Hệ Thống Nhúng:
"Thiết kế Mạch báo cháy gia đình sử dụng ESP32, FreeRTOS (Dual-Core), MQTT và Giao diện Web/App"
Sinh viên: Vũ Minh Khoa - MSV: 231432270 - Lớp: Điện Tử và Tin Học Công Nghiệp 1 - K64
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = r"d:\KI 1 NAM 4\HỆ THỐNG NHÚNG\Lab_RTOS_BaoChay"
IMG_DIR  = os.path.join(BASE_DIR, "images")
SKETCH_PATH = os.path.join(BASE_DIR, "wokwi_esp32_rtos_baochay", "sketch.ino")
DIAGRAM_PATH = os.path.join(BASE_DIR, "wokwi_esp32_rtos_baochay", "diagram.json")
HTML_PATH = os.path.join(BASE_DIR, "web_dashboard", "index.html")


def set_cell_shading(cell, fill_hex="D9EAF7"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def format_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


def add_styled_table(doc, headers, rows, header_fill="1F4E79", header_text_white=True):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        format_run_font(
            r, size=11, bold=True,
            color=RGBColor(255, 255, 255) if header_text_white else RGBColor(0, 0, 0)
        )
        set_cell_shading(hdr_cells[i], header_fill)
        hdr_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    for r_idx, row_data in enumerate(rows):
        cells = table.add_row().cells
        bg = "F2F7FB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cells[c_idx].text = ""
            p = cells[c_idx].paragraphs[0]
            r = p.add_run(str(val))
            format_run_font(r, size=11, bold=(c_idx == 0))
            set_cell_shading(cells[c_idx], bg)
            cells[c_idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    doc.add_paragraph()
    return table


def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    set_cell_shading(cell, "F8FAFC")
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.08
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(code_text.strip())
    format_run_font(r, name="Consolas", size=9.2)
    doc.add_paragraph()


def add_figure(doc, img_filename, caption_text, width_inches=6.2):
    img_path = os.path.join(IMG_DIR, img_filename)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(img_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run(caption_text)
        format_run_font(r_cap, size=11, bold=True, italic=True, color=RGBColor(31, 78, 121))


def add_bullet(doc, bold_prefix, text):
    p = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        r1 = p.add_run(bold_prefix)
        format_run_font(r1, size=12, bold=True)
    r2 = p.add_run(text)
    format_run_font(r2, size=12, bold=False)
    return p


def build_report():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)
    sec.left_margin = Inches(0.95)
    sec.right_margin = Inches(0.8)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    styles["Normal"].font.size = Pt(12)
    styles["Normal"].paragraph_format.line_spacing = 1.25
    styles["Normal"].paragraph_format.space_after = Pt(6)

    for level, sz, col in [
        ("Heading 1", 15, RGBColor(31, 78, 121)),
        ("Heading 2", 13, RGBColor(46, 117, 182)),
        ("Heading 3", 12, RGBColor(31, 78, 121)),
    ]:
        styles[level].font.name = "Times New Roman"
        styles[level]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        styles[level].font.size = Pt(sz)
        styles[level].font.bold = True
        styles[level].font.color.rgb = col

    # ==================== TRANG THÔNG TIN SINH VIÊN & ĐỀ BÀI ====================
    for line, bold in [
        ("Họ và tên: Vũ Minh Khoa", True),
        ("Mã sinh viên: 231432270", True),
        ("Lớp: Điện Tử và Tin Học Công Nghiệp 1 - K64", True),
        ("Học phần: Hệ thống Nhúng", True),
        ("Đề tài: Thiết kế Mạch báo cháy gia đình sử dụng ESP32, FreeRTOS và MQTT", True),
    ]:
        p = doc.add_paragraph()
        r = p.add_run(line)
        format_run_font(r, size=12.5, bold=bold)

    doc.add_heading("1. ĐỀ BÀI VÀ YÊU CẦU THỰC HIỆN", level=1)
    doc.add_paragraph(
        "Thiết kế Mạch báo cháy gia đình bằng việc phát hiện khí gas/khói và nhiệt độ. "
        "Mạch báo cháy sử dụng ESP32 đọc dữ liệu nồng độ khí gas/khói từ cảm biến MQ2 và "
        "nhiệt độ từ cảm biến nhiệt, hiển thị dữ liệu qua giao tiếp serial. Đồng thời ESP32 "
        "gửi dữ liệu lên MQTT Broker qua Wifi và hiển thị dữ liệu trên Web/App. Yêu cầu thực hiện:"
    )
    add_bullet(doc, "• Vẽ mạch kết nối trong Wokwi: ",
               "Kết nối vi điều khiển ESP32 với cảm biến khí gas/khói MQ-2, cảm biến nhiệt độ DS18B20 và cơ cấu chấp hành (Quạt, Máy bơm, Còi báo cháy).")
    add_bullet(doc, "• Thiết kế giao diện trên Web/App: ",
               "Đọc dữ liệu từ MQTT Broker hiển thị trên thẻ HTML có thuộc tính 'class' và nút 'button' để điều khiển cơ cấu chấp hành, bao gồm: "
               "(1) 2 thẻ HTML hiển thị dữ liệu Nồng độ khí gas và Nhiệt độ dạng số; "
               "(2) 2 biểu đồ cập nhật dữ liệu Nồng độ khí gas và Nhiệt độ trực tiếp theo thời gian thực; "
               "(3) 2 nút button để điều khiển trạng thái Máy bơm và Quạt ở chế độ Manual.")
    add_bullet(doc, "• Xây dựng hệ RTOS cho hoạt động của ESP32: ",
               "Phân tách chương trình thành 3 Task chạy song song trên 2 nhân (Core 0 và Core 1) của ESP32: "
               "(1) 'Task truyền data' chạy Core 0 kết nối Wi-Fi, đọc dữ liệu từ hàng đợi 'data Queue' và gửi lên MQTT Broker; "
               "(2) 'Task đọc data' chạy Core 1 đọc dữ liệu MQ-2 và cảm biến nhiệt, hiển thị qua Serial, gửi dữ liệu đầy đủ vào hàng đợi 'data Queue' và hàng đợi 'data Alert'; "
               "(3) 'Task cảnh báo' chạy Core 1 đọc dữ liệu từ hàng đợi 'data Alert' và điều khiển Quạt (bật khi khí gas vượt ngưỡng) và Máy bơm (bật khi nhiệt độ vượt ngưỡng).")

    # ==================== PHẦN 2: LÝ THUYẾT RTOS & FREERTOS ====================
    doc.add_heading("2. GIỚI THIỆU VỀ RTOS VÀ ƯU / NHƯỢC ĐIỂM CỦA FREERTOS", level=1)

    doc.add_heading("2.1. Tổng quan và các ưu điểm nổi bật của Hệ điều hành thời gian thực (RTOS)", level=2)
    doc.add_paragraph(
        "Hệ điều hành thời gian thực (Real-Time Operating System - RTOS) là hệ điều hành chuyên dụng "
        "cho các hệ thống nhúng, được thiết kế để đảm bảo các tác vụ (Tasks) được thực thi trong một "
        "khoảng thời gian xác định trước (Deterministic Timing). Khác với mô hình lập trình tuần tự "
        "truyền thống (Super-Loop dùng vòng lặp while(1) hoặc loop() với delay()), RTOS sở hữu bộ lập lịch "
        "(Scheduler) cho phép chia nhỏ bài toán phức tạp thành nhiều Task độc lập chạy song song."
    )
    add_bullet(doc, "1. Tính tiền định và phản hồi thời gian thực (Determinism & Responsiveness): ",
               "Trong mạch báo cháy, tác vụ phát hiện vượt ngưỡng và kích hoạt Quạt/Máy bơm ('Task cảnh báo') "
               "cần được phản hồi ngay lập tức. Với cơ chế lập lịch ưu tiên có trưng dụng (Preemptive Priority Scheduling), "
               "ngay khi có dữ liệu nguy hiểm trong hàng đợi 'data Alert', bộ lập lịch RTOS sẽ lập tức chuyển ngữ cảnh "
               "(Context Switch) sang Task cảnh báo mà không bị chặn bởi quá trình chờ mạng Wi-Fi hay MQTT.")
    add_bullet(doc, "2. Khai thác tối đa kiến trúc Đa nhân (Multicore SMP) trên ESP32: ",
               "Vi điều khiển ESP32 tích hợp 2 nhân xử lý Xtensa LX6 32-bit (Core 0 - Protocol CPU và Core 1 - Application CPU). "
               "RTOS cho phép ghim (pin) các tác vụ mạng tốn thời gian chờ I/O ('Task truyền data') vào Core 0, "
               "trong khi ghim các tác vụ đo lường và điều khiển thời gian thực ('Task đọc data', 'Task cảnh báo') vào Core 1.")
    add_bullet(doc, "3. Tính mô-đun hóa cao và dễ bảo trì, mở rộng (Modularity & Scalability): ",
               "Mỗi Task đảm nhận một chức năng rõ ràng với vùng nhớ ngăn xếp (Stack) riêng biệt. Khi cần nâng cấp "
               "giao thức truyền thông hoặc thêm cảm biến mới, lập trình viên chỉ cần chỉnh sửa Task tương ứng mà không "
               "làm xáo trộn thời gian thực thi của các Task còn lại.")
    add_bullet(doc, "4. Sử dụng hiệu quả tài nguyên CPU và năng lượng: ",
               "Thay vì dùng vòng lặp bận (Busy-waiting) gây lãng phí chu kỳ máy, các hàm API của RTOS như "
               "vTaskDelayUntil(), xQueueReceive() sẽ đưa Task đang chờ về trạng thái Blocked, nhường hoàn toàn CPU cho các Task khác.")

    doc.add_heading("2.2. Giới thiệu về FreeRTOS và phân tích Ưu điểm / Nhược điểm", level=2)
    doc.add_paragraph(
        "FreeRTOS là hệ điều hành thời gian thực mã nguồn mở phổ biến nhất thế giới dành cho vi điều khiển "
        "(do Richard Barry sáng lập và hiện được Amazon Web Services - AWS bảo trợ). Trên ESP32, hãng Espressif "
        "đã tích hợp sẵn phiên bản ESP-IDF FreeRTOS hỗ trợ xử lý đa đối xứng (Symmetric Multiprocessing - SMP) "
        "trên cả hai nhân Core 0 và Core 1."
    )

    add_styled_table(
        doc,
        ["Tiêu chí", "Ưu điểm của FreeRTOS", "Nhược điểm / Thách thức của FreeRTOS"],
        [
            ("Dung lượng & Chi phí",
             "Mã nguồn mở hoàn toàn miễn phí (giấy phép MIT). Nhân (Kernel) cực kỳ gọn nhẹ, chỉ chiếm khoảng 6 KB – 12 KB ROM và vài trăm byte RAM.",
             "Không cung cấp sẵn các dịch vụ cấp cao phức tạp (như hệ thống quản lý file đầy đủ, giao diện đồ họa, bảo mật cấp OS) nếu không cài thêm thư viện ngoài."),
            ("Hiệu năng & Đa nhiệm",
             "Hỗ trợ lập lịch Preemptive (ưu tiên trưng dụng), Time-slicing (chia sẻ lát cắt thời gian) và hỗ trợ chạy đa nhân SMP trên ESP32 với hàm xTaskCreatePinnedToCore().",
             "Chi phí chuyển ngữ cảnh (Context Switching Overhead) và quản lý Tick Timer tiêu tốn một phần nhỏ chu kỳ CPU so với chương trình Bare-metal đơn giản."),
            ("Cơ chế giao tiếp & Đồng bộ",
             "Cung cấp đầy đủ các đối tượng IPC chuẩn: Queue (Hàng đợi), Binary/Counting Semaphore, Mutex (có kế thừa ưu tiên Priority Inheritance), Event Groups, Task Notifications.",
             "Đòi hỏi người lập trình phải nắm vững tư duy lập trình song song; nếu thiết kế sai dễ gặp các lỗi kinh điển như Deadlock (khóa chết), Race Condition (tranh chấp dữ liệu) hoặc Priority Inversion."),
            ("Quản lý bộ nhớ",
             "Cung cấp 5 mô hình cấp phát Heap linh hoạt (heap_1 đến heap_5) và tích hợp trực tiếp vào bộ nhớ SRAM của ESP32.",
             "Mỗi Task cần cấp phát sẵn một vùng Stack cố định (ví dụ 4096 hoặc 8192 bytes). Nếu tính toán quá nhỏ sẽ gây lỗi Stack Overflow làm treo chip; nếu cấp quá lớn sẽ gây lãng phí RAM."),
        ]
    )

    # ==================== PHẦN 3: SEMAPHORE VÀ QUEUE ====================
    doc.add_heading("3. CƠ CHẾ GIAO TIẾP GIỮA CÁC TASK: CỜ HIỆU (SEMAPHORE) VÀ HÀNG ĐỢI (QUEUE)", level=1)
    doc.add_paragraph(
        "Trong hệ thống đa nhiệm FreeRTOS, các Task hoạt động độc lập nhưng cần trao đổi dữ liệu "
        "và đồng bộ hóa thứ tự thực thi. Việc sử dụng biến toàn cục thông thường giữa các Task chạy trên "
        "hai nhân khác nhau (Core 0 và Core 1) rất dễ dẫn đến hiện tượng xung đột dữ liệu (Race Condition) "
        "khi một Task đang ghi dở thì Task khác nhảy vào đọc. Do đó, FreeRTOS cung cấp hai cơ chế cốt lõi "
        "là Cờ hiệu (Semaphore) và Hàng đợi (Queue)."
    )

    doc.add_heading("3.1. Cơ chế Cờ hiệu (Semaphore & Mutex)", level=2)
    doc.add_paragraph(
        "Semaphore (Cờ hiệu) là một cơ chế báo hiệu và đồng bộ hóa giữa các Task hoặc giữa Ngắt (ISR) với Task, "
        "hoạt động dựa trên một biến đếm nguyên (Token) mà không dùng để truyền tải gói dữ liệu lớn. "
        "Hai thao tác cơ bản trên Semaphore là Take (Lấy cờ - xSemaphoreTake) và Give (Trả/Phát cờ - xSemaphoreGive)."
    )
    add_bullet(doc, "• Binary Semaphore (Cờ hiệu nhị phân): ",
               "Chỉ có hai giá trị 0 (trống) và 1 (có sẵn). Thường dùng để đồng bộ hóa sự kiện: Task xử lý gọi "
               "xSemaphoreTake() và ngủ chờ; khi có sự kiện (ví dụ nhận lệnh điều khiển Manual từ Web qua MQTT), "
               "hàm Callback gọi xSemaphoreGive(controlSem) để đánh thức Task cảnh báo dậy xử lý tức thời.")
    add_bullet(doc, "• Counting Semaphore (Cờ hiệu đếm): ",
               "Có giá trị đếm từ 0 đến N, dùng để đếm số lượng sự kiện phát sinh hoặc quản lý một nhóm tài nguyên có số lượng giới hạn.")
    add_bullet(doc, "• Mutex (Mutual Exclusion - Loại trừ tương hỗ): ",
               "Là loại Semaphore đặc biệt dùng để bảo vệ tài nguyên dùng chung (như cổng giao tiếp Serial hoặc cấu trúc trạng thái sysState). "
               "Task nào muốn truy cập tài nguyên phải 'khóa' Mutex (Take) và 'mở khóa' (Give) ngay sau khi xong. "
               "Đặc biệt, Mutex trong FreeRTOS có cơ chế Kế thừa mức ưu tiên (Priority Inheritance) giúp ngăn chặn triệt để lỗi Đảo ngược độ ưu tiên (Priority Inversion).")

    doc.add_heading("3.2. Cơ chế Hàng đợi (Queue)", level=2)
    doc.add_paragraph(
        "Queue (Hàng đợi) là cơ chế chính để truyền dữ liệu thực sự giữa các Task trong FreeRTOS. "
        "Queue hoạt động theo cấu trúc FIFO (First-In, First-Out: Dữ liệu vào trước được lấy ra trước) "
        "với kích thước phần tử và độ dài hàng đợi được xác định khi khởi tạo bằng hàm xQueueCreate(uxQueueLength, uxItemSize)."
    )
    add_bullet(doc, "• Truyền dữ liệu theo giá trị (Copy by Value): ",
               "Khi Task gọi xQueueSend(), FreeRTOS sao chép toàn bộ nội dung biến cấu trúc (ví dụ SensorData_t) "
               "vào bộ nhớ đệm nội bộ của Queue. Nhờ đó, Task gửi có thể tái sử dụng hoặc hủy biến cục bộ ngay lập tức mà không sợ làm hỏng dữ liệu của Task nhận.")
    add_bullet(doc, "• An toàn tuyệt đối giữa nhiều Task và nhiều Core (Thread-safe & Multicore-safe): ",
               "FreeRTOS tự động sử dụng các khóa spinlock phần cứng bên trong Queue, cho phép 'Task đọc data' ở Core 1 "
               "gửi dữ liệu sang 'Task truyền data' ở Core 0 qua 'data Queue' một cách an toàn tuyệt đối.")
    add_bullet(doc, "• Cơ chế Chặn thông minh (Blocking Read / Write): ",
               "Khi 'Task cảnh báo' gọi xQueueReceive(dataAlertQueue, &alertData, portMAX_DELAY), nếu hàng đợi đang rỗng, "
               "Task sẽ tự động chuyển sang trạng thái Blocked (không tốn 0% CPU nào) và lập tức thức dậy ngay ở micro-giây "
               "mà 'Task đọc data' đẩy mẫu cảm biến mới vào hàng đợi.")

    add_figure(doc, "02_semaphore_vs_queue.png",
               "Hình 1. Sơ đồ nguyên lý hoạt động và ứng dụng của Hàng đợi (Queue) và Cờ hiệu (Semaphore/Mutex) trong bài Lab.")

    add_styled_table(
        doc,
        ["Đặc điểm so sánh", "Hàng đợi (Queue)", "Cờ hiệu (Semaphore / Mutex)"],
        [
            ("Mục đích chính", "Truyền tải dữ liệu (biến, mảng, struct) giữa các Task.", "Đồng bộ hóa sự kiện hoặc bảo vệ tài nguyên dùng chung."),
            ("Dữ liệu mang theo", "Sao chép toàn bộ gói dữ liệu (Copy by Value).", "Không chứa dữ liệu, chỉ lưu trạng thái/biến đếm Token."),
            ("Hàm API trong FreeRTOS", "xQueueCreate(), xQueueSend(), xQueueReceive()", "xSemaphoreCreateBinary(), xSemaphoreCreateMutex(), xSemaphoreTake(), xSemaphoreGive()"),
            ("Ứng dụng thực tế trong bài Lab",
             "1. 'data Queue': Truyền SensorData_t từ Task đọc data (Core 1) sang Task truyền data (Core 0).\n"
             "2. 'data Alert': Truyền SensorData_t từ Task đọc data (Core 1) sang Task cảnh báo (Core 1).",
             "1. 'stateMutex': Bảo vệ cấu trúc trạng thái Quạt/Bơm/Chế độ (sysState).\n"
             "2. 'serialMutex': Tránh xung đột khi Core 0 và Core 1 cùng in Serial.\n"
             "3. 'controlSem': Đánh thức Task cảnh báo khi bấm nút Manual trên Web."),
        ]
    )

    # ==================== PHẦN 4: CÁC BƯỚC THỰC HIỆN BÀI LAB ====================
    doc.add_heading("4. TRÌNH BÀY CÁC BƯỚC THỰC HIỆN BÀI LAB", level=1)

    doc.add_heading("4.1. Sơ đồ mạch trong Wokwi và Bảng kết nối chân phần cứng", level=2)
    doc.add_paragraph(
        "Mạch mô phỏng trên Wokwi sử dụng vi điều khiển trung tâm ESP32-DevKitC V4 kết nối với "
        "cảm biến khí gas/khói MQ-2, cảm biến nhiệt độ số DS18B20 và các cơ cấu chấp hành gồm Quạt hút khói/gas "
        "(mô phỏng bằng LED Xanh công suất / ngõ ra Relay tại GPIO 18), Máy bơm nước chữa cháy "
        "(mô phỏng bằng LED Đỏ công suất / ngõ ra Relay tại GPIO 19) và Còi báo cháy Buzzer (GPIO 5)."
    )

    add_styled_table(
        doc,
        ["Thiết bị / Cảm biến", "Thông số kỹ thuật & Giới hạn đo", "Đơn vị đo", "Chân kết nối ESP32", "Chức năng trong hệ thống"],
        [
            ("Cảm biến khí Gas/Khói MQ-2",
             "Đọc giá trị tương tự qua bộ ADC 12-bit của ESP32 (0 – 4095), quy đổi dải nồng độ 0 – 1000 ppm (ngưỡng cảnh báo ≥ 400 ppm).",
             "ppm (và %)",
             "VCC → 5V\nGND → GND\nAOUT → GPIO 34\nDOUT → GPIO 35",
             "Phát hiện rò rỉ khí gas (LPG, প্রোপan, metan) và khói đám cháy."),
            ("Cảm biến nhiệt độ DS18B20",
             "Cảm biến nhiệt độ số chuẩn giao tiếp 1-Wire, dải đo từ -55 °C đến +125 °C, sai số ±0.5 °C (ngưỡng cảnh báo ≥ 50 °C).",
             "°C (Độ C)",
             "VCC → 3V3\nGND → GND\nDQ → GPIO 4 (kèm R kéo lên 4.7 kΩ)",
             "Đo nhiệt độ môi trường phòng theo thời gian thực để phát hiện đám cháy."),
            ("Cơ cấu chấp hành 1: Quạt (Fan)",
             "Ngõ ra số Digital Output (mức HIGH = 3.3V kích dẫn Relay / sáng LED Xanh qua trở 220 Ω).",
             "Trạng thái BẬT (1) / TẮT (0)",
             "GPIO 18 → Anode LED Xanh (Relay Quạt)",
             "Tự động BẬT khi nồng độ khí gas vượt ngưỡng (≥ 400 ppm) hoặc điều khiển bằng nút nhấn Web."),
            ("Cơ cấu chấp hành 2: Máy bơm (Pump)",
             "Ngõ ra số Digital Output (mức HIGH = 3.3V kích dẫn Relay / sáng LED Đỏ qua trở 220 Ω).",
             "Trạng thái BẬT (1) / TẮT (0)",
             "GPIO 19 → Anode LED Đỏ (Relay Bơm)",
             "Tự động BẬT khi nhiệt độ vượt ngưỡng (≥ 50 °C) hoặc điều khiển bằng nút nhấn Web."),
            ("Còi báo động (Buzzer)",
             "Ngõ ra xung PWM âm thanh tần số 2000 Hz khi có cảnh báo.",
             "Hz / ON-OFF",
             "GPIO 5 → Buzzer (+)",
             "Phát âm thanh cảnh báo tại chỗ khi phát hiện khí gas hoặc nhiệt độ vượt ngưỡng."),
        ]
    )

    add_figure(doc, "03_wokwi_circuit_normal.png",
               "Hình 2. Sơ đồ mạch kết nối ESP32, cảm biến MQ-2, DS18B20 và cơ cấu chấp hành Quạt, Máy bơm trong Wokwi.")

    doc.add_heading("4.2. Triển khai FreeRTOS trên ESP32 và Bảng dữ liệu cho các Task", level=2)
    doc.add_paragraph(
        "Hệ thống phần mềm trên ESP32 được thiết kế theo đúng kiến trúc RTOS yêu cầu của đề bài, "
        "phân bổ tường minh trên 2 nhân vật lý của ESP32 thông qua hàm xTaskCreatePinnedToCore():"
    )
    add_figure(doc, "01_rtos_architecture.png",
               "Hình 3. Sơ đồ kiến trúc đa nhiệm FreeRTOS trên 2 nhân (Core 0 & Core 1) và luồng dữ liệu qua 2 hàng đợi 'data Queue' và 'data Alert'.")

    doc.add_paragraph("Bảng 1 dưới đây trình bày chi tiết thông số thiết kế của 3 Task trong hệ thống FreeRTOS:")
    add_styled_table(
        doc,
        ["Tên Task theo đề bài", "Tên hàm trong Code", "Core thực thi", "Độ ưu tiên (Priority)", "Kích thước Stack", "Hàng đợi giao tiếp & Nhiệm vụ chi tiết"],
        [
            ("Task truyền data",
             "TaskTransmitData",
             "Core 0\n(Protocol CPU)",
             "2",
             "8192 bytes",
             "• Kết nối Wi-Fi (Wokwi-GUEST) và kết nối MQTT Broker (broker.emqx.io).\n"
             "• Nếu kết nối thành công, đọc dữ liệu từ hàng đợi 'data Queue' (xQueueReceive) và đóng gói JSON gửi lên topic telemetry.\n"
             "• Nhận lệnh điều khiển từ 2 nút button trên Web qua topic control."),
            ("Task đọc data",
             "TaskReadData",
             "Core 1\n(App CPU)",
             "2",
             "4096 bytes",
             "• Chu kỳ 1000 ms (sử dụng vTaskDelayUntil).\n"
             "• Đọc nồng độ khí gas từ cảm biến MQ-2 (GPIO 34) và nhiệt độ từ DS18B20 (GPIO 4).\n"
             "• Hiển thị đầy đủ thông số qua giao tiếp Serial Monitor.\n"
             "• Gửi bản ghi SensorData_t vào cả 2 hàng đợi: 'data Queue' và 'data Alert'."),
            ("Task cảnh báo",
             "TaskAlertControl",
             "Core 1\n(App CPU)",
             "3\n(Cao nhất)",
             "4096 bytes",
             "• Đọc dữ liệu từ hàng đợi 'data Alert' (Blocking Read).\n"
             "• Kiểm tra ngưỡng báo cháy và điều khiển cơ cấu chấp hành:\n"
             "  + Quạt (GPIO 18) BẬT khi nồng độ khí gas ≥ 400 ppm.\n"
             "  + Máy bơm (GPIO 19) BẬT khi nhiệt độ ≥ 50 °C.\n"
             "  + Khi ở chế độ Manual: thực thi lệnh bật/tắt trực tiếp từ nút nhấn Web."),
        ]
    )

    doc.add_paragraph("Bảng 2 mô tả cấu trúc gói dữ liệu SensorData_t được truyền bên trong hai hàng đợi 'data Queue' và 'data Alert':")
    add_styled_table(
        doc,
        ["Tên trường dữ liệu", "Kiểu dữ liệu C/C++", "Kích thước", "Ý nghĩa và phạm vi giá trị"],
        [
            ("sampleId", "uint32_t", "4 bytes", "Số thứ tự mẫu đo tăng dần từ khi ESP32 khởi động."),
            ("timestampMs", "uint32_t", "4 bytes", "Thời điểm lấy mẫu tính bằng mili-giây (millis())."),
            ("gasAdc", "int", "4 bytes", "Giá trị số nguyên ADC 12-bit đọc từ chân AOUT của MQ-2 (0 – 4095)."),
            ("gasPpm", "float", "4 bytes", "Nồng độ khí gas/khói quy đổi theo thang đo (0.0 – 1000.0 ppm)."),
            ("gasPercent", "float", "4 bytes", "Tỉ lệ phần trăm nồng độ khí gas (0.0 – 100.0 %)."),
            ("temperatureC", "float", "4 bytes", "Nhiệt độ đọc từ cảm biến nhiệt DS18B20 (-55.0 đến +125.0 °C)."),
            ("gasExceed", "bool", "1 byte", "Cờ cảnh báo khí gas vượt ngưỡng (true khi gasPpm ≥ 400.0 ppm)."),
            ("tempExceed", "bool", "1 byte", "Cờ cảnh báo nhiệt độ vượt ngưỡng (true khi temperatureC ≥ 50.0 °C)."),
        ]
    )

    doc.add_paragraph("Bảng 3 tổng hợp thuật toán điều khiển cơ cấu chấp hành Quạt và Máy bơm (tích hợp vùng trễ Hysteresis chống đóng cắt liên tục):")
    add_styled_table(
        doc,
        ["Cơ cấu chấp hành", "Chân GPIO", "Điều kiện BẬT (Chế độ Auto)", "Điều kiện TẮT (Chế độ Auto)", "Hoạt động ở Chế độ Manual (Web Button)"],
        [
            ("Quạt hút khói/gas (Fan)", "GPIO 18", "Nồng độ khí gas ≥ 400.0 ppm", "Nồng độ khí gas ≤ 360.0 ppm", "Bật / Tắt trực tiếp khi nhấn nút <button> Quạt trên Web."),
            ("Máy bơm chữa cháy (Pump)", "GPIO 19", "Nhiệt độ ≥ 50.0 °C", "Nhiệt độ ≤ 47.0 °C", "Bật / Tắt trực tiếp khi nhấn nút <button> Máy bơm trên Web."),
        ]
    )

    doc.add_heading("4.3. Thiết kế giao diện trên Website/App để hiển thị dữ liệu và điều khiển", level=2)
    doc.add_paragraph(
        "Giao diện giám sát và điều khiển (tệp web_dashboard/index.html) được xây dựng bằng HTML5, CSS3, "
        "thư viện MQTT.js (kết nối tới MQTT Broker broker.emqx.io qua WebSockets tại cổng 8084) và thư viện "
        "Chart.js. Giao diện đáp ứng đầy đủ và chính xác cả 3 yêu cầu trong đề bài:"
    )
    add_bullet(doc, "1. Hai thẻ HTML có thuộc tính 'class' hiển thị số liệu Nồng độ khí gas và Nhiệt độ: ",
               "Sử dụng thẻ <div class='sensor-card gas-card'> chứa <span class='sensor-number gas-value'> "
               "để hiển thị nồng độ khí gas (ppm) và thẻ <div class='sensor-card temp-card'> chứa "
               "<span class='sensor-number temp-value'> để hiển thị nhiệt độ (°C). Trong JavaScript, chương trình "
               "truy xuất trực tiếp qua document.querySelector('.gas-value') và document.querySelector('.temp-value') "
               "để cập nhật giá trị ngay khi nhận bản tin từ MQTT Broker.")
    add_bullet(doc, "2. Hai biểu đồ cập nhật trực tiếp theo thời gian thực (Realtime Charts): ",
               "Sử dụng hai thẻ <canvas id='gasRealtimeChart' class='realtime-chart'> và "
               "<canvas id='tempRealtimeChart' class='realtime-chart'> vẽ đường biến thiên nồng độ khí gas (ppm) "
               "và nhiệt độ (°C) theo từng thời điểm nhận gói tin, có kèm đường nét đứt màu đỏ biểu diễn ngưỡng cảnh báo (400 ppm và 50 °C).")
    add_bullet(doc, "3. Hai nút <button> điều khiển trạng thái Máy bơm và Quạt (chế độ Manual): ",
               "Sử dụng thẻ <button class='control-button btn-fan-control' onclick='toggleFanManual()'> và "
               "<button class='control-button btn-pump-control' onclick='togglePumpManual()'>. Khi người dùng nhấn nút, "
               "giao diện Web sẽ xuất bản (Publish) bản tin JSON {'cmd':'setFan','state':true/false} hoặc "
               "{'cmd':'setPump','state':true/false} lên topic fire_alarm_vmk_231432270/control để ESP32 chuyển sang "
               "chế độ Manual và bật/tắt ngay cơ cấu chấp hành tương ứng.")

    # ==================== PHẦN 4.4: CODE VÀ GIẢI THÍCH CODE ====================
    doc.add_heading("4.4. Code chương trình đầy đủ và Giải thích chi tiết", level=2)

    doc.add_heading("4.4.1. Code chương trình ESP32 FreeRTOS (sketch.ino)", level=3)
    with open(SKETCH_PATH, "r", encoding="utf-8") as f:
        sketch_code = f.read()
    add_code_block(doc, sketch_code)

    doc.add_heading("4.4.2. Giải thích chi tiết chương trình ESP32 (Tạo kết nối, Cập nhật dữ liệu và Điều khiển)", level=3)
    add_bullet(doc, "• Khởi tạo Hàng đợi (Queue) và Cờ hiệu (Semaphore) trong hàm setup(): ",
               "Chương trình gọi xQueueCreate(10, sizeof(SensorData_t)) để tạo hai hàng đợi 'dataQueue' và 'dataAlertQueue', "
               "mỗi hàng đợi chứa tối đa 10 cấu trúc SensorData_t. Đồng thời tạo hai Mutex ('stateMutex', 'serialMutex') "
               "bằng xSemaphoreCreateMutex() và một Binary Semaphore ('controlSem') bằng xSemaphoreCreateBinary().")
    add_bullet(doc, "• Phân bổ 3 Task vào đúng Core của ESP32 bằng xTaskCreatePinnedToCore(): ",
               "Hàm xTaskCreatePinnedToCore(TaskTransmitData, ..., 0) ghim 'Task truyền data' cố định vào Core 0. "
               "Hai hàm xTaskCreatePinnedToCore(TaskReadData, ..., 1) và xTaskCreatePinnedToCore(TaskAlertControl, ..., 1) "
               "ghim 'Task đọc data' (Priority = 2) và 'Task cảnh báo' (Priority = 3) cố định vào Core 1.")
    add_bullet(doc, "• Quá trình đọc cảm biến và đẩy vào 2 Queue tại 'Task đọc data' (Core 1): ",
               "Định kỳ mỗi 1000 ms (nhờ vTaskDelayUntil), TaskReadData đọc giá trị ADC 12-bit từ chân GPIO 34 của MQ-2, "
               "quy đổi ra nồng độ ppm, đồng thời gọi tempSensor.requestTemperatures() để đọc nhiệt độ (°C) từ cảm biến "
               "DS18B20 trên chân GPIO 4. Sau khi in thông số ra Serial Monitor, Task gọi xQueueSend(dataQueue, &currentData, ...) "
               "để gửi dữ liệu sang Core 0 và gọi xQueueSend(dataAlertQueue, &currentData, ...) để gửi dữ liệu cho Task cảnh báo.")
    add_bullet(doc, "• Quá trình kiểm tra ngưỡng và điều khiển cơ cấu chấp hành tại 'Task cảnh báo' (Core 1): ",
               "TaskAlertControl gọi xQueueReceive(dataAlertQueue, &alertData, ...) để lấy dữ liệu từ hàng đợi 'data Alert'. "
               "Nếu hệ thống đang ở chế độ Tự động (AUTO), Task so sánh nồng độ khí gas với ngưỡng 400 ppm (nếu vượt ngưỡng thì "
               "xuất mức HIGH ra chân FAN_PIN = GPIO 18 để bật Quạt) và so sánh nhiệt độ với ngưỡng 50 °C (nếu vượt ngưỡng thì "
               "xuất mức HIGH ra chân PUMP_PIN = GPIO 19 để bật Máy bơm). Nếu đang ở chế độ Thủ công (MANUAL), Task giữ nguyên "
               "trạng thái Quạt và Máy bơm theo lệnh từ nút nhấn trên Web.")
    add_bullet(doc, "• Quá trình tạo kết nối Wi-Fi/MQTT, truyền dữ liệu và nhận lệnh điều khiển tại 'Task truyền data' (Core 0): ",
               "TaskTransmitData chạy trên Core 0 thực hiện kết nối mạng Wi-Fi Wokwi-GUEST và kết nối tới MQTT Broker "
               "broker.emqx.io (cổng 1883), đồng thời đăng ký lắng nghe (Subscribe) topic 'fire_alarm_vmk_231432270/control'. "
               "Khi kết nối thành công, Task gọi xQueueReceive(dataQueue, &txData, ...) để lấy dữ liệu từ 'data Queue', "
               "đóng gói thành chuỗi JSON thông qua thư viện ArduinoJson và gọi mqttClient.publish() gửi lên topic "
               "'fire_alarm_vmk_231432270/telemetry'. Khi người dùng nhấn nút Quạt hoặc Máy bơm trên Web, hàm mqttCallback() "
               "sẽ giải mã JSON, cập nhật biến sysState (bảo vệ bởi stateMutex), xuất tín hiệu ra GPIO và phát cờ controlSem.")

    doc.add_heading("4.4.3. Code cấu hình sơ đồ mạch Wokwi (diagram.json)", level=3)
    with open(DIAGRAM_PATH, "r", encoding="utf-8") as f:
        diagram_code = f.read()
    add_code_block(doc, diagram_code)

    doc.add_heading("4.4.4. Code giao diện Web hiển thị và điều khiển (web_dashboard/index.html)", level=3)
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_code = f.read()
    add_code_block(doc, html_code)

    # ==================== PHẦN 5: KẾT QUẢ ĐẠT ĐƯỢC & GITHUB ====================
    doc.add_heading("5. KẾT QUẢ ĐẠT ĐƯỢC BẰNG HÌNH ẢNH VÀ ĐƯA LÊN GITHUB", level=1)

    doc.add_heading("5.1. Kết quả mô phỏng mạch và hoạt động của hệ FreeRTOS trên Wokwi", level=2)
    doc.add_paragraph(
        "Khi khởi chạy mô phỏng trên Wokwi, ESP32 khởi tạo thành công 2 hàng đợi ('data Queue', 'data Alert') "
        "và 3 Task trên Core 0 và Core 1. Ở trạng thái bình thường (Nồng độ khí gas = 245 ppm < 400 ppm, "
        "Nhiệt độ = 31.5 °C < 50 °C), cả Quạt (GPIO 18) và Máy bơm (GPIO 19) đều ở trạng thái TẮT (OFF). "
        "Khi kéo thanh trượt tăng nồng độ khí gas trên cảm biến MQ-2 vượt quá 400 ppm (ví dụ 620 ppm) và tăng "
        "nhiệt độ trên cảm biến DS18B20 vượt quá 50 °C (ví dụ 64.5 °C), 'Task đọc data' lập tức đẩy dữ liệu vào "
        "'data Alert' để 'Task cảnh báo' bật sáng đèn LED Quạt (GPIO 18), bật sáng đèn LED Máy bơm (GPIO 19) "
        "và kích hoạt Còi báo cháy (GPIO 5)."
    )
    add_figure(doc, "04_wokwi_circuit_alarm.png",
               "Hình 4. Kết quả mô phỏng trên Wokwi khi nồng độ khí gas (620 ppm) và nhiệt độ (64.5 °C) vượt ngưỡng: Quạt (GPIO 18) và Máy bơm (GPIO 19) tự động BẬT.")

    doc.add_heading("5.2. Kết quả hiển thị dữ liệu và điều khiển trên giao diện Web/App", level=2)
    doc.add_paragraph(
        "Trên giao diện Web/App, dữ liệu nhận trực tiếp từ MQTT Broker được hiển thị tức thời lên 2 thẻ HTML "
        "sử dụng thuộc tính 'class' (.gas-value và .temp-value) và cập nhật liên tục lên 2 biểu đồ thời gian thực. "
        "Người dùng có thể nhấn trực tiếp vào 2 nút <button> 'BẬT/TẮT QUẠT' và 'BẬT/TẮT MÁY BƠM' để chuyển sang "
        "chế độ Manual và điều khiển đóng/ngắt cơ cấu chấp hành từ xa."
    )
    add_figure(doc, "05_web_dashboard_normal.png",
               "Hình 5. Giao diện Web/App hiển thị 2 thẻ số (HTML class), 2 biểu đồ thời gian thực và 2 nút điều khiển ở trạng thái bình thường (Chế độ AUTO).")
    add_figure(doc, "06_web_dashboard_manual.png",
               "Hình 6. Giao diện Web/App khi phát hiện cảnh báo vượt ngưỡng và điều khiển bật/tắt Máy bơm, Quạt bằng 2 nút <button> ở chế độ MANUAL.")

    doc.add_heading("5.3. Tổ chức thư mục mã nguồn và Đưa kết quả lên GitHub", level=2)
    doc.add_paragraph(
        "Toàn bộ mã nguồn dự án Wokwi ESP32 FreeRTOS, giao diện Web Dashboard, script mô phỏng MQTT, "
        "hình ảnh kết quả và báo cáo chi tiết đã được đóng gói chuẩn hóa trong kho lưu trữ Git (Git Repository) "
        "với cấu trúc thư mục như sau:"
    )
    repo_tree = (
        "Lab_RTOS_BaoChay/\n"
        "├── wokwi_esp32_rtos_baochay/\n"
        "│   ├── sketch.ino          # Mã nguồn ESP32 FreeRTOS (3 Tasks trên Core 0 & Core 1, 2 Queues)\n"
        "│   ├── diagram.json        # Sơ đồ mạch mô phỏng Wokwi (ESP32, MQ-2, DS18B20, Quạt, Máy bơm)\n"
        "│   ├── libraries.txt       # Danh sách thư viện Wokwi (PubSubClient, ArduinoJson, DallasTemperature)\n"
        "│   └── wokwi.toml          # Cấu hình Wokwi Simulator\n"
        "├── web_dashboard/\n"
        "│   ├── index.html          # Giao diện Web (2 thẻ HTML class, 2 biểu đồ Realtime, 2 nút button)\n"
        "│   └── mqtt_simulator.py   # Script Python kiểm thử truyền nhận MQTT trực tiếp với Web\n"
        "├── images/                 # Hình ảnh sơ đồ kiến trúc RTOS, mạch Wokwi và kết quả Web Dashboard\n"
        "├── BAO_CAO_LAB_RTOS_BAO_CHAY.md\n"
        "├── VuMinhKhoa_231432270_Lab_RTOS_BaoChay.docx\n"
        "└── README.md               # Tài liệu hướng dẫn chạy mô phỏng và báo cáo trên GitHub"
    )
    add_code_block(doc, repo_tree)

    doc.add_paragraph("Các lệnh Git sử dụng để khởi tạo kho lưu trữ và đẩy (Push) toàn bộ kết quả bài Lab lên GitHub:")
    git_cmds = (
        "# 1. Khởi tạo kho lưu trữ Git tại thư mục dự án\n"
        "git init\n"
        "git branch -M main\n\n"
        "# 2. Thêm toàn bộ mã nguồn, sơ đồ mạch Wokwi, giao diện Web, hình ảnh và báo cáo\n"
        "git add .\n"
        "git commit -m \"Hoan thanh Lab Mach bao chay gia dinh ESP32 FreeRTOS MQTT - Vu Minh Khoa 231432270\"\n\n"
        "# 3. Liên kết tới kho lưu trữ trên GitHub và đẩy dữ liệu lên nhánh main\n"
        "git remote add origin https://github.com/<username>/ESP32-FreeRTOS-FireAlarm-MQTT.git\n"
        "git push -u origin main"
    )
    add_code_block(doc, git_cmds)

    out_docx_1 = os.path.join(BASE_DIR, "VuMinhKhoa_231432270_Lab_RTOS_BaoChay.docx")
    out_docx_2 = r"d:\KI 1 NAM 4\HỆ THỐNG NHÚNG\VuMinhKhoa_231432270_Lab_RTOS_BaoChay.docx"
    doc.save(out_docx_1)
    doc.save(out_docx_2)
    print("DOCX REPORTS SAVED SUCCESSFULLY!")


if __name__ == "__main__":
    build_report()
