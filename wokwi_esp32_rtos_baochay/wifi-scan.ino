/*
 * ============================================================================
 * ĐỀ TÀI: THIẾT KẾ MẠCH BÁO CHÁY GIA ĐÌNH SỬ DỤNG ESP32, FREERTOS VÀ MQTT
 * Sinh viên thực hiện : Vũ Minh Khoa
 * Mã sinh viên        : 231432270
 * Lớp                 : Điện Tử và Tin Học Công Nghiệp 1 - K64
 * ============================================================================
 * YÊU CẦU HỆ THỐNG RTOS TRÊN ESP32:
 *  1. "Task truyền data" (TaskTransmitData) - Chạy trên Core 0:
 *     - Kết nối Wi-Fi, nếu thành công thì kết nối MQTT Broker.
 *     - Đọc dữ liệu từ hàng đợi "data Queue" (dataQueue) và gửi lên MQTT Broker.
 *     - Nhận lệnh điều khiển Quạt / Máy bơm (chế độ Manual/Auto) từ Web/App.
 *  2. "Task đọc data" (TaskReadData) - Chạy trên Core 1:
 *     - Đọc nồng độ khí gas/khói từ cảm biến MQ-2 (ADC GPIO 34) và nhiệt độ
 *       từ cảm biến nhiệt DS18B20 (1-Wire GPIO 4).
 *     - Hiển thị dữ liệu qua giao tiếp Serial.
 *     - Gửi dữ liệu đầy đủ vào hàng đợi "data Queue" (dataQueue) và
 *       vào hàng đợi "data Alert" (dataAlertQueue).
 *  3. "Task cảnh báo" (TaskAlertControl) - Chạy trên Core 1:
 *     - Đọc dữ liệu từ hàng đợi "data Alert" (dataAlertQueue).
 *     - Thực hiện điều khiển cơ cấu chấp hành là Quạt (GPIO 18) và Máy bơm (GPIO 19):
 *       + Quạt bật khi nồng độ khí gas vượt ngưỡng (chế độ Auto).
 *       + Máy bơm bật khi nhiệt độ vượt ngưỡng (chế độ Auto).
 *       + Hỗ trợ điều khiển bật/tắt Máy bơm và Quạt bằng nút nhấn từ Web (Manual).
 * ============================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ===================== 1. CẤU HÌNH MẠNG WIFI & MQTT BROKER ==================
const char* WIFI_SSID       = "Wokwi-GUEST";
const char* WIFI_PASSWORD   = "";

// Sử dụng Public MQTT Broker EMQX (hỗ trợ TCP 1883 cho ESP32 & WebSocket 8083/8084 cho Web)
const char* MQTT_BROKER     = "broker.emqx.io";
const int   MQTT_PORT       = 1883;
const char* MQTT_CLIENT_ID  = "ESP32_FireAlarm_VMK_231432270";

// Các MQTT Topic giao tiếp giữa ESP32 và Giao diện Web/App
const char* TOPIC_TELEMETRY = "fire_alarm_vmk_231432270/telemetry";
const char* TOPIC_CONTROL   = "fire_alarm_vmk_231432270/control";
const char* TOPIC_STATUS    = "fire_alarm_vmk_231432270/status";

// ===================== 2. ĐỊNH NGHĨA CHÂN PHẦN CỨNG (GPIO) ==================
#define MQ2_ADC_PIN         34    // Chân Analog đọc nồng độ khí gas/khói từ MQ-2 (Input Only)
#define MQ2_DOUT_PIN        35    // Chân Digital của cảm biến MQ-2 (Input Only)
#define TEMP_ONEWIRE_PIN    4     // Chân DATA giao tiếp 1-Wire với cảm biến nhiệt DS18B20
#define FAN_PIN             18    // Cơ cấu chấp hành 1: Quạt hút khói/gas (LED Xanh / Relay 1)
#define PUMP_PIN            19    // Cơ cấu chấp hành 2: Máy bơm chữa cháy (LED Đỏ / Relay 2)
#define BUZZER_PIN          5     // Còi báo động tại chỗ khi phát hiện cháy/rò rỉ khí gas

// ===================== 3. NGƯỠNG CẢNH BÁO CHÁY (THRESHOLDS) =================
#define GAS_THRESHOLD_PPM   400.0f  // Ngưỡng nồng độ khí gas/khói kích hoạt Quạt (ppm)
#define GAS_HYSTERESIS_PPM  360.0f  // Ngưỡng trễ tắt Quạt tránh đóng cắt liên tục (ppm)
#define TEMP_THRESHOLD_C    50.0f   // Ngưỡng nhiệt độ kích hoạt Máy bơm (°C)
#define TEMP_HYSTERESIS_C   47.0f   // Ngưỡng trễ tắt Máy bơm (°C)

// ===================== 4. CẤU TRÚC DỮ LIỆU HÀNG ĐỢI (QUEUE) =================
typedef struct {
  uint32_t sampleId;        // Số thứ tự mẫu đo
  uint32_t timestampMs;     // Thời điểm lấy mẫu (ms từ lúc khởi động)
  int      gasAdc;          // Giá trị ADC thô từ MQ-2 (0 - 4095)
  float    gasPpm;          // Nồng độ khí gas/khói quy đổi (ppm: 0 - 1000)
  float    gasPercent;      // Phần trăm mức khí gas (0 - 100%)
  float    temperatureC;    // Nhiệt độ môi trường (°C)
  bool     gasExceed;       // Cờ báo nồng độ khí gas vượt ngưỡng
  bool     tempExceed;      // Cờ báo nhiệt độ vượt ngưỡng
} SensorData_t;

// Cấu trúc lưu trạng thái hệ thống & cơ cấu chấp hành (bảo vệ bởi Mutex Semaphore)
typedef struct {
  bool manualMode;          // false = Chế độ Tự động (AUTO), true = Chế độ Thủ công (MANUAL)
  bool fanState;            // Trạng thái hiện tại của Quạt (true = BẬT, false = TẮT)
  bool pumpState;           // Trạng thái hiện tại của Máy bơm (true = BẬT, false = TẮT)
  bool manualFanCmd;        // Lệnh điều khiển Quạt từ nút nhấn Web ở chế độ Manual
  bool manualPumpCmd;       // Lệnh điều khiển Máy bơm từ nút nhấn Web ở chế độ Manual
  bool gasAlert;            // Cảnh báo khí gas vượt ngưỡng
  bool tempAlert;           // Cảnh báo nhiệt độ vượt ngưỡng
} SystemState_t;

// ===================== 5. KHAI BÁO CÁC ĐỐI TƯỢNG FREERTOS ===================
QueueHandle_t     dataQueue;          // Hàng đợi "data Queue": Task đọc data -> Task truyền data
QueueHandle_t     dataAlertQueue;     // Hàng đợi "data Alert": Task đọc data -> Task cảnh báo
SemaphoreHandle_t stateMutex;         // Semaphore Mutex bảo vệ biến trạng thái chung sysState
SemaphoreHandle_t serialMutex;        // Semaphore Mutex đồng bộ in Serial giữa Core 0 & Core 1
SemaphoreHandle_t controlSem;         // Binary Semaphore đánh thức Task cảnh báo khi có lệnh Manual

TaskHandle_t      taskTransmitHandle = NULL;
TaskHandle_t      taskReadHandle     = NULL;
TaskHandle_t      taskAlertHandle    = NULL;

// ===================== 6. ĐỐI TƯỢNG PHẦN CỨNG & TRẠNG THÁI ==================
WiFiClient        espWiFiClient;
PubSubClient      mqttClient(espWiFiClient);
OneWire           oneWireBus(TEMP_ONEWIRE_PIN);
DallasTemperature tempSensor(&oneWireBus);

SystemState_t     sysState = {
  .manualMode    = false,
  .fanState      = false,
  .pumpState     = false,
  .manualFanCmd  = false,
  .manualPumpCmd = false,
  .gasAlert      = false,
  .tempAlert     = false
};

uint32_t globalSampleCounter = 0;

// ===================== 7. HÀM TIỆN ÍCH ĐỒNG BỘ SERIAL =======================
void safeSerialPrintln(const String& msg) {
  if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    Serial.println(msg);
    xSemaphoreGive(serialMutex);
  }
}

// Hàm áp dụng trạng thái ra chân GPIO vật lý của Quạt, Máy bơm và Còi báo động
void applyActuatorOutputs(bool fanOn, bool pumpOn, bool alarmActive) {
  digitalWrite(FAN_PIN, fanOn ? HIGH : LOW);
  digitalWrite(PUMP_PIN, pumpOn ? HIGH : LOW);
  if (alarmActive) {
    tone(BUZZER_PIN, 2000, 250);
  } else {
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

// Hàm gửi nhanh bản tin trạng thái cơ cấu chấp hành lên MQTT khi có thay đổi
void publishSystemStatus() {
  if (!mqttClient.connected()) return;

  StaticJsonDocument<256> doc;
  if (xSemaphoreTake(stateMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
    doc["mode"]       = sysState.manualMode ? "MANUAL" : "AUTO";
    doc["manualMode"] = sysState.manualMode;
    doc["fan"]        = sysState.fanState;
    doc["pump"]       = sysState.pumpState;
    doc["gasAlert"]   = sysState.gasAlert;
    doc["tempAlert"]  = sysState.tempAlert;
    xSemaphoreGive(stateMutex);
  }

  char buffer[256];
  serializeJson(doc, buffer);
  mqttClient.publish(TOPIC_STATUS, buffer, true);
}

// ===================== 8. CALLBACK NHẬN LỆNH TỪ WEB QUA MQTT ================
/*
 * Định dạng JSON gửi từ các nút <button> trên giao diện Web/App:
 *  - Chuyển chế độ: {"cmd": "setMode", "manual": true/false}
 *  - Nút Quạt     : {"cmd": "setFan",  "state": true/false}
 *  - Nút Máy bơm  : {"cmd": "setPump", "state": true/false}
 */
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) {
    safeSerialPrintln("[MQTT-RX] Loi phan tich JSON lenh dieu khien!");
    return;
  }

  const char* cmd = doc["cmd"] | "";
  bool stateChanged = false;

  if (xSemaphoreTake(stateMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    if (strcmp(cmd, "setMode") == 0) {
      sysState.manualMode = doc["manual"].as<bool>();
      if (sysState.manualMode) {
        // Khi chuyển sang Manual, giữ nguyên trạng thái hiện tại làm lệnh khởi đầu
        sysState.manualFanCmd  = sysState.fanState;
        sysState.manualPumpCmd = sysState.pumpState;
      }
      stateChanged = true;
    }
    else if (strcmp(cmd, "setFan") == 0) {
      bool targetState = doc["state"].as<bool>();
      sysState.manualMode   = true; // Tự động kích hoạt chế độ Manual khi bấm nút trên Web
      sysState.manualFanCmd = targetState;
      sysState.fanState     = targetState;
      applyActuatorOutputs(sysState.fanState, sysState.pumpState,
                           sysState.gasAlert || sysState.tempAlert);
      stateChanged = true;
    }
    else if (strcmp(cmd, "setPump") == 0) {
      bool targetState = doc["state"].as<bool>();
      sysState.manualMode    = true; // Tự động kích hoạt chế độ Manual khi bấm nút trên Web
      sysState.manualPumpCmd = targetState;
      sysState.pumpState     = targetState;
      applyActuatorOutputs(sysState.fanState, sysState.pumpState,
                           sysState.gasAlert || sysState.tempAlert);
      stateChanged = true;
    }
    xSemaphoreGive(stateMutex);
  }

  if (stateChanged) {
    // Phát tín hiệu Semaphore cho Task cảnh báo cập nhật ngay lập tức
    xSemaphoreGive(controlSem);
    publishSystemStatus();

    String logMsg = String("[MQTT-RX] Nhan lenh Web: cmd=") + cmd +
                    " | Mode=" + (sysState.manualMode ? "MANUAL" : "AUTO") +
                    " | Quat=" + (sysState.fanState ? "ON" : "OFF") +
                    " | MayBom=" + (sysState.pumpState ? "ON" : "OFF");
    safeSerialPrintln(logMsg);
  }
}

// ===================== 9. TASK 1: ĐỌC DỮ LIỆU CẢM BIẾN (CORE 1) =============
/*
 * Yêu cầu đề bài:
 * - "Task đọc data", chạy Core 1: đọc dữ liệu cảm biến MQ2 và nhiệt độ từ cảm
 *   biến nhiệt, hiển thị dữ liệu qua giao tiếp serial, gửi dữ liệu đầy đủ vào
 *   hàng đợi "data Queue" và vào hàng đợi "data Alert".
 */
void TaskReadData(void* pvParameters) {
  (void)pvParameters;
  safeSerialPrintln("[RTOS] TaskReadData khoi chay tren Core " + String(xPortGetCoreID()));

  TickType_t xLastWakeTime = xTaskGetTickCount();
  const TickType_t xFrequency = pdMS_TO_TICKS(1000); // Chu kỳ lấy mẫu: 1000 ms (1 giây)

  for (;;) {
    // 1. Đọc giá trị ADC 12-bit (0 - 4095) từ cảm biến khí gas/khói MQ-2
    int rawAdc = analogRead(MQ2_ADC_PIN);

    // Quy đổi giá trị ADC sang nồng độ khí gas/khói tương đương (0 - 1000 ppm) và %
    float gasPpm     = (rawAdc / 4095.0f) * 1000.0f;
    float gasPercent = (rawAdc / 4095.0f) * 100.0f;

    // 2. Đọc nhiệt độ (°C) từ cảm biến nhiệt độ 1-Wire DS18B20
    tempSensor.requestTemperatures();
    float tempC = tempSensor.getTempCByIndex(0);

    // Kiểm tra nếu cảm biến DS18B20 chưa kịp phản hồi (-127°C) thì giữ giá trị an toàn
    if (tempC == DEVICE_DISCONNECTED_C || isnan(tempC) || tempC < -55.0f || tempC > 150.0f) {
      tempC = 31.5f;
    }

    // 3. Đóng gói dữ liệu đầy đủ vào cấu trúc SensorData_t
    globalSampleCounter++;
    SensorData_t currentData;
    currentData.sampleId     = globalSampleCounter;
    currentData.timestampMs  = millis();
    currentData.gasAdc       = rawAdc;
    currentData.gasPpm       = gasPpm;
    currentData.gasPercent   = gasPercent;
    currentData.temperatureC = tempC;
    currentData.gasExceed    = (gasPpm >= GAS_THRESHOLD_PPM);
    currentData.tempExceed   = (tempC  >= TEMP_THRESHOLD_C);

    // 4. Hiển thị dữ liệu qua giao tiếp Serial
    String serialLog = "[TaskReadData - Core " + String(xPortGetCoreID()) + "] " +
                       "Mau #" + String(currentData.sampleId) +
                       " | Gas MQ-2: " + String(currentData.gasPpm, 1) + " ppm" +
                       " (ADC: " + String(currentData.gasAdc) + ", " + String(currentData.gasPercent, 1) + "%)" +
                       " | Nhiet do: " + String(currentData.temperatureC, 1) + " C";
    safeSerialPrintln(serialLog);

    // 5. Gửi dữ liệu đầy đủ vào hàng đợi "data Queue" (cho Task truyền data ở Core 0)
    if (xQueueSend(dataQueue, &currentData, pdMS_TO_TICKS(50)) != pdPASS) {
      // Nếu hàng đợi đầy, ghi đè phần tử cũ nhất để luôn ưu tiên dữ liệu thời gian thực
      SensorData_t dummy;
      xQueueReceive(dataQueue, &dummy, 0);
      xQueueSend(dataQueue, &currentData, 0);
    }

    // 6. Gửi dữ liệu đầy đủ vào hàng đợi "data Alert" (cho Task cảnh báo ở Core 1)
    if (xQueueSend(dataAlertQueue, &currentData, pdMS_TO_TICKS(50)) != pdPASS) {
      SensorData_t dummy;
      xQueueReceive(dataAlertQueue, &dummy, 0);
      xQueueSend(dataAlertQueue, &currentData, 0);
    }

    // Lập lịch chu kỳ chính xác 1 giây bằng vTaskDelayUntil
    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

// ===================== 10. TASK 2: CẢNH BÁO & ĐIỀU KHIỂN (CORE 1) ===========
/*
 * Yêu cầu đề bài:
 * - "Task cảnh báo", chạy Core 1: đọc dữ liệu từ hàng đợi "data Alert", và thực
 *   hiện điều khiển cơ cấu chấp hành là quạt và máy bơm.
 *   + Quạt bật khi nồng độ khí gas vượt ngưỡng.
 *   + Máy bơm bật khi nhiệt độ vượt ngưỡng.
 */
void TaskAlertControl(void* pvParameters) {
  (void)pvParameters;
  safeSerialPrintln("[RTOS] TaskAlertControl khoi chay tren Core " + String(xPortGetCoreID()));

  SensorData_t alertData;

  for (;;) {
    // Chờ nhận gói dữ liệu mới từ hàng đợi "data Alert" (Blocking Read tiết kiệm CPU)
    if (xQueueReceive(dataAlertQueue, &alertData, pdMS_TO_TICKS(200)) == pdPASS) {
      bool fanOut      = false;
      bool pumpOut     = false;
      bool gasIsAlert  = false;
      bool tempIsAlert = false;
      bool isManual    = false;

      if (xSemaphoreTake(stateMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        // Cập nhật trạng thái cảnh báo vượt ngưỡng (có vùng trễ Hysteresis chống nhiễu)
        if (alertData.gasPpm >= GAS_THRESHOLD_PPM) {
          sysState.gasAlert = true;
        } else if (alertData.gasPpm <= GAS_HYSTERESIS_PPM) {
          sysState.gasAlert = false;
        }

        if (alertData.temperatureC >= TEMP_THRESHOLD_C) {
          sysState.tempAlert = true;
        } else if (alertData.temperatureC <= TEMP_HYSTERESIS_C) {
          sysState.tempAlert = false;
        }

        gasIsAlert  = sysState.gasAlert;
        tempIsAlert = sysState.tempAlert;
        isManual    = sysState.manualMode;

        if (!sysState.manualMode) {
          // CHẾ ĐỘ TỰ ĐỘNG (AUTO):
          // - Quạt bật khi nồng độ khí gas vượt ngưỡng
          // - Máy bơm bật khi nhiệt độ vượt ngưỡng
          sysState.fanState  = sysState.gasAlert;
          sysState.pumpState = sysState.tempAlert;
        } else {
          // CHẾ ĐỘ THỦ CÔNG (MANUAL):
          // Điều khiển theo trạng thái nút nhấn từ giao diện Web/App
          sysState.fanState  = sysState.manualFanCmd;
          sysState.pumpState = sysState.manualPumpCmd;
        }

        fanOut  = sysState.fanState;
        pumpOut = sysState.pumpState;
        xSemaphoreGive(stateMutex);
      }

      // Xuất tín hiệu điều khiển ra chân GPIO Quạt (GPIO 18), Máy bơm (GPIO 19) và Còi (GPIO 5)
      applyActuatorOutputs(fanOut, pumpOut, gasIsAlert || tempIsAlert);

      // In thông báo trạng thái điều khiển và cảnh báo qua Serial
      String alertMsg = "[TaskAlertControl - Core " + String(xPortGetCoreID()) + "] " +
                        "Che do: " + String(isManual ? "MANUAL" : "AUTO") +
                        " | Canh bao Gas: " + String(gasIsAlert ? "NGUY HIEM!" : "An toan") +
                        " | Canh bao Nhiet: " + String(tempIsAlert ? "NGUY HIEM!" : "An toan") +
                        " => QUAT: " + String(fanOut ? "BAT (ON)" : "TAT (OFF)") +
                        " | MAY BOM: " + String(pumpOut ? "BAT (ON)" : "TAT (OFF)");
      safeSerialPrintln(alertMsg);
    }

    // Kiểm tra nếu có Semaphore điều khiển tức thời từ nút nhấn Web
    if (xSemaphoreTake(controlSem, 0) == pdTRUE) {
      if (xSemaphoreTake(stateMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
        applyActuatorOutputs(sysState.fanState, sysState.pumpState,
                             sysState.gasAlert || sysState.tempAlert);
        xSemaphoreGive(stateMutex);
      }
    }
  }
}

// ===================== 11. TASK 3: KẾT NỐI WIFI & TRUYỀN MQTT (CORE 0) ======
/*
 * Yêu cầu đề bài:
 * - "Task truyền data": kết nối Wifi chạy Core 0, nếu thành công, đọc dữ liệu
 *   từ hàng đợi "data Queue", và gửi lên MQTT broker.
 */
void ensureWiFiConnected() {
  if (WiFi.status() == WL_CONNECTED) return;

  safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                    "] Dang ket noi WiFi: " + String(WIFI_SSID) + " ...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);

  while (WiFi.status() != WL_CONNECTED) {
    vTaskDelay(pdMS_TO_TICKS(500));
  }

  safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                    "] WiFi da ket noi! IP: " + WiFi.localIP().toString());
}

void ensureMQTTConnected() {
  if (mqttClient.connected()) return;

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);

  while (!mqttClient.connected() && WiFi.status() == WL_CONNECTED) {
    String clientId = String(MQTT_CLIENT_ID) + "_" + String(random(1000, 9999));
    safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                      "] Dang ket noi MQTT Broker (" + String(MQTT_BROKER) + ")...");

    if (mqttClient.connect(clientId.c_str())) {
      safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                        "] MQTT Broker da ket noi thanh cong!");
      mqttClient.subscribe(TOPIC_CONTROL);
      publishSystemStatus();
    } else {
      safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                        "] Loi ket noi MQTT, ma loi rc=" + String(mqttClient.state()) +
                        ". Thu lai sau 2 giay...");
      vTaskDelay(pdMS_TO_TICKS(2000));
    }
  }
}

void TaskTransmitData(void* pvParameters) {
  (void)pvParameters;
  safeSerialPrintln("[RTOS] TaskTransmitData khoi chay tren Core " + String(xPortGetCoreID()));

  SensorData_t txData;

  for (;;) {
    // 1. Đảm bảo kết nối Wi-Fi trên Core 0
    ensureWiFiConnected();

    // 2. Nếu Wi-Fi thành công, duy trì kết nối tới MQTT Broker
    if (WiFi.status() == WL_CONNECTED) {
      ensureMQTTConnected();
      mqttClient.loop();

      // 3. Đọc dữ liệu từ hàng đợi "data Queue" và gửi lên MQTT Broker
      if (xQueueReceive(dataQueue, &txData, pdMS_TO_TICKS(100)) == pdPASS) {
        StaticJsonDocument<384> doc;

        doc["sampleId"]    = txData.sampleId;
        doc["timestamp"]   = txData.timestampMs;
        doc["gasAdc"]      = txData.gasAdc;
        doc["gas"]         = serialized(String(txData.gasPpm, 1));
        doc["gasPercent"]  = serialized(String(txData.gasPercent, 1));
        doc["temperature"] = serialized(String(txData.temperatureC, 1));

        // Đọc trạng thái cơ cấu chấp hành hiện tại thông qua Mutex Semaphore
        if (xSemaphoreTake(stateMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
          doc["mode"]       = sysState.manualMode ? "MANUAL" : "AUTO";
          doc["manualMode"] = sysState.manualMode;
          doc["fan"]        = sysState.fanState;
          doc["pump"]       = sysState.pumpState;
          doc["gasAlert"]   = sysState.gasAlert;
          doc["tempAlert"]  = sysState.tempAlert;
          xSemaphoreGive(stateMutex);
        }

        // Thông tin chẩn đoán RTOS Core
        doc["coreRead"]  = 1;
        doc["coreAlert"] = 1;
        doc["coreTx"]    = xPortGetCoreID();

        char payload[384];
        serializeJson(doc, payload);

        if (mqttClient.publish(TOPIC_TELEMETRY, payload)) {
          safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                            "] Da gui MQTT Telemetry: " + String(payload));
        } else {
          safeSerialPrintln("[TaskTransmitData - Core " + String(xPortGetCoreID()) +
                            "] Gui MQTT that bai!");
        }
      }
    }

    // Nhường CPU ngắn cho Idle Task & Watchdog Timer trên Core 0
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

// ===================== 12. HÀM KHỞI TẠO HỆ THỐNG (SETUP) ====================
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("==================================================================");
  Serial.println(" HE THONG BAO CHAY GIA DINH - ESP32 DUAL-CORE FREERTOS & MQTT");
  Serial.println(" Sinh vien: Vu Minh Khoa - MSV: 231432270");
  Serial.println("==================================================================");

  // Cấu hình độ phân giải ADC 12-bit (0 - 4095) cho cảm biến MQ-2
  analogReadResolution(12);
  pinMode(MQ2_ADC_PIN, INPUT);
  pinMode(MQ2_DOUT_PIN, INPUT);

  // Khởi tạo cảm biến nhiệt độ 1-Wire DS18B20
  tempSensor.begin();

  // Cấu hình các chân điều khiển Cơ cấu chấp hành (Quạt, Máy bơm, Còi)
  pinMode(FAN_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Khởi tạo các Hàng đợi (Queues) và Cờ hiệu (Semaphores / Mutexes) của FreeRTOS
  dataQueue      = xQueueCreate(10, sizeof(SensorData_t));
  dataAlertQueue = xQueueCreate(10, sizeof(SensorData_t));
  stateMutex     = xSemaphoreCreateMutex();
  serialMutex    = xSemaphoreCreateMutex();
  controlSem     = xSemaphoreCreateBinary();

  if (dataQueue == NULL || dataAlertQueue == NULL ||
      stateMutex == NULL || serialMutex == NULL || controlSem == NULL) {
    Serial.println("[LOI NGHIEM TRONG] Khong du bo nho Heap de tao Queue/Semaphore!");
    while (true) { delay(1000); }
  }

  // Khởi tạo 3 Task theo đúng yêu cầu phân chia Core của đề bài:
  // 1. "Task truyền data": chạy trên Core 0
  xTaskCreatePinnedToCore(
    TaskTransmitData,     // Hàm thực thi Task
    "TaskTransmitData",   // Tên Task
    8192,                 // Kích thước Stack (bytes)
    NULL,                 // Tham số truyền vào
    2,                    // Độ ưu tiên (Priority = 2)
    &taskTransmitHandle,  // Handle quản lý Task
    0                     // Gán cố định vào CORE 0 (Protocol CPU)
  );

  // 2. "Task đọc data": chạy trên Core 1
  xTaskCreatePinnedToCore(
    TaskReadData,         // Hàm thực thi Task
    "TaskReadData",       // Tên Task
    4096,                 // Kích thước Stack (bytes)
    NULL,                 // Tham số truyền vào
    2,                    // Độ ưu tiên (Priority = 2)
    &taskReadHandle,      // Handle quản lý Task
    1                     // Gán cố định vào CORE 1 (Application CPU)
  );

  // 3. "Task cảnh báo": chạy trên Core 1 (Ưu tiên cao hơn để phản ứng tức thời)
  xTaskCreatePinnedToCore(
    TaskAlertControl,     // Hàm thực thi Task
    "TaskAlertControl",   // Tên Task
    4096,                 // Kích thước Stack (bytes)
    NULL,                 // Tham số truyền vào
    3,                    // Độ ưu tiên cao nhất (Priority = 3)
    &taskAlertHandle,     // Handle quản lý Task
    1                     // Gán cố định vào CORE 1 (Application CPU)
  );

  safeSerialPrintln("[RTOS] Da khoi tao thanh cong 3 Task va 2 Queue (data Queue, data Alert)!");
}

// ===================== 13. VÒNG LẶP CHÍNH (LOOP) ============================
void loop() {
  // Toàn bộ nghiệp vụ đã được quản lý bởi bộ lập lịch FreeRTOS trên Core 0 và Core 1.
  // Đưa loopTask vào trạng thái ngủ dài để giải phóng tài nguyên CPU.
  vTaskDelay(pdMS_TO_TICKS(5000));
}
