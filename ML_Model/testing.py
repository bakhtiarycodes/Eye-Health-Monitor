import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(FILE_DIR, "blink_random_forest_model.pkl")

# ============================================
# Load Trained Model
# ============================================

rf_model = joblib.load(MODEL_PATH)

# ============================================
# Recreate Label Encoder
# ============================================

label_encoder = LabelEncoder()

# IMPORTANT:
# Same order used during training
label_encoder.classes_ = np.array([
    "Fatigue_Dryness",
    "Normal"
])

if __name__ == "__main__":
    print("✅ Model loaded successfully from", MODEL_PATH)

    # ============================================
    # New Sample
    # ============================================

    new_sample = pd.DataFrame({
        "Blink_Rate": [30],
        "Blink_Duration": [0.45],
        "Incomplete_Blink_Ratio": [0.60]
    })

    # ============================================
    # Prediction
    # ============================================

    prediction = rf_model.predict(new_sample)
    predicted_class = label_encoder.inverse_transform(prediction)

    # ============================================
    # Output
    # ============================================

    print("\nPrediction Result")
    print("-----------------")
    print("Blink Rate:", new_sample["Blink_Rate"][0])
    print("Blink Duration:", new_sample["Blink_Duration"][0])
    print("Incomplete Blink Ratio:", new_sample["Incomplete_Blink_Ratio"][0])
    print("\nPredicted Class:", predicted_class[0])