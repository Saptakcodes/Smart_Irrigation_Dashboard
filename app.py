from flask import Flask, render_template, request, jsonify
import os
import json

# ==== Imports from your logic files ====
from ml_logic.predict_crop_logic import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ==== Flask app setup ====
template_path = os.path.join(os.path.dirname(__file__), 'templates')
static_path = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== Home Route ====
@app.route('/')
def home():
    return render_template('index.html')

# ==== Crop Prediction API ====
@app.route('/predict_crop', methods=['POST'])
def crop_prediction():
    try:
        data = request.json
        result = predict_crop(data)
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== Irrigation Prediction API ====
@app.route('/predict_irrigation', methods=['POST'])
def irrigation_prediction():
    try:
        data = request.json
        result = predict_irrigation(data)
        return jsonify({'pump_status': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== Sensor Data API ====
@app.route('/api/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        with open('sensor_data.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==== Run the App ====
if __name__ == '__main__':
    # app.run(debug=True)
    #accessing on different devices
    app.run(host='0.0.0.0', port=5000, debug=True)


