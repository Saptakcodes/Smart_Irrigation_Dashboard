import joblib
import pandas as pd

model = joblib.load('crop_model.pkl')
le = joblib.load('label_encoder.pkl')

print("🔎 Enter the following values:")

n = float(input("Nitrogen: "))
p = float(input("Phosphorus: "))
k = float(input("Potassium: "))
temp = float(input("Temperature (°C): "))
humidity = float(input("Humidity (%): "))
soil_pH = float(input("Soil pH: "))
soil_moisture = float(input("Soil Moisture (%): "))

input_data = pd.DataFrame([{
    'nitrogen': n,
    'phosphorus': p,
    'potassium': k,
    'temperature': temp,
    'humidity': humidity,
    'soil_pH': soil_pH,
    'soil_moisture': soil_moisture
}])

# OPTIONAL: Reorder columns to match training
df = pd.read_csv("crop_dataset.csv")
input_data = input_data[df.columns[:-1]]

encoded_prediction = model.predict(input_data)
actual_prediction = le.inverse_transform(encoded_prediction)

print("\n✅ Recommended Crop:", actual_prediction[0])
