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
latest_sensor_data = {}          # in‑memory cache
JSON_PATH = os.path.join(BASE_DIR, "sensor_data.json")  # optional on‑disk copy

# ==== Open serial once ====
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)
    time.sleep(2)
    print("✅ Serial connected.")
except Exception as e:
    print(f"[ERROR] Could not open /dev/ttyACM0: {e}")
    ser = None

# ==== Background thread to read Arduino ====
def read_serial_loop():
    while True:
        try:
            if ser and ser.in_waiting:
                raw = ser.readline().decode('utf-8').strip()
                if raw:
                    vals = [float(x.strip()) for x in raw.strip("[]").split(",")]
                    if len(vals) != 7:
                        continue

                    # update cache
                    latest_sensor_data.update({
                        "nitrogen":   vals[0],
                        "phosphorus": vals[1],
                        "potassium":  vals[2],
                        "temperature":vals[3],
                        "humidity":   vals[4],
                        "ph":         vals[5],
                        "moisture":   vals[6],
                        "timestamp":  time.strftime('%Y-%m-%d %H:%M:%S')
                    })

                    # (optional) also dump to file so you can inspect it
                    with open(JSON_PATH, "w") as f:
                        json.dump(latest_sensor_data, f)

        except Exception as e:
            print(f"[ERROR] Serial read: {e}")
        time.sleep(0.5)

if ser:
    threading.Thread(target=read_serial_loop, daemon=True).start()

# ==== Routes ====
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/sensor_data")
def api_sensor_data():
    if not latest_sensor_data:
        return jsonify({"error": "No data yet"}), 204
    return jsonify(latest_sensor_data)

@app.route("/predict_crop", methods=["POST"])
def api_predict_crop():
    try:
        result = predict_crop(request.json)
        return jsonify({"crop": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/predict_irrigation", methods=["POST"])
def api_predict_irrigation():
    try:
        result = predict_irrigation(request.json)
        return jsonify({"pump_status": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# optional manual upload endpoint remains
@app.route("/upload_sensor_data", methods=["POST"])
def upload_sensor_data():
    try:
        with open(JSON_PATH, "w") as f:
            json.dump(request.json, f)
        latest_sensor_data.update(request.json)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==== Run ====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
