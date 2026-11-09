"""
Script mô phỏng thiết bị ESP32 chạy FreeRTOS gửi dữ liệu cảm biến MQ-2 & DS18B20
lên MQTT Broker (broker.emqx.io) và nhận lệnh điều khiển Quạt / Máy bơm từ Web.
Sinh viên: Vũ Minh Khoa - MSV: 231432270
"""

import json
import time
import random
import paho.mqtt.client as mqtt

MQTT_BROKER     = "broker.emqx.io"
MQTT_PORT       = 1883
TOPIC_TELEMETRY = "fire_alarm_vmk_231432270/telemetry"
TOPIC_CONTROL   = "fire_alarm_vmk_231432270/control"
TOPIC_STATUS    = "fire_alarm_vmk_231432270/status"

GAS_THRESHOLD   = 400.0
TEMP_THRESHOLD  = 50.0

state = {
    "manualMode": False,
    "fan": False,
    "pump": False,
    "gasAlert": False,
    "tempAlert": False,
}

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[Core 0 - TaskTransmitData] Connected to MQTT Broker ({MQTT_BROKER}) rc={reason_code}")
    client.subscribe(TOPIC_CONTROL)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        cmd = payload.get("cmd", "")
        if cmd == "setMode":
            state["manualMode"] = bool(payload.get("manual", False))
        elif cmd == "setFan":
            state["manualMode"] = True
            state["fan"] = bool(payload.get("state", False))
        elif cmd == "setPump":
            state["manualMode"] = True
            state["pump"] = bool(payload.get("state", False))
        print(f"[Core 0 - MQTT Callback] Received command: {payload} -> State: {state}")
        client.publish(TOPIC_STATUS, json.dumps(state))
    except Exception as e:
        print(f"[Error] Invalid JSON: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"ESP32_Sim_VMK_{random.randint(1000,9999)}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    sample_id = 0
    scenarios = [
        (235.0, 31.2),
        (248.5, 31.6),
        (465.0, 32.4),  # Gas vượt ngưỡng -> Quạt BẬT
        (520.0, 33.1),  # Gas vượt ngưỡng -> Quạt BẬT
        (260.0, 56.8),  # Nhiệt độ vượt ngưỡng -> Máy bơm BẬT
        (610.0, 61.5),  # Cả 2 vượt ngưỡng -> Quạt & Máy bơm BẬT
        (240.0, 31.5),  # Trở về an toàn
    ]

    try:
        while True:
            gas_ppm, temp_c = scenarios[sample_id % len(scenarios)]
            sample_id += 1
            gas_adc = int((gas_ppm / 1000.0) * 4095)

            state["gasAlert"] = gas_ppm >= GAS_THRESHOLD
            state["tempAlert"] = temp_c >= TEMP_THRESHOLD

            if not state["manualMode"]:
                state["fan"] = state["gasAlert"]
                state["pump"] = state["tempAlert"]

            telemetry = {
                "sampleId": sample_id,
                "gasAdc": gas_adc,
                "gas": round(gas_ppm, 1),
                "gasPercent": round(gas_ppm / 10.0, 1),
                "temperature": round(temp_c, 1),
                "mode": "MANUAL" if state["manualMode"] else "AUTO",
                "manualMode": state["manualMode"],
                "fan": state["fan"],
                "pump": state["pump"],
                "gasAlert": state["gasAlert"],
                "tempAlert": state["tempAlert"],
                "coreRead": 1,
                "coreAlert": 1,
                "coreTx": 0,
            }

            client.publish(TOPIC_TELEMETRY, json.dumps(telemetry))
            print(f"[Core 1 -> Queue -> Core 0] Published: {json.dumps(telemetry)}")
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
