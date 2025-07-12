from flask import Flask, render_template, request, jsonify
import os, json, serial, time, threading

# ==== Flask setup ====
BASE_DIR      = os.path.dirname(__file__)
template_path = os.path.join(BASE_DIR, 'templates')
static_path   = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# ==== ML logic ====
from ml_logic.predict_crop_logic       import predict_crop
from ml_logic.predict_irrigation_logic import predict_irrigation

# ==== Globals ====
latest_sensor_data = {}  # in-memory cache
JSON_PATH = os.path.join(BASE_DIR, "sensor_data.json")

# ==== Setup Serial Port ====
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    time.sleep(2)
    print("✅ Serial connected to /dev/ttyACM0.")
except Exception as e:
    print(f"❌ Serial connection failed: {e}")
    ser = None

# ==== Background Serial Reader ====
def read_serial_loop():
    while True:
        try:
            if ser and ser.in_waiting:
                raw = ser.readline().decode('utf-8').strip()
                print("📥 Raw from Arduino:", raw)

                if not raw:
                    continue

                values = [float(x.strip()) for x in raw.strip("[]").split(",")]

                if len(values) != 7:
                    print(f"❌ Expected 7 values, got {len(values)} — Skipping")
                    continue

                latest_sensor_data.update({
                    "nitrogen": values[0],
                    "phosphorus": values[1],
                    "potassium": values[2],
                    "temperature": values[3],
                    "humidity": values[4],
                    "ph": values[5],
                    "moisture": values[6],
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                })

                print("✅ Parsed Sensor Data:", latest_sensor_data)

                # Save to file
                with open(JSON_PATH, "w") as f:
                    json.dump(latest_sensor_data, f)

        except Exception as e:
            print(f"[ERROR] Serial Read Loop: {e}")
        time.sleep(1)

if ser:
    threading.Thread(target=read_serial_loop, daemon=True).start()

# ==== Flask Routes ====
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/sensor_data", methods=["GET"])
def api_sensor_data():
    if not latest_sensor_data:
        print("⚠️  No sensor data yet")
        return '', 204
    print("📤 Returning sensor data to frontend:", latest_sensor_data)
    return jsonify(latest_sensor_data), 200

# in app.py
@app.route("/predict_crop", methods=["POST"])
def api_predict_crop():
    try:
        data = request.json.copy()

        # map frontend → model names
        data["soil_pH"]        = data.pop("ph",        None)
        data["soil_moisture"]  = data.pop("moisture",  None)

        result = predict_crop(data)
        return jsonify({"crop": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict_irrigation", methods=["POST"])
def api_predict_irrigation():
    try:
        result = predict_irrigation(request.json)
        return jsonify({"pump_status": result})
    except Exception as e:
        print(f"❌ Irrigation Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/upload_sensor_data", methods=["POST"])
def upload_sensor_data():
    try:
        data = request.json
        with open(JSON_PATH, "w") as f:
            json.dump(data, f)
        latest_sensor_data.update(data)
        print("📦 Manual upload received and saved:", latest_sensor_data)
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return jsonify({"error": str(e)}), 500

# ==== Run Server ====
# ==== Run Server ====
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,          # keep debugger / hot‑reload off
        use_reloader=False   # <‑‑ THE important line
    )

