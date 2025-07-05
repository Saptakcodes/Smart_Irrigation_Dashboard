import pandas as pd
import joblib
import RPi.GPIO as GPIO
import time

# Load model and features
model = joblib.load("irrigation_model.pkl")
features = joblib.load("irrigation_features.pkl")

RELAY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)  # Safer setup

print("Pump status: OFF before prediction")

try:
    input_values = []
    print("?? Enter values for the following features:")
    for feature in features:
        val = float(input(f"{feature}: "))
        input_values.append(val)

    data = pd.DataFrame([input_values], columns=features)
    prediction = model.predict(data)[0]
    print(f"?? Model Prediction: {prediction}")

    if prediction == 1:
        print("?? Turning pump ON for 30 seconds...")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(30)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("? Pump turned OFF")
    else:
        print("?? No watering needed. Pump stays OFF.")
finally:
    GPIO.cleanup()
