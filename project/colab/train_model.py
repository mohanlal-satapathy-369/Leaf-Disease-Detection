# ============================================================
# FILE: colab/train_model.py
# PURPOSE: Run this entirely on Google Colab (free GPU)
# STEP 1: Upload PlantVillage dataset to Colab or mount Google Drive
# ============================================================

# ── STEP 1: Install dependencies ──────────────────────────
# Run this cell first in Colab
# !pip install tensorflow matplotlib numpy

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten,
    Dense, Dropout, BatchNormalization
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np
import os

# ── STEP 2: Mount Google Drive (if dataset is there) ──────
# Uncomment below if your dataset is in Google Drive
# from google.colab import drive
# drive.mount('/content/drive')
# DATASET_PATH = '/content/drive/MyDrive/PlantVillage/'

# If uploading directly to Colab session:
DATASET_PATH = '/content/PlantVillage/'
IMAGE_SIZE   = (128, 128)
BATCH_SIZE   = 32
EPOCHS       = 15

# ── STEP 3: Load and augment dataset ──────────────────────
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    shear_range=0.1
)

train_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    subset='training',
    class_mode='categorical'
)

val_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    subset='validation',
    class_mode='categorical'
)

# Save class names for later use on Raspberry Pi
class_names = list(train_data.class_indices.keys())
print("Classes found:", class_names)
print("Total training samples:", train_data.samples)
print("Total validation samples:", val_data.samples)

# ── STEP 4: Build CNN Model ────────────────────────────────
model = Sequential([
    # Block 1
    Conv2D(32, (3, 3), activation='relu', padding='same',
           input_shape=(128, 128, 3)),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    # Block 2
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    # Block 3
    Conv2D(128, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    # Classifier
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(train_data.num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ── STEP 5: Train the model ────────────────────────────────
callbacks = [
    EarlyStopping(patience=3, restore_best_weights=True),
    ModelCheckpoint('best_model.h5', save_best_only=True)
]

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    callbacks=callbacks
)

# ── STEP 6: Plot accuracy and loss ────────────────────────
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Model Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.legend()

plt.savefig('training_results.png')
plt.show()

# ── STEP 7: Convert to TFLite for Raspberry Pi ────────────
model = tf.keras.models.load_model('best_model.h5')

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Smaller file size
tflite_model = converter.convert()

with open('plant_disease_model.tflite', 'wb') as f:
    f.write(tflite_model)

# Save class names to a text file
with open('class_names.txt', 'w') as f:
    for name in class_names:
        f.write(name + '\n')

print("\n✅ Done! Download these 2 files and copy to Raspberry Pi:")
print("   → plant_disease_model.tflite")
print("   → class_names.txt")

# ── STEP 8: Quick test on a sample image ──────────────────
def predict_sample(image_path):
    from tensorflow.keras.preprocessing import image
    img = image.load_img(image_path, target_size=IMAGE_SIZE)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = np.max(predictions) * 100

    print(f"Predicted: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    return predicted_class, confidence

# Usage: predict_sample('/path/to/test/leaf.jpg')
