# from flask import Flask, render_template, request, jsonify
# import os
# import json
# import serial
# import time
# import threading

# # ==== Setup Flask ====
# template_path = os.path.join(os.path.dirname(__file__), 'templates')
# static_path = os.path.join(os.path.dirname(__file__), 'static')
# app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# # ==== ML Imports ====
# from ml_logic.predict_crop_logic import predict_crop
# from ml_logic.predict_irrigation_logic import predict_irrigation

# # ==== Global Sensor Cache ====
# latest_sensor_data = {}

# # ==== Try to open serial port ====
# try:
#     ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
#     time.sleep(2)  # Let Arduino reset
#     print("✅ Serial connected.")
# except Exception as e:
#     print(f"[ERROR] Could not connect to Arduino: {e}")
#     ser = None

# # ==== Background Serial Reader ====
# def read_serial_data():
#     global latest_sensor_data
#     while True:
#         try:
#             if ser and ser.in_waiting:
#                 line = ser.readline().decode('utf-8').strip()
#                 print("[SERIAL DATA]", line)
#                 if not line:
#                     continue
#                 values = [float(x.strip()) for x in line.strip("[]").split(",")]
#                 if len(values) != 7:
#                     continue

#                 latest_sensor_data = {
#                     'nitrogen': values[0],
#                     'phosphorus': values[1],
#                     'potassium': values[2],
#                     'temperature': values[3],
#                     'humidity': values[4],
#                     'ph': values[5],
#                     'moisture': values[6],
#                     'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
#                 }
#         except Exception as e:
#             print(f"[ERROR] Reading serial: {e}")
#         time.sleep(1)

# # ==== Flask Routes ====
# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/api/sensor_data', methods=['GET'])
# def get_sensor_data():
#     if latest_sensor_data:
#         return jsonify(latest_sensor_data)
#     return '', 204

# @app.route('/predict_crop', methods=['POST'])
# def crop_prediction():
#     try:
#         data = request.json
#         result = predict_crop(data)
#         return jsonify({'crop': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/predict_irrigation', methods=['POST'])
# def irrigation_prediction():
#     try:
#         data = request.json
#         result = predict_irrigation(data)
#         return jsonify({'pump_status': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/upload_sensor_data', methods=['POST'])
# def upload_sensor_data():
#     try:
#         data = request.json
#         with open('sensor_data.json', 'w') as f:
#             json.dump(data, f)
#         return jsonify({'status': 'success'})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Start Background Thread ====
# if ser:
#     threading.Thread(target=read_serial_data, daemon=True).start()

# # ==== Run App ====
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, render_template, request, jsonify
import os
import json

# ==== Flask app setup ====
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== ML logic ====
from ml_logic.predict_crop_logic import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ==== Routes ====

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        with open("sensor_data.json", "r") as f:
            data = json.load(f)
        
        # Normalize keys for frontend consistency
        return jsonify({
            "nitrogen": data.get("nitrogen", 0),
            "phosphorus": data.get("phosphorus", 0),
            "potassium": data.get("potassium", 0),
            "temperature": data.get("temperature", 0),
            "humidity": data.get("humidity", 0),
            "ph": data.get("soil_pH", 0),
            "moisture": data.get("soil_moisture", 0),
            "irrigation_prediction": data.get("irrigation_prediction", "OFF")
        })
    except Exception as e:
        print("[ERROR] reading sensor_data.json:", e)
        return jsonify({}), 204  # No content

@app.route('/predict_crop', methods=['POST'])
def crop_prediction():
    try:
        data = request.json
        result = predict_crop(data)
        return jsonify({'crop': result, 'reason': "Recommended based on conditions"})
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

# ==== Start server ====
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
