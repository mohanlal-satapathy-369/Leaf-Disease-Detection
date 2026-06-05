# ============================================================
# FILE: pi/config.py
# PURPOSE: Central config — edit this file with your credentials
# ============================================================

# ── Adafruit IO Credentials ────────────────────────────────
ADAFRUIT_USERNAME = "your_adafruit_username"
ADAFRUIT_KEY      = "your_adafruit_io_key"

# ── Plant.id API (Free tier — get key at plant.id) ─────────
PLANTID_API_KEY   = "your_plantid_api_key"

# ── GPIO Pin Numbers (BCM mode) ────────────────────────────
PIN_SOIL_MOISTURE  = 17   # Soil moisture sensor (digital out)
PIN_DHT            = 4    # DHT11 / DHT22 data pin
PIN_LDR            = 27   # LDR sensor (digital out)
PIN_RAIN           = 22   # Rain sensor (digital out)
PIN_PIR            = 23   # PIR motion sensor
PIN_ULTRASONIC_TRIG= 24   # Ultrasonic trigger
PIN_ULTRASONIC_ECHO= 25   # Ultrasonic echo
PIN_SMOKE          = 5    # MQ-2 smoke sensor
PIN_RELAY_PUMP     = 18   # Relay controlling water pump

# ── Sensor Settings ────────────────────────────────────────
DHT_SENSOR_TYPE    = "DHT22"  # Change to "DHT11" if using DHT11

# ── Thresholds ─────────────────────────────────────────────
SOIL_DRY_THRESHOLD     = 1     # 1 = dry, 0 = wet (digital sensor)
TEMP_HIGH_THRESHOLD    = 35    # Celsius — alert if above this
HUMIDITY_LOW_THRESHOLD = 30    # % — alert if below this
SMOKE_THRESHOLD        = 1     # 1 = smoke detected
ANIMAL_DISTANCE_CM     = 50    # Alert if animal closer than this

# ── Watering Settings ──────────────────────────────────────
PUMP_DURATION_SECONDS  = 5     # How long pump runs each cycle
WATERING_INTERVAL_MINS = 30    # Check soil every 30 minutes

# ── Disease Detection Settings ─────────────────────────────
DISEASE_CHECK_INTERVAL_MINS = 60   # Take leaf photo every 60 mins
MODEL_PATH      = "plant_disease_model.tflite"
CLASS_NAMES_PATH= "class_names.txt"
USE_API_MODE    = True   # True = Plant.id API, False = local TFLite

# ── LCD Settings ───────────────────────────────────────────
LCD_I2C_ADDRESS = 0x27   # Default I2C address (try 0x3F if not working)
LCD_COLUMNS     = 16
LCD_ROWS        = 2
