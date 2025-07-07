# # from flask import Flask, render_template, request, jsonify
# # import os
# # import json

# # # ==== Imports from your logic files ====
# # from ml_logic.predict_crop_logic import predict_crop
# # from ml_logic.predict_irrigation_logic import predict_irrigation

# # # ==== Flask app setup ====
# # template_path = os.path.join(os.path.dirname(__file__), 'templates')
# # static_path = os.path.join(os.path.dirname(__file__), 'static')

# # app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# # # ==== Home Route ====
# # @app.route('/')
# # def home():
# #     return render_template('index.html')

# # # ==== Crop Prediction API ====
# # @app.route('/predict_crop', methods=['POST'])
# # def crop_prediction():
# #     try:
# #         data = request.json
# #         result = predict_crop(data)
# #         return jsonify({'prediction': result})
# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500

# # # ==== Irrigation Prediction API ====
# # @app.route('/predict_irrigation', methods=['POST'])
# # def irrigation_prediction():
# #     try:
# #         data = request.json
# #         result = predict_irrigation(data)
# #         return jsonify({'pump_status': result})
# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500

# # # ==== Sensor Data API ====
# # @app.route('/api/sensor_data', methods=['GET'])
# # def get_sensor_data():
# #     try:
# #         with open('sensor_data.json', 'r') as f:
# #             data = json.load(f)
# #         return jsonify(data)
# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500

# # # ==== Run the App ====
# # if __name__ == '__main__':
# #     # app.run(debug=True)
# #     #accessing on different devices
# #     app.run(host='0.0.0.0', port=5000, debug=True)


# from flask import Flask, render_template, request, jsonify
# import os
# import json
# import serial  # For real-time Arduino data

# # ==== Flask app setup ====
# template_path = os.path.join(os.path.dirname(__file__), 'templates')
# static_path = os.path.join(os.path.dirname(__file__), 'static')

# app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# # ==== Import ML logic ====
# from ml_logic.predict_crop_logic import predict_crop
# from ml_logic.predict_irrigation_logic import predict_irrigation

# # ==== Serial Port Setup ====
# # Update the port to match your system
# try:
#     ser = serial.Serial('dev/ttyACM0', 9600, timeout=5)
#  # ⬅️ CHANGE this if needed (e.g., 'COM3' on Windows)
# except Exception as e:
#     print(f"[ERROR] Could not connect to Arduino: {e}")
#     ser = None

# # ==== Routes ====

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/predict_crop', methods=['POST'])
# def crop_prediction():
#     try:
#         data = request.json
#         result = predict_crop(data)
#         return jsonify({'prediction': result})
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

# @app.route('/api/sensor_data', methods=['GET'])
# def get_sensor_data():
#     if not ser:
#         return jsonify({'error': 'Arduino not connected'}), 500

#     try:
#         if ser.in_waiting:
#             line = ser.readline().decode('utf-8').strip()
#             print("[SERIAL DATA]", line)
#             data = json.loads(line)
#             return jsonify(data)
#         else:
#             return jsonify({'error': 'No data from Arduino yet'}), 204
#     except Exception as e:
#         return jsonify({'error': f'Serial read error: {str(e)}'}), 500


# @app.route('/upload_sensor_data', methods=['POST'])
# def upload_sensor_data():
#     try:
#         data = request.json
#         with open('sensor_data.json', 'w') as f:
#             json.dump(data, f)
#         return jsonify({'status': 'success'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Run App ====
# if __name__ == '__main__':
#     #app.run(debug=True)
#     app.run(host='0.0.0.0', port=5000, debug=True) #for similar ip 


# from flask import Flask, render_template, request, jsonify
# import os
# import json
# import serial

# # ==== Flask app setup ====
# template_path = os.path.join(os.path.dirname(__file__), 'templates')
# static_path = os.path.join(os.path.dirname(__file__), 'static')
# app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# # ==== Import ML logic ====
# from ml_logic.predict_crop_logic import predict_crop
# from ml_logic.predict_irrigation_logic import predict_irrigation

# # ==== Serial Port Setup (Arduino) ====
# try:
#     ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)  # ✅ FIXED PATH
# except Exception as e:
#     print(f"[ERROR] Could not connect to Arduino: {e}")
#     ser = None

# # ==== Routes ====
# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/predict_crop', methods=['POST'])
# def crop_prediction():
#     try:
#         data = request.json
#         result = predict_crop(data)
#         return jsonify({'prediction': result})
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

# @app.route('/api/sensor_data', methods=['GET'])
# def get_sensor_data():
#     if not ser:
#         return jsonify({'error': 'Arduino not connected'}), 500

#     try:
#         line = ser.readline().decode('utf-8').strip()
#         if not line:
#             return jsonify({'error': 'Empty serial data'}), 204

#         print("[SERIAL DATA]", line)
#         line = line.strip("[]")
#         values = [float(x.strip()) for x in line.split(',')]

#         if len(values) != 7:
#             return jsonify({'error': 'Invalid sensor data length'}), 400

#         data = {
#             'nitrogen': values[0],
#             'phosphorus': values[1],
#             'potassium': values[2],
#             'temperature': values[3],
#             'humidity': values[4],
#             'ph': values[5],
#             'moisture': values[6],
#             'timestamp': json.dumps(str(line))
#         }
#         return jsonify(data)

#     except Exception as e:
#         return jsonify({'error': f'Serial read error: {str(e)}'}), 500


# @app.route('/upload_sensor_data', methods=['POST'])
# def upload_sensor_data():
#     try:
#         data = request.json
#         with open('sensor_data.json', 'w') as f:
#             json.dump(data, f)
#         return jsonify({'status': 'success'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ==== Run App ====
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)








import threading
import serial
import time
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

latest_sensor_data = {}
ser = None

# Background thread function
def read_serial_data():
    global latest_sensor_data
    while True:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                print("[SERIAL DATA]", line)
                if not line:
                    continue
                parts = line.strip("[]").split(",")
                if len(parts) != 7:
                    continue
                values = [float(x.strip()) for x in parts]

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
            print("Error reading serial:", e)
        time.sleep(1)  # adjust if needed

# API to get cached data
@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    if latest_sensor_data:
        return jsonify(latest_sensor_data)
    else:
        return '', 204

# Try to open serial
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    print("✅ Serial connected.")
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Could not connect to Arduino: {e}")

# Start background thread
if ser:
    threading.Thread(target=read_serial_data, daemon=True).start()

# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
