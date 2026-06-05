# ============================================================
# FILE: pi/sensors.py
# PURPOSE: Read data from all sensors connected to GPIO pins
# ============================================================

import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import config

# ── GPIO Setup ─────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(config.PIN_SOIL_MOISTURE,   GPIO.IN)
GPIO.setup(config.PIN_LDR,             GPIO.IN)
GPIO.setup(config.PIN_RAIN,            GPIO.IN)
GPIO.setup(config.PIN_PIR,             GPIO.IN)
GPIO.setup(config.PIN_SMOKE,           GPIO.IN)
GPIO.setup(config.PIN_ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(config.PIN_ULTRASONIC_ECHO, GPIO.IN)

# ── DHT Sensor Setup ───────────────────────────────────────
if config.DHT_SENSOR_TYPE == "DHT22":
    dht_sensor = adafruit_dht.DHT22(board.D4)
else:
    dht_sensor = adafruit_dht.DHT11(board.D4)


# ── Soil Moisture ──────────────────────────────────────────
def read_soil_moisture():
    """Returns True if soil is DRY, False if WET"""
    value = GPIO.input(config.PIN_SOIL_MOISTURE)
    is_dry = value == config.SOIL_DRY_THRESHOLD
    print(f"[Soil] {'DRY 🔴' if is_dry else 'WET 🟢'}")
    return is_dry


# ── Temperature & Humidity ─────────────────────────────────
def read_dht():
    """Returns (temperature_C, humidity_%) or (None, None) on error"""
    try:
        temperature = dht_sensor.temperature
        humidity    = dht_sensor.humidity
        print(f"[DHT] Temp: {temperature}°C | Humidity: {humidity}%")
        return temperature, humidity
    except RuntimeError as e:
        print(f"[DHT] Read error: {e}")
        return None, None


# ── Light (LDR) ────────────────────────────────────────────
def read_light():
    """Returns True if there IS light, False if dark"""
    value = GPIO.input(config.PIN_LDR)
    has_light = value == 0   # LDR outputs 0 when light is detected
    print(f"[Light] {'Bright 🌞' if has_light else 'Dark 🌙'}")
    return has_light


# ── Rain Sensor ────────────────────────────────────────────
def read_rain():
    """Returns True if it IS raining"""
    value = GPIO.input(config.PIN_RAIN)
    is_raining = value == 0   # 0 = rain detected
    print(f"[Rain] {'Raining 🌧️' if is_raining else 'No Rain ☀️'}")
    return is_raining


# ── PIR Motion Sensor ──────────────────────────────────────
def read_pir():
    """Returns True if motion detected"""
    motion = GPIO.input(config.PIN_PIR) == 1
    if motion:
        print("[PIR] Motion Detected! 🚨")
    return motion


# ── Ultrasonic Distance ────────────────────────────────────
def read_ultrasonic():
    """Returns distance in centimeters"""
    GPIO.output(config.PIN_ULTRASONIC_TRIG, True)
    time.sleep(0.00001)
    GPIO.output(config.PIN_ULTRASONIC_TRIG, False)

    pulse_start = time.time()
    pulse_end   = time.time()

    while GPIO.input(config.PIN_ULTRASONIC_ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(config.PIN_ULTRASONIC_ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = round(duration * 17150, 2)   # Convert to cm
    print(f"[Ultrasonic] Distance: {distance} cm")
    return distance


# ── Smoke Sensor ───────────────────────────────────────────
def read_smoke():
    """Returns True if smoke is detected"""
    smoke = GPIO.input(config.PIN_SMOKE) == config.SMOKE_THRESHOLD
    if smoke:
        print("[Smoke] ⚠️ SMOKE DETECTED!")
    return smoke


# ── Read All Sensors at Once ───────────────────────────────
def read_all_sensors():
    """Returns a dictionary of all sensor readings"""
    temperature, humidity = read_dht()
    return {
        "soil_dry"   : read_soil_moisture(),
        "temperature": temperature,
        "humidity"   : humidity,
        "light"      : read_light(),
        "raining"    : read_rain(),
        "motion"     : read_pir(),
        "distance_cm": read_ultrasonic(),
        "smoke"      : read_smoke()
    }
