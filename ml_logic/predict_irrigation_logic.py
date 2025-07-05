import pandas as pd
import joblib

# Load model and feature list once
model = joblib.load("rpi_set/irrigation_model.pkl")
features = joblib.load("rpi_set/irrigation_features.pkl")  # ['temperature', 'humidity', 'soil_moisture']

def predict_irrigation(input_dict):
    """
    Accepts a dictionary with 3 inputs and returns "ON" or "OFF".
    """
    try:
        # Convert to DataFrame
        input_df = pd.DataFrame([input_dict])

        # Reorder to match model training order
        input_df = input_df[features]

        prediction = model.predict(input_df)[0]
        return "ON" if prediction == 1 else "OFF"

    except Exception as e:
        return f"❌ Error during irrigation prediction: {e}"
