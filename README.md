# IoT Smart Plant Disease Detection 🌿

An end-to-end IoT system for real-time plant disease detection and smart farm monitoring, deployed on a **Raspberry Pi 5** using a **TFLite-optimised CNN** trained on the PlantVillage dataset. Covers the full pipeline: model training → post-training quantisation → edge deployment → sensor integration → cloud dashboard.

---

## 🧠 ML Model

| Attribute | Detail |
|---|---|
| Dataset | PlantVillage (~54,000 images, 38 classes) |
| Architecture | MobileNetV2 (fine-tuned CNN) |
| Optimisation | TFLite INT8 post-training quantisation |
| Inference Speed | Sub-200ms on Raspberry Pi 5 |
| Size Reduction | 74% smaller than FP32 baseline |
| Latency Reduction | 3.8x faster than FP32 ResNet-18 |
| Accuracy Drop | Only 2.1% vs. full precision model |

---

## 🏗️ System Architecture

```
PlantVillage Dataset
       ↓
  CNN Training (Colab)
       ↓
TFLite Quantisation (INT8)
       ↓
  Raspberry Pi 5
  ├── Camera Module → Leaf Disease Inference
  ├── DHT22 Sensor  → Temperature & Humidity
  ├── Soil Sensor   → Moisture Level
  ├── LDR Sensor    → Light Intensity
  ├── Rain Sensor   → Rainfall Detection
  ├── PIR Sensor    → Animal Intrusion
  ├── Ultrasonic    → Distance Measurement
  ├── MQ-2 Sensor   → Smoke Detection
  └── Relay Pump    → Automated Watering
       ↓
  MQTT Broker → Adafruit IO Cloud Dashboard
       ↓
  LCD Display (I2C, 16x2)
```

---

## 📁 Project Structure

```
Leaf-Disease-Detection/
├── project/
│   ├── colab/
│   │   └── train_model.py          # CNN training + TFLite export
│   ├── pi/
│   │   ├── main.py                 # Main orchestration loop
│   │   ├── camera.py               # Leaf capture + TFLite inference
│   │   ├── sensors.py              # All GPIO sensor readings
│   │   ├── cloud_pump_display.py   # Adafruit IO + pump + LCD control
│   │   └── config.py               # Central config (credentials, pins, thresholds)
│   ├── requirements.txt
│   └── README.md
├── plant_disease_model.tflite      # Quantised model (ready for Pi deployment)
└── class_names.txt                 # 38 PlantVillage class labels
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Raspberry Pi 5 (or compatible)
- Python 3.10+
- Adafruit IO account (free tier)
- Plant.id API key (optional — for API-based detection mode)

### Install Dependencies

```bash
cd project
pip install -r requirements.txt
```

### Configure Credentials

Edit `pi/config.py` with your credentials:

```python
ADAFRUIT_USERNAME = "your_adafruit_username"
ADAFRUIT_KEY      = "your_adafruit_io_key"
PLANTID_API_KEY   = "your_plantid_api_key"   # Optional
```

### Run on Raspberry Pi

```bash
cd project/pi
python main.py
```

### Train Model (Google Colab)

```bash
cd project/colab
python train_model.py
```

---

## 🔧 GPIO Pin Configuration (BCM Mode)

| Sensor | GPIO Pin |
|---|---|
| Soil Moisture | 17 |
| DHT22 (Temp/Humidity) | 4 |
| LDR (Light) | 27 |
| Rain Sensor | 22 |
| PIR (Motion/Animal) | 23 |
| Ultrasonic TRIG | 24 |
| Ultrasonic ECHO | 25 |
| MQ-2 Smoke | 5 |
| Relay (Water Pump) | 18 |

---

## 🌡️ Alert Thresholds

| Parameter | Threshold |
|---|---|
| High Temperature | > 35°C |
| Low Humidity | < 30% |
| Pump Duration | 5 seconds per cycle |
| Watering Interval | Every 30 minutes |
| Disease Check | Every 60 minutes |
| Animal Distance Alert | < 50 cm |

---

## ☁️ Cloud Dashboard

Sensor telemetry streams to **Adafruit IO** via MQTT, providing a real-time dashboard for:
- Temperature & humidity trends
- Soil moisture status
- Disease detection events
- Pump activation logs
- Intrusion alerts

---

## 🛠️ Tech Stack

- **ML:** TensorFlow Lite, MobileNetV2, PlantVillage dataset
- **Hardware:** Raspberry Pi 5, DHT22, soil sensor, PIR, ultrasonic, MQ-2, relay
- **Connectivity:** MQTT, Adafruit IO
- **Display:** I2C LCD (16x2, address 0x27)
- **Languages:** Python

---

## 👨‍💻 Author

**Mohanlal Satapathy**  
BTech CSE, Silicon Institute of Technology, Bhubaneswar  
[GitHub](https://github.com/mohanlal-satapathy-369) · [LinkedIn](https://linkedin.com/in/mohanlal-satapathy)
