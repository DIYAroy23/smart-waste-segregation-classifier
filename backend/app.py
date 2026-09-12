from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from predict import predict_single_image
from database import initialize_database, save_scan, get_history


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500"
            ]
        }
    }
)


# Folder where uploaded images will be stored
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Waste information
waste_info = {

    "cardboard": {
        "category": "Recyclable",
        "bin": "Blue Bin",
        "disposal": "Keep cardboard dry and clean, flatten it, and place it in the recycling bin."
    },

    "glass": {
        "category": "Recyclable",
        "bin": "Blue Bin",
        "disposal": "Empty and rinse glass containers. Handle broken glass carefully and follow local disposal rules."
    },

    "metal": {
        "category": "Recyclable",
        "bin": "Blue Bin",
        "disposal": "Empty and clean metal containers before placing them in the recycling bin."
    },

    "paper": {
        "category": "Recyclable",
        "bin": "Blue Bin",
        "disposal": "Keep paper clean and dry and place it in the recycling bin."
    },

    "plastic": {
        "category": "Recyclable",
        "bin": "Blue Bin",
        "disposal": "Empty and rinse plastic containers before placing them in the recycling bin."
    },

    "trash": {
        "category": "Non-Recyclable",
        "bin": "General Waste Bin",
        "disposal": "Place non-recyclable waste in the general waste bin."
    }
}


# Initialize database when server starts
initialize_database()


@app.route("/")
def home():

    return jsonify({
        "message": "Smart Waste Segregation Classifier API is running"
    })


@app.route("/predict", methods=["POST"])
def predict():

    # Check whether an image was uploaded
    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400


    file = request.files["image"]


    # Check that a file was actually selected
    if file.filename == "":

        return jsonify({
            "error": "No image selected"
        }), 400


    # Save uploaded image
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)


    try:

        # Run the ML model
        predicted_class, confidence = predict_single_image(
            file_path
        )


        # Get additional information
        info = waste_info[predicted_class]


        # Save result in database
        save_scan(
            file.filename,
            predicted_class,
            confidence,
            info["category"],
            info["bin"],
            info["disposal"]
        )


        # Return result to frontend
        return jsonify({

            "success": True,

            "prediction": predicted_class,

            "confidence": round(confidence * 100, 2),

            "category": info["category"],

            "bin": info["bin"],

            "disposal": info["disposal"]

        })


    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/history", methods=["GET"])
def history():

    records = get_history()

    return jsonify({
        "success": True,
        "history": records
    })


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )