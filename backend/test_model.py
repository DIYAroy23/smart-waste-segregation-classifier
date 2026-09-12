from tensorflow.keras.models import load_model

model = load_model("model/waste_classifier.h5")

print("Model loaded successfully!")
print(model.summary())
