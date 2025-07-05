import pandas as pd
import joblib
import RPi.GPIO as GPIO
import time
import serial

# Load model and feature order
model = joblib.load("irrigation_model.pkl")
features = joblib.load("irrigation_features.pkl")  # ['temperature', 'humidity', 'soil_moisture']

# Setup GPIO pin for pump
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

# Setup Serial port for Arduino
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)
    time.sleep(2)  # Allow time for Arduino to reset
except Exception as e:
    print("⚠️ Could not open serial port:", e)
    GPIO.cleanup()
    exit()

try:
    print("📡 Waiting for sensor data from Arduino...")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue

        # Expected format: [n, p, k, temp, humidity, ph, soil_moisture]
        try:
            line = line.strip("[]")  # remove brackets
            parts = [float(x.strip()) for x in line.split(',')]

            if len(parts) != 7:
                print(f"❌ Expected 7 values, got {len(parts)}. Skipping line.")
                continue

            # Extract only the required features
            temp = parts[3]
            humidity = parts[4]
            soil_moisture = parts[6]

            # Create DataFrame
            input_data = pd.DataFrame([{
                'temperature': temp,
                'humidity': humidity,
                'soil_moisture': soil_moisture
            }])[features]  # Ensures correct column order

            # Predict irrigation need
            prediction = model.predict(input_data)[0]

            # Display the received values
            print("\n🌱 Sensor Readings:")
            print(f"🌡️  Temperature:     {temp} °C")
            print(f"💧 Humidity:        {humidity} %")
            print(f"🌾 Soil Moisture:   {soil_moisture} %")

            # Display result and act
            if prediction == 1:
                print("🚿 Irrigation needed → Turning pump ON for 30 seconds...")
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                time.sleep(30)
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print("✅ Pump turned OFF.")
            else:
                print("🛑 No irrigation needed. Pump remains OFF.")

            # Optional delay between cycles (e.g., wait for next sensor reading)
            print("⏳ Waiting for next reading...\n")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Error processing line: {line} — {e}")

finally:
    GPIO.cleanup()
    ser.close()




