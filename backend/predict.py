from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np


# Load the trained model once when the backend starts
model = load_model("model/waste_classifier.h5")


# Class names must match the training order
classes = [
    "cardboard",
    "glass",
    "metal",
    "paper",
    "plastic",
    "trash"
]


def predict_single_image(image_path):

    # Open image and convert it to RGB
    img = Image.open(image_path).convert("RGB")

    # Resize image to the size expected by the model
    img = img.resize((224, 224))

    # Convert image to NumPy array and normalize pixels
    img_array = np.array(img) / 255.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Make prediction
    prediction = model.predict(img_array, verbose=0)

    # Find class with highest probability
    predicted_index = np.argmax(prediction[0])

    # Get class name
    predicted_class = classes[predicted_index]

    # Get confidence
    confidence = float(prediction[0][predicted_index])

    return predicted_class, confidence