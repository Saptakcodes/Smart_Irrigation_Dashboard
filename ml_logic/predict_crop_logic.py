import pandas as pd
import joblib

# Load model and label encoder once
model = joblib.load("rpi_set/crop_model.pkl")
label_encoder = joblib.load("rpi_set/label_encoder.pkl")

# Define feature order (optional safety)
expected_columns = [
    'nitrogen', 'phosphorus', 'potassium',
    'temperature', 'humidity', 'soil_pH', 'soil_moisture'
]

def predict_crop(input_dict):
    """
    Accepts a dictionary with 7 inputs and returns the recommended crop.
    """
    try:
        # Convert to DataFrame
        input_df = pd.DataFrame([input_dict])

        # Reorder columns to match training
        input_df = input_df[expected_columns]

        # Predict (encoded)
        encoded_prediction = model.predict(input_df)

        # Decode to actual crop name
        actual_prediction = label_encoder.inverse_transform(encoded_prediction)

        return actual_prediction[0]

    except Exception as e:
        return f"❌ Error during prediction: {e}"
