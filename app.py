from flask import Flask, render_template, request, jsonify
import os, json

# ==== Setup Flask ====
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path     = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== ML Imports ====
from ml_logic.predict_crop_logic       import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ------------------------------------------------------------------
# Serial / background reader DISABLED because sensor_reader_main.py
# already owns /dev/ttyACM0 and writes sensor_data.json for us.
# ------------------------------------------------------------------
# import serial, time, threading
# latest_sensor_data = {}
#
# try:
#     ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
#     time.sleep(2)
#     print("✅ Serial connected (inside app.py).")
# except Exception as e:
#     print(f"[ERROR] Could not connect to Arduino: {e}")
#     ser = None
#
# def read_serial_data():
#     global latest_sensor_data
#     while True:
#         try:
#             if ser and ser.in_waiting:
#                 line = ser.readline().decode('utf-8').strip()
#                 if not line:
#                     continue
#                 vals = [float(x.strip()) for x in line.strip("[]").split(",")]
#                 if len(vals) != 7:
#                     continue
#                 latest_sensor_data = {
#                     'nitrogen': vals[0], 'phosphorus': vals[1], 'potassium': vals[2],
#                     'temperature': vals[3], 'humidity': vals[4], 'ph': vals[5],
#                     'moisture': vals[6], 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
#                 }
#                 with open("sensor_data.json", "w") as f:
#                     json.dump(latest_sensor_data, f)
#         except Exception as e:
#             print(f"[ERROR] Serial read: {e}")
#         time.sleep(1)
#
# if ser:
#     threading.Thread(target=read_serial_data, daemon=True).start()

# ==== Flask Routes ====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sensor_data')
def get_sensor_data():
    """
    Front‑end polls this endpoint every few seconds.
    We simply read the JSON file written by sensor_reader_main.py.
    """
    try:
        with open("sensor_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({'error': 'sensor_data.json not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'sensor_data.json is invalid'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_crop', methods=['POST'])
def crop_prediction():
    try:
        result = predict_crop(request.json)
        return jsonify({'crop': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_irrigation', methods=['POST'])
def irrigation_prediction():
    try:
        result = predict_irrigation(request.json)
        return jsonify({'pump_status': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_sensor_data', methods=['POST'])
def upload_sensor_data():
    """Optional manual upload endpoint."""
    try:
        with open("sensor_data.json", "w") as f:
            json.dump(request.json, f)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== Run App ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
