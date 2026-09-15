import os
import io
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "waste_classifier.h5")
IMG_SIZE = (224, 224)
CLASSES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

DISPOSAL_INFO = {
    "cardboard": {"bin": "Dry / Recyclable Waste", "tip": "Flatten boxes and keep them dry before recycling."},
    "glass":     {"bin": "Dry / Recyclable Waste", "tip": "Rinse the item and separate from mixed waste; handle carefully."},
    "metal":     {"bin": "Dry / Recyclable Waste", "tip": "Empty and rinse cans before placing in the recyclables bin."},
    "paper":     {"bin": "Dry / Recyclable Waste", "tip": "Keep paper clean and dry; soiled paper isn't recyclable."},
    "plastic":   {"bin": "Dry / Recyclable Waste", "tip": "Rinse containers and check the recycling symbol if unsure."},
    "trash":     {"bin": "General Waste", "tip": "This item isn't easily recyclable — dispose of it as general waste."},
}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
CORS(app)

print("Loading model, please wait...")
model = load_model(MODEL_PATH)
print("Model loaded successfully.")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided. Use form field name 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use png, jpg, jpeg, or webp."}), 400

    try:
        file_bytes = file.read()
        img_array = preprocess_image(file_bytes)

        prediction = model.predict(img_array)[0]
        predicted_index = int(np.argmax(prediction))
        predicted_class = CLASSES[predicted_index]
        confidence = float(prediction[predicted_index])
        probabilities = {CLASSES[i]: float(prediction[i]) for i in range(len(CLASSES))}

        return jsonify({
            "success": True,
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "disposal": DISPOSAL_INFO.get(predicted_class, {}),
        })
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)