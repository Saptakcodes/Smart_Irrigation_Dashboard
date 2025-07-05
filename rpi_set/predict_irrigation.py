import joblib
import pandas as pd

# Load model and feature list
model = joblib.load("irrigation_model.pkl")
features = joblib.load("irrigation_features.pkl")

# Take user input
print("🔎 Enter the following values:")

temp = float(input("Temperature (°C): "))
humidity = float(input("Humidity (%): "))
soil_moisture = float(input("Soil Moisture (%): "))

# Create input data
input_data = pd.DataFrame([{
    'temperature': temp,
    'humidity': humidity,
    'soil_moisture': soil_moisture
}])

# Reorder to match training
input_data = input_data[features]

# Predict
prediction = model.predict(input_data)[0]

# Output
result = "💧 Turn ON the Pump" if prediction == 1 else "🚫 No Irrigation Needed"
print("\n✅ Prediction Result:", result)
