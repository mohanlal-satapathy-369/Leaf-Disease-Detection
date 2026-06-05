# ============================================================
# FILE: pi/main.py
# PURPOSE: Main script — runs the entire system in a loop
# HOW TO RUN: python3 main.py
# ============================================================

import time
import config
import sensors
import camera
import cloud
import display

# Split intervals into seconds
SENSOR_INTERVAL  = config.WATERING_INTERVAL_MINS * 60
DISEASE_INTERVAL = config.DISEASE_CHECK_INTERVAL_MINS * 60

last_disease_check = 0   # Track when we last ran disease detection


def check_alerts(sensor_data):
    """Check all sensor thresholds and send alerts if needed"""
    alerts = []

    if sensor_data["temperature"] and \
       sensor_data["temperature"] > config.TEMP_HIGH_THRESHOLD:
        alerts.append(f"High Temp: {sensor_data['temperature']}C")

    if sensor_data["humidity"] and \
       sensor_data["humidity"] < config.HUMIDITY_LOW_THRESHOLD:
        alerts.append(f"Low Humidity: {sensor_data['humidity']}%")

    if sensor_data["smoke"]:
        alerts.append("SMOKE DETECTED!")

    if sensor_data["motion"] and \
       sensor_data["distance_cm"] < config.ANIMAL_DISTANCE_CM:
        alerts.append(f"Animal at {sensor_data['distance_cm']}cm!")

    for alert in alerts:
        print(f"[ALERT] {alert}")
        cloud.send_alert(alert)
        display.show_alert(alert)

    return alerts


def main():
    global last_disease_check

    print("=" * 40)
    print("  Smart Plant Monitoring System")
    print("  Starting up... 🌱")
    print("=" * 40)

    display.show_message("Plant Monitor", "Starting...")
    time.sleep(2)

    disease_result = {
        "status"    : "Unknown",
        "disease"   : "Not checked yet",
        "confidence": 0,
        "treatment" : "Pending first check"
    }

    while True:
        try:
            print("\n--- New Sensor Cycle ---")

            # ── 1. Read all sensors ────────────────────────
            sensor_data = sensors.read_all_sensors()

            # ── 2. Check for alerts ────────────────────────
            check_alerts(sensor_data)

            # ── 3. Send sensor data to cloud ───────────────
            cloud.send_sensor_data(sensor_data)

            # ── 4. Display sensor readings on LCD ──────────
            display.show_sensor_data(sensor_data)

            # ── 5. Run disease detection periodically ──────
            current_time = time.time()
            if current_time - last_disease_check >= DISEASE_INTERVAL:
                print("\n--- Running Disease Detection ---")
                display.show_message("Detecting...", "Please wait")

                disease_result = camera.run_disease_detection()
                cloud.send_disease_result(disease_result)
                display.show_disease_result(disease_result)

                last_disease_check = current_time

            # ── 6. Smart watering decision ─────────────────
            pump_action = pump.smart_water(sensor_data, disease_result)
            if pump_action.startswith("watered"):
                display.show_message("Watering...", "Pump Active")
            elif pump_action == "skipped_rain":
                display.show_message("Skipped", "Its Raining")
            elif pump_action == "skipped_wet":
                display.show_message("Skipped", "Soil is Wet")

            # ── 7. Wait before next cycle ──────────────────
            print(f"\nNext check in {config.WATERING_INTERVAL_MINS} mins...")
            display.show_message("System Active", "Monitoring...")
            time.sleep(SENSOR_INTERVAL)

        except KeyboardInterrupt:
            print("\n[System] Shutting down gracefully...")
            display.show_message("Shutting down", "Goodbye!")
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            break

        except Exception as e:
            print(f"[System] Unexpected error: {e}")
            display.show_message("Error!", str(e)[:16])
            time.sleep(10)   # Wait and retry


if __name__ == "__main__":
    import pump   # Import here to avoid circular imports
    main()
