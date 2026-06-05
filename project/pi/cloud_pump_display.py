# ============================================================
# FILE: pi/cloud.py
# PURPOSE: Send all data to Adafruit IO cloud dashboard
# ============================================================

from Adafruit_IO import Client
import config

aio = Client(config.ADAFRUIT_USERNAME, config.ADAFRUIT_KEY)

def send_sensor_data(sensor_data):
    """Push all sensor readings to Adafruit IO feeds"""
    try:
        if sensor_data["temperature"]:
            aio.send_data('temperature', sensor_data["temperature"])
        if sensor_data["humidity"]:
            aio.send_data('humidity', sensor_data["humidity"])
        aio.send_data('soil-moisture', 'Dry' if sensor_data["soil_dry"] else 'Wet')
        aio.send_data('light',         'Bright' if sensor_data["light"] else 'Dark')
        aio.send_data('rain',          'Raining' if sensor_data["raining"] else 'Clear')
        aio.send_data('smoke',         'SMOKE!' if sensor_data["smoke"] else 'Clear')
        print("[Cloud] Sensor data sent ✅")
    except Exception as e:
        print(f"[Cloud] Error sending sensor data: {e}")


def send_disease_result(disease_result):
    """Push disease detection result to Adafruit IO"""
    try:
        message = f"{disease_result['disease']} ({disease_result['confidence']}%)"
        aio.send_data('plant-disease', message)
        print(f"[Cloud] Disease result sent: {message} ✅")
    except Exception as e:
        print(f"[Cloud] Error sending disease result: {e}")


def send_alert(alert_message):
    """Send emergency alerts to Adafruit IO"""
    try:
        aio.send_data('alerts', alert_message)
        print(f"[Cloud] Alert sent: {alert_message} ✅")
    except Exception as e:
        print(f"[Cloud] Error sending alert: {e}")


# ============================================================
# FILE: pi/pump.py
# PURPOSE: Control the water pump via relay
# ============================================================

import RPi.GPIO as GPIO
import time
import config

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.PIN_RELAY_PUMP, GPIO.OUT)
GPIO.output(config.PIN_RELAY_PUMP, GPIO.LOW)   # Pump OFF by default


def pump_on():
    GPIO.output(config.PIN_RELAY_PUMP, GPIO.HIGH)
    print("[Pump] 💧 Water pump ON")


def pump_off():
    GPIO.output(config.PIN_RELAY_PUMP, GPIO.LOW)
    print("[Pump] Water pump OFF")


def water_plant(duration=None):
    """Turn pump on for set duration then off"""
    if duration is None:
        duration = config.PUMP_DURATION_SECONDS
    pump_on()
    time.sleep(duration)
    pump_off()
    print(f"[Pump] Watered for {duration} seconds ✅")


def smart_water(sensor_data, disease_result):
    """
    Decide whether to water based on:
    - Soil moisture
    - Rain detection
    - Disease status (water less if diseased)
    """
    if sensor_data["raining"]:
        print("[Pump] Skipping watering — it is raining 🌧️")
        return "skipped_rain"

    if not sensor_data["soil_dry"]:
        print("[Pump] Skipping watering — soil is already wet 💧")
        return "skipped_wet"

    if sensor_data["soil_dry"]:
        if disease_result["status"] == "Diseased":
            # Water less when plant is diseased
            print("[Pump] Diseased plant — watering briefly")
            water_plant(duration=2)
            return "watered_brief"
        else:
            water_plant()
            return "watered_normal"

    return "no_action"


# ============================================================
# FILE: pi/display.py
# PURPOSE: Show readings on I2C LCD 16x2 display
# ============================================================

from RPLCD.i2c import CharLCD
import config
import time

lcd = CharLCD(
    i2c_expander='PCF8574',
    address=config.LCD_I2C_ADDRESS,
    port=1,
    cols=config.LCD_COLUMNS,
    rows=config.LCD_ROWS
)


def clear():
    lcd.clear()


def show_message(line1, line2=""):
    """Display two lines on LCD"""
    lcd.clear()
    lcd.write_string(line1[:16])
    if line2:
        lcd.crlf()
        lcd.write_string(line2[:16])


def show_sensor_data(sensor_data):
    """Cycle through sensor readings on LCD"""
    readings = [
        (f"Temp:{sensor_data['temperature']}C",
         f"Hum:{sensor_data['humidity']}%"),
        (f"Soil:{'Dry' if sensor_data['soil_dry'] else 'Wet'}",
         f"Rain:{'Yes' if sensor_data['raining'] else 'No'}"),
        (f"Light:{'On' if sensor_data['light'] else 'Off'}",
         f"Smoke:{'YES!' if sensor_data['smoke'] else 'No'}"),
    ]
    for line1, line2 in readings:
        show_message(line1, line2)
        time.sleep(3)


def show_disease_result(disease_result):
    """Show disease detection result on LCD"""
    show_message(
        disease_result["status"],
        disease_result["disease"][:16]
    )
    time.sleep(5)


def show_alert(message):
    """Flash alert on LCD"""
    for _ in range(3):
        show_message("!! ALERT !!", message[:16])
        time.sleep(0.5)
        clear()
        time.sleep(0.5)
    show_message("!! ALERT !!", message[:16])
