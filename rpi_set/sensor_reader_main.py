import pandas as pd
import joblib
import RPi.GPIO as GPIO
import time
import serial

# ==== Load ML model and feature names ====
model = joblib.load("irrigation_model.pkl")
features = joblib.load("irrigation_features.pkl")  # ['temperature', 'humidity', 'soil_moisture']

# ==== Setup Relay ====
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

print("Pump status: OFF before prediction")

# ==== Setup Serial (Arduino UNO usually at /dev/ttyACM0) ====
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)
    time.sleep(2)  # Wait for Arduino to reset
except Exception as e:
    print("⚠️  Could not open serial port:", e)
    GPIO.cleanup()
    exit()

try:
    print("Waiting for sensor data from Arduino...")
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print("Raw from Arduino:", line)
            try:
                # Clean and parse the array
                line = line.strip("[]")
                all_values = [float(x.strip()) for x in line.split(',')]
                if len(all_values) != 7:
                    print(f"❌ Expected 7 values, got {len(all_values)}. Skipping...")
                    continue

                # Display all 7 sensor readings
                print("\n📋 Full Sensor Data:")
                print(f"Nitrogen:       {all_values[0]}")
                print(f"Phosphorus:     {all_values[1]}")
                print(f"Potassium:      {all_values[2]}")
                print(f"Temperature:    {all_values[3]} °C")
                print(f"Humidity:       {all_values[4]} %")
                print(f"Soil pH:        {all_values[5]}")
                print(f"Soil Moisture:  {all_values[6]} %")

                # Extract relevant data for irrigation model
                values = [
                    all_values[3],  # temperature
                    all_values[4],  # humidity
                    all_values[6]   # soil moisture
                ]
                break

            except Exception as e:
                print("❌ Parsing error:", e)

    # ==== Create DataFrame and Predict ====
    data = pd.DataFrame([values], columns=features)
    prediction = model.predict(data)[0]

    print(f"\n✅ Model Prediction: {prediction}")

    if prediction == 1:
        print("🚿 Turning pump ON for 30 seconds...")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(30)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("✅ Pump turned OFF.")
    else:
        print("🛑 No watering needed. Pump stays OFF.")

    ######sensor_data.json#######
    import json

    sensor_dict = {
        "nitrogen": all_values[0],
        "phosphorus": all_values[1],
        "potassium": all_values[2],
        "temperature": all_values[3],
        "humidity": all_values[4],
        "soil_pH": all_values[5],
        "soil_moisture": all_values[6],
        "irrigation_prediction": "ON" if prediction == 1 else "OFF"
    }

    with open("/home/aanchal/Desktop/Smart_Irrigation_Dashboard/sensor_data.json", "w") as f:

        json.dump(sensor_dict, f)


finally:
    GPIO.cleanup()
    ser.close()

