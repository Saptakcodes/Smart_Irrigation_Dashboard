from flask import Flask, render_template, request, jsonify
import os
import json
import serial
import time
import threading

# ==== Setup Flask ====
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== ML Imports ====
from ml_logic.predict_crop_logic import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ==== Global Sensor Cache ====
latest_sensor_data = {}

# ==== Try to open serial port ====
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    time.sleep(2)  # Let Arduino reset
    print("✅ Serial connected.")
except Exception as e:
    print(f"[ERROR] Could not connect to Arduino: {e}")
    ser = None

# ==== Background Serial Reader ====
def read_serial_data():
    global latest_sensor_data
    while True:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                print("[SERIAL DATA]", line)
                if not line:
                    continue
                values = [float(x.strip()) for x in line.strip("[]").split(",")]
                if len(values) != 7:
                    continue

                latest_sensor_data = {
                    'nitrogen': values[0],
                    'phosphorus': values[1],
                    'potassium': values[2],
                    'temperature': values[3],
                    'humidity': values[4],
                    'ph': values[5],
                    'moisture': values[6],
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            print(f"[ERROR] Reading serial: {e}")
        time.sleep(1)

# ==== Flask Routes ====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        with open("/home/aanchal/Desktop/Smart_Irrigation_Dashboard/sensor_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({'error': 'sensor_data.json not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'sensor_data.json is not valid JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_crop', methods=['POST'])
def crop_prediction():
    try:
        data = request.json
        result = predict_crop(data)
        return jsonify({'crop': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_irrigation', methods=['POST'])
def irrigation_prediction():
    try:
        data = request.json
        result = predict_irrigation(data)
        return jsonify({'pump_status': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_sensor_data', methods=['POST'])
def upload_sensor_data():
    try:
        data = request.json
        with open('sensor_data.json', 'w') as f:
            json.dump(data, f)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== Start Background Thread ====
if ser:
    threading.Thread(target=read_serial_data, daemon=True).start()

# ==== Run App ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
