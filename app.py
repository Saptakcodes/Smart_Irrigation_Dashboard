# from flask import Flask, render_template, request, jsonify
# import os
# import json

# # ==== Imports from your logic files ====
# from ml_logic.predict_crop_logic import predict_crop
# from ml_logic.predict_irrigation_logic import predict_irrigation

# # ==== Flask app setup ====
# template_path = os.path.join(os.path.dirname(__file__), 'templates')
# static_path = os.path.join(os.path.dirname(__file__), 'static')

# app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# # ==== Home Route ====
# @app.route('/')
# def home():
#     return render_template('index.html')

# # ==== Crop Prediction API ====
# @app.route('/predict_crop', methods=['POST'])
# def crop_prediction():
#     try:
#         data = request.json
#         result = predict_crop(data)
#         return jsonify({'prediction': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Irrigation Prediction API ====
# @app.route('/predict_irrigation', methods=['POST'])
# def irrigation_prediction():
#     try:
#         data = request.json
#         result = predict_irrigation(data)
#         return jsonify({'pump_status': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Sensor Data API ====
# @app.route('/api/sensor_data', methods=['GET'])
# def get_sensor_data():
#     try:
#         with open('sensor_data.json', 'r') as f:
#             data = json.load(f)
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Run the App ====
# if __name__ == '__main__':
#     # app.run(debug=True)
#     #accessing on different devices
#     app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, render_template, request, jsonify
import os
import json
import serial  # For real-time Arduino data

# ==== Flask app setup ====
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== Import ML logic ====
from ml_logic.predict_crop_logic import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ==== Serial Port Setup ====
# Update the port to match your system
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)  # ⬅️ CHANGE this if needed (e.g., 'COM3' on Windows)
except Exception as e:
    print(f"[ERROR] Could not connect to Arduino: {e}")
    ser = None

# ==== Routes ====

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_crop', methods=['POST'])
def crop_prediction():
    try:
        data = request.json
        result = predict_crop(data)
        return jsonify({'prediction': result})
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

@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    if not ser:
        return jsonify({'error': 'Arduino not connected'}), 500

    try:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print("[SERIAL DATA]", line)
            data = json.loads(line)
            return jsonify(data)
        else:
            return jsonify({'error': 'No data from Arduino yet'}), 204
    except Exception as e:
        return jsonify({'error': f'Serial read error: {str(e)}'}), 500

# ==== Run App ====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
