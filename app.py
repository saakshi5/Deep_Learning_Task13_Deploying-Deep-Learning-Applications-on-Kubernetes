
from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
import numpy as np
import tensorflow as tf
import io

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import (
    preprocess_input,
    decode_predictions
)

app = Flask(__name__)

# Limit uploaded images to 10 MB.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Load pretrained model once when the container starts.
model = MobileNetV2(
    weights="imagenet",
    include_top=True
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "Task 13 Deep Learning Prediction API",
        "model": "MobileNetV2",
        "status": "running",
        "endpoints": {
            "health": "/healthz",
            "model_info": "/model-info",
            "prediction": "/predict"
        }
    })


@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/model-info", methods=["GET"])
def model_info():
    return jsonify({
        "model_name": "MobileNetV2",
        "dataset": "ImageNet",
        "input_size": "224x224 RGB",
        "task": "Image classification",
        "framework": "TensorFlow / Keras"
    }), 200


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({
            "error": "Missing image file. Use form field 'image'."
        }), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({
            "error": "No image file selected."
        }), 400

    try:
        image_bytes = file.read()

        if not image_bytes:
            return jsonify({
                "error": "The uploaded file is empty."
            }), 400

        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize((224, 224))

    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify({
            "error": "Invalid image file. Upload a valid image."
        }), 400

    try:
        image_array = np.array(image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = preprocess_input(image_array)

        predictions = model.predict(
            image_array,
            verbose=0
        )

        results = decode_predictions(
            predictions,
            top=3
        )[0]

        top_predictions = [
            {
                "label": label,
                "class_id": class_id,
                "confidence": round(float(score), 4)
            }
            for class_id, label, score in results
        ]

        return jsonify({
            "model": "MobileNetV2",
            "prediction": top_predictions[0]["label"],
            "confidence": top_predictions[0]["confidence"],
            "top_3_predictions": top_predictions
        }), 200

    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "Prediction failed. Check application logs."
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image exceeds the 10 MB upload limit."
    }), 413


if __name__ == "__main__":
    # Listen on all container interfaces.
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
