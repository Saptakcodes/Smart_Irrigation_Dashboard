from flask import Flask, render_template, request, jsonify
import os, json, serial, time, threading
from ml_logic.predict_irrigation_logic import predict_irrigation

# ---- GPIO setup (safe) ------------------------------------------------
# ------------------------------------------------------------------
# 🟢  GPIO / Pump control – now using pigpio instead of RPi.GPIO
# ------------------------------------------------------------------
import pigpio                         # ← NEW
PUMP_PIN = 17                         # ⚠️ change if your relay is on another pin

pi = pigpio.pi()                      # connect to the pigpio daemon
if not pi.connected:                  #‑‑ fails if pigpiod not running
    print("❌ pigpio daemon not running!  Run: sudo systemctl start pigpiod")
    # fall back to a dummy object so app still works without GPIO
    class _MockPi:
        def write(self, pin, value):              pass
        def set_mode(self, pin, mode):            pass
        def stop(self):                           pass
    pi = _MockPi()
    gpio_available = False
else:
    pi.set_mode(PUMP_PIN, pigpio.OUTPUT)
    pi.write(PUMP_PIN, 0)              # ensure pump is OFF at startup
    print(f"✅ pigpio ready on GPIO {PUMP_PIN}.")
    gpio_available = True
# ----------------------------------------------------------------------



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
    
#############PUMP########################

#PUMP AUTO

@app.route("/start_manual_irrigation", methods=["POST"])
def start_irrigation():
    pi.write(PUMP_PIN, 1)
    return jsonify({"status": "Pump turned ON manually"})

@app.route("/stop_manual_irrigation", methods=["POST"])
def stop_irrigation():
    pi.write(PUMP_PIN, 0)
    return jsonify({"status": "Pump turned OFF manually"})

#PUMP MANUAL
# ---------- Manual / timed pump control ---------------------------------
def _auto_off(delay_s: int):
    time.sleep(delay_s)
    pi.write(PUMP_PIN, 0)
    print(f"⏹️  Pump auto‑stopped after {delay_s//60} min")

@app.route("/start_manual_irrigation", methods=["POST"])
def start_manual_irrigation():
    """
    POST JSON: { "minutes": 5|10|15|30 }
    """
    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", 5))
    if minutes not in (5, 10, 15, 30):
        return jsonify({"error": "Allowed durations: 5, 10, 15, 30"}), 400

    pi.write(PUMP_PIN, 1)
    threading.Thread(target=_auto_off, args=(minutes * 60,), daemon=True).start()
    return jsonify({"status": f"Pump ON for {minutes} minutes"}), 200

@app.route("/stop_manual_irrigation", methods=["POST"])
def stop_manual_irrigation():
    pi.write(PUMP_PIN, 0)
    return jsonify({"status": "Pump OFF manually"}), 200
# ------------------------------------------------------------------------


##########Irrigation Card#########
@app.route("/api/irrigation_needed")
def api_irrigation_needed():
    if not latest_sensor_data:
        return jsonify({"error": "No sensor data"}), 204

    # map keys for the model
    payload = {
        "temperature": latest_sensor_data["temperature"],
        "humidity":    latest_sensor_data["humidity"],
        "soil_moisture": latest_sensor_data["moisture"],
    }
    needed = predict_irrigation(payload)   # returns 1 / 0
    return jsonify({"needed": bool(needed)})



# ==== Run Server ====
# ==== Run Server ====
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,          # keep debugger / hot‑reload off
        use_reloader=False   # <‑‑ THE important line
    )

