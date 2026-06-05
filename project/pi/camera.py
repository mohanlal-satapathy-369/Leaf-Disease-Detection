# ============================================================
# FILE: pi/camera.py
# PURPOSE: Capture leaf image and detect disease
#          Mode 1 → Plant.id API (easier, no model needed)
#          Mode 2 → Local TFLite model (offline capable)
# ============================================================

import requests
import base64
import numpy as np
import time
import config

# ── Capture Image from Pi Camera ──────────────────────────
def capture_leaf_image(filename="leaf.jpg"):
    """Captures a photo using Pi Camera and saves it"""
    from picamera2 import Picamera2
    camera = Picamera2()
    camera.configure(
        camera.create_still_configuration(
            main={"size": (1280, 720)}
        )
    )
    camera.start()
    time.sleep(2)   # Warm up camera
    camera.capture_file(filename)
    camera.stop()
    print(f"[Camera] Image captured → {filename}")
    return filename


# ── MODE 1: Plant.id API Detection (Recommended) ──────────
def detect_disease_api(image_path):
    """
    Sends leaf image to Plant.id API and returns disease info.
    Free tier allows 100 requests/day — enough for demos.
    Get free API key at: https://plant.id
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "api_key": config.PLANTID_API_KEY,
        "images": [image_data],
        "modifiers": ["health_all"],
        "plant_details": ["common_names", "url"],
        "disease_details": ["description", "treatment"]
    }

    try:
        response = requests.post(
            "https://api.plant.id/v2/health_assessment",
            json=payload,
            timeout=15
        )
        data = response.json()

        # Parse response
        is_healthy = data["health_assessment"]["is_healthy"]

        if is_healthy:
            result = {
                "status"    : "Healthy",
                "disease"   : "None",
                "confidence": 99.0,
                "treatment" : "No action needed"
            }
        else:
            diseases = data["health_assessment"]["diseases"]
            top_disease = diseases[0]
            result = {
                "status"    : "Diseased",
                "disease"   : top_disease["name"],
                "confidence": round(top_disease["probability"] * 100, 2),
                "treatment" : top_disease.get(
                    "disease_details", {}
                ).get("treatment", {}).get("biological", "Consult expert")
            }

        print(f"[Disease API] {result['disease']} — {result['confidence']}%")
        return result

    except Exception as e:
        print(f"[Disease API] Error: {e}")
        return {
            "status"    : "Error",
            "disease"   : "API Failed",
            "confidence": 0,
            "treatment" : "Check internet connection"
        }


# ── MODE 2: Local TFLite Model (Offline) ──────────────────
def detect_disease_local(image_path):
    """
    Uses the TFLite model trained on Google Colab.
    Copy plant_disease_model.tflite and class_names.txt to Pi first.
    Works fully offline.
    """
    import tflite_runtime.interpreter as tflite
    from PIL import Image

    # Load class names
    with open(config.CLASS_NAMES_PATH, "r") as f:
        class_names = [line.strip() for line in f.readlines()]

    # Load model
    interpreter = tflite.Interpreter(model_path=config.MODEL_PATH)
    interpreter.allocate_tensors()
    input_details  = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Preprocess image
    img = Image.open(image_path).resize((128, 128))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    predicted_index = np.argmax(output)
    confidence      = round(float(np.max(output)) * 100, 2)
    disease_name    = class_names[predicted_index]
    is_healthy      = "healthy" in disease_name.lower()

    result = {
        "status"    : "Healthy" if is_healthy else "Diseased",
        "disease"   : disease_name,
        "confidence": confidence,
        "treatment" : "No action needed" if is_healthy else "Check plant immediately"
    }

    print(f"[Disease Local] {result['disease']} — {result['confidence']}%")
    return result


# ── Main Detection Function ────────────────────────────────
def run_disease_detection():
    """
    Captures image and runs detection based on config mode.
    Returns result dictionary.
    """
    image_path = capture_leaf_image("leaf.jpg")

    if config.USE_API_MODE:
        return detect_disease_api(image_path)
    else:
        return detect_disease_local(image_path)
