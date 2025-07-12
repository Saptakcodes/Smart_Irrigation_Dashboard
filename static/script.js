/* =========================================================
   Smart‑Irrigation Dashboard – main client script
   Works with app.py that owns the Arduino serial port
   ========================================================= */

const CONFIG = {
  API_BASE_URL: window.location.origin,      // auto‑detect http://<host>:5000
  UPDATE_INTERVAL: 5000,                     // ms
  WEATHER_UPDATE_INTERVAL: 300000,           // ms
  MOISTURE_THRESHOLD: 30,
  PH_THRESHOLD_LOW: 5.5,
  PH_THRESHOLD_HIGH: 7.5,
  WEATHER_API_KEY: "your_weatherapi_key_here"
};

/* ---------- Icons ---------- */
const CROP_ICONS = { Rice: "🌾", Maize: "🌽", Potato: "🥔", Cotton: "🌸", Sugarcane: "🎋" };
const WEATHER_ICONS = {
  Sunny: "☀️", Clear: "🌞", "Partly cloudy": "⛅", Cloudy: "☁️",
  Rain: "🌧️", Overcast: "🌫️", Mist: "🌫️", Thunderstorm: "🌩️", Snow: "❄️"
};

/* ---------- DOM Shortcuts ---------- */
const $ = id => document.getElementById(id);
const elements = {
  connectionStatus: $("connectionStatus"), connectionText: $("connectionText"),

  moistureValue: $("moistureValue"), moistureProgress: $("moistureProgress"),
  moistureStatus: $("moistureStatus"), moistureUpdated: $("moistureUpdated"),

  nitrogenValue: $("nitrogenValue"), phosphorusValue: $("phosphorusValue"),
  potassiumValue: $("potassiumValue"), npkUpdated: $("npkUpdated"),

  temperatureValue: $("temperatureValue"), humidityValue: $("humidityValue"),
  climateStatus: $("climateStatus"), climateUpdated: $("climateUpdated"),

  phValue: $("phValue"), phProgress: $("phProgress"),
  phStatus: $("phStatus"), phUpdated: $("phUpdated"),

  irrigationStatus: $("irrigationStatus"), lastWatering: $("lastWatering"),
  waterLevel: $("waterLevel"), systemUpdated: $("systemUpdated"),

  systemModeToggle: $("systemModeToggle"), systemModeText: $("systemModeText"),

  lastSync: $("lastSync"),

  singleCropRecommendation: $("singleCropRecommendation"),
  npkSummary: $("npkSummary"), tempSummary: $("tempSummary"),
  humiditySummary: $("humiditySummary"), moistureSummary: $("moistureSummary"),
  cropsUpdated: $("cropsUpdated"),

  irrigationButton: $("irrigationButton"),

  weatherIcon: $("weatherIcon"), weatherTemp: $("weatherTemp"),
  weatherDesc: $("weatherDesc"), feelsLike: $("feelsLike"),
  pressure: $("pressure"), windSpeed: $("windSpeed"), weatherUpdated: $("weatherUpdated"),

  manualIrrigationControls: $("manualIrrigationControls"),
  startIrrigation: $("startIrrigation"), stopIrrigation: $("stopIrrigation"),
  irrigationDurationOptions: $("irrigationDurationOptions")
};

/* ---------- Theme Toggle ---------- */
const themeToggle = $("themeToggle");
themeToggle.addEventListener("click", () => {
  const root = document.documentElement;
  const isDark = root.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  themeToggle.querySelector(".fa-moon").classList.toggle("hidden", isDark);
  themeToggle.querySelector(".fa-sun").classList.toggle("hidden", !isDark);
});

/* ---------- Init on DOM ready ---------- */
window.addEventListener("DOMContentLoaded", () => {
  // initial theme
  const savedTheme = localStorage.getItem("theme");
  const root = document.documentElement;
  const isDark = savedTheme === "dark" ||
                 (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches);
  root.classList.toggle("dark", isDark);
  themeToggle.querySelector(".fa-moon").classList.toggle("hidden", isDark);
  themeToggle.querySelector(".fa-sun").classList.toggle("hidden", !isDark);

  // set manual / auto button states
  toggleManualMode(elements.systemModeToggle.checked);

  // start polling
  refreshData();
  fetchWeather();
  setInterval(refreshData,  CONFIG.UPDATE_INTERVAL);
  setInterval(fetchWeather, CONFIG.WEATHER_UPDATE_INTERVAL);
});

/* ---------- Manual / Auto Toggle ---------- */
elements.systemModeToggle.addEventListener("change", () => {
  toggleManualMode(elements.systemModeToggle.checked);
});
function toggleManualMode(isManual) {
  elements.systemModeText.textContent = isManual ? "Manual" : "Auto";
  elements.irrigationButton.disabled  = !isManual;
  elements.manualIrrigationControls.classList.toggle("hidden", !isManual);
  elements.irrigationButton.classList.toggle("opacity-50", !isManual);
  elements.irrigationButton.classList.toggle("cursor-not-allowed", !isManual);
}

/* ---------- Fetch Helpers ---------- */
async function fetchSensorData() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/api/sensor_data`);
    if (!res.ok) throw new Error(res.status);
    if (res.status === 204) return null;       // no data yet
    return await res.json();
  } catch (err) {
    console.error("Sensor fetch error:", err);
    return null;
  }
}

async function fetchWeather() {
  if (!CONFIG.WEATHER_API_KEY || CONFIG.WEATHER_API_KEY === "your_weatherapi_key_here") return;
  try {
    const res = await fetch(`https://api.weatherapi.com/v1/current.json?key=${CONFIG.WEATHER_API_KEY}&q=auto:ip`);
    if (!res.ok) throw new Error(res.status);
    updateWeatherUI(await res.json());
  } catch (e) {
    console.error("Weather fetch error:", e);
  }
}

/* ---------- UI Updates ---------- */
function updateSensorUI(data) {
  if (!data) return;   // no data yet

  const now = new Date();

  /* Moisture */
  elements.moistureValue.textContent     = data.moisture ?? "--";
  elements.moistureProgress.style.width  = `${data.moisture ?? 0}%`;
  elements.moistureStatus.textContent    = data.moisture < CONFIG.MOISTURE_THRESHOLD ? "Irrigation Needed" : "Optimal";
  elements.moistureUpdated.textContent   = now.toLocaleTimeString();

  /* NPK */
  elements.nitrogenValue.textContent     = data.nitrogen ?? "--";
  elements.phosphorusValue.textContent   = data.phosphorus ?? "--";
  elements.potassiumValue.textContent    = data.potassium ?? "--";
  elements.npkUpdated.textContent        = now.toLocaleTimeString();

  /* Climate */
  elements.temperatureValue.textContent  = data.temperature ?? "--";
  elements.humidityValue.textContent     = data.humidity ?? "--";
  elements.climateUpdated.textContent    = now.toLocaleTimeString();

  /* pH */
  elements.phValue.textContent           = data.ph ?? "--";
  elements.phProgress.style.width        = `${((data.ph ?? 0) / 14) * 100}%`;
  elements.phStatus.textContent =
      data.ph < CONFIG.PH_THRESHOLD_LOW  ? "Too Acidic"  :
      data.ph > CONFIG.PH_THRESHOLD_HIGH ? "Too Alkaline": "Optimal";
  elements.phUpdated.textContent         = now.toLocaleTimeString();

  /* System + Summary */
  const statusDot = data.irrigation_prediction === "ON" ? "green" : "gray";
  const statusTxt = data.irrigation_prediction === "ON" ? "Active" : "Standby";
  elements.irrigationStatus.innerHTML = `
    <span class="status-indicator-small w-2 h-2 rounded-full bg-${statusDot}-500 animate-pulse-slow"></span> ${statusTxt}`;
  elements.systemUpdated.textContent = now.toLocaleTimeString();
  elements.lastWatering.textContent  = "Just Now";
  elements.waterLevel.textContent    = `${Math.floor(Math.random() * 30 + 70)}%`;
  elements.lastSync.textContent      = now.toLocaleTimeString();

  /* Summary mini‑cards */
  elements.npkSummary.textContent     = `N:${data.nitrogen} P:${data.phosphorus} K:${data.potassium}`;
  elements.tempSummary.textContent    = `${data.temperature}°C`;
  elements.humiditySummary.textContent= `${data.humidity}%`;
  elements.moistureSummary.textContent= `${data.moisture}%`;
}

function updateWeatherUI(data) {
  const c = data.current;
  const icon = WEATHER_ICONS[c.condition.text] || "🌤️";
  elements.weatherIcon.textContent   = icon;
  elements.weatherTemp.textContent   = `${c.temp_c}°C`;
  elements.weatherDesc.textContent   = c.condition.text;
  elements.feelsLike.textContent     = `${c.feelslike_c}°C`;
  elements.pressure.textContent      = `${c.pressure_mb} hPa`;
  elements.windSpeed.textContent     = `${c.wind_kph} km/h`;
  elements.weatherUpdated.textContent= new Date().toLocaleTimeString();
}

/* ---------- Crop Recommendation ---------- */
async function fetchCropRecommendation(data) {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/predict_crop`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(res.status);
    return (await res.json()).crop;
  } catch (e) {
    console.error("Crop recommendation error:", e);
    return "Unknown";
  }
}
function updateCropRecommendationUI(crop) {
  const icon = CROP_ICONS[crop] || "🌱";
  elements.singleCropRecommendation.innerHTML = `
    <div class="text-center">
      <div class="text-6xl mb-2">${icon}</div>
      <div class="text-xl font-bold">${crop}</div>
      <div class="text-green-600 dark:text-green-300 mt-2">Recommended by AI</div>
    </div>`;
  elements.cropsUpdated.textContent = new Date().toLocaleTimeString();
}

/* ---------- Public buttons ---------- */
window.refreshData = async () => {
  const sensor = await fetchSensorData();
  updateSensorUI(sensor);
  if (sensor) {
    const crop = await fetchCropRecommendation(sensor);
    updateCropRecommendationUI(crop);
  }
};

window.exportData = async () => {
  const sensor = await fetchSensorData();
  const blob   = new Blob([JSON.stringify(sensor, null, 2)], { type: "application/json" });
  const url    = URL.createObjectURL(blob);
  const a      = document.createElement("a");
  a.href = url; a.download = `sensor_data_${Date.now()}.json`; a.click();
  URL.revokeObjectURL(url);
};

window.manualIrrigation = () => {
  if (!elements.systemModeToggle.checked) return alert("Switch to Manual mode first.");
  alert("Manual irrigation controls enabled.");
};

/* ---------- Manual irrigation buttons ---------- */
elements.startIrrigation.addEventListener("click", () => {
  elements.irrigationDurationOptions.classList.toggle("hidden");
});
document.querySelectorAll(".duration-btn").forEach(btn =>
  btn.addEventListener("click", () => {
    const mins = btn.dataset.minutes;
    alert(`✅ Irrigation started for ${mins} minutes.`);
    elements.irrigationDurationOptions.classList.add("hidden");
  })
);
elements.stopIrrigation.addEventListener("click", () => {
  alert("🛑 Irrigation stopped manually.");
});

/* ---------- Helper for connection UI ---------- */
function setConnection(connected) {
  elements.connectionStatus.className =
      `status-dot w-3 h-3 rounded-full bg-${connected ? "green" : "red"}-500 ${connected ? "animate-pulse-slow" : ""}`;
  elements.connectionText.textContent = connected ? "Connected" : "Disconnected";
}

/* ---------- Main poll loop ---------- */
async function refreshData() {
  const data = await fetchSensorData();
  if (data) {
    setConnection(true);
    updateSensorUI(data);
    const crop = await fetchCropRecommendation(data);
    updateCropRecommendationUI(crop);
  } else {
    setConnection(false);
  }
}


/**pump */
async function callPump(url) {
  await fetch(url, { method: "POST" });
}

elements.startIrrigation.addEventListener("click", () => {
  callPump("/pump/on");
  alert("✅ Pump started (manual)");
});

elements.stopIrrigation.addEventListener("click", () => {
  callPump("/pump/off");
  alert("🛑 Pump stopped");
});


//pump manual
async function sendIrrigationCommand(mins) {
  await fetch("/start_manual_irrigation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ minutes: mins })
  });
  alert(`🚿 Pump will run for ${mins} min`);
}

document.querySelectorAll(".duration-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const mins = parseInt(btn.dataset.minutes, 10);
    sendIrrigationCommand(mins);
    elements.irrigationDurationOptions.classList.add("hidden");
  });
});

// ────────────────────────────────────────────────
//  GET irrigation recommendation
async function fetchIrrigationNeeded() {
  const res = await fetch("/api/irrigation_needed");
  if (!res.ok) return null;
  const { needed } = await res.json();
  return needed;   // true / false
}

// // update the card
// function updateIrrigationNeededUI(needed) {
//   const answer = needed ? "YES ✅" : "NO 🛑";
//   const el = document.getElementById("irrigationNeededAnswer");
//   const stamp = document.getElementById("irrigationNeededUpdated");

//   el.textContent = answer;
//   el.className =
//     "text-center text-4xl font-bold py-6 rounded-xl transition-all duration-300 " +
//     (needed
//       ? "bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-200 border border-red-300 dark:border-red-700"
//       : "bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-200 border border-green-300 dark:border-green-700");

//   stamp.textContent = new Date().toLocaleTimeString();
// }

// // call it whenever you refresh sensor data
// async function refreshData() {
//   const sensor = await fetchSensorData();
//   if (!sensor) return;

//   updateSensorUI(sensor);

//   // NEW: irrigation needed?
//   const needed = await fetchIrrigationNeeded();
//   if (needed !== null) updateIrrigationNeededUI(needed);

//   // crop recommendation as before …
// }

// 🔁 Poll irrigation_needed every 5 seconds
async function updateIrrigationCard() {
    try {
        const res = await fetch("/api/irrigation_needed");
        if (!res.ok) return;
        const data = await res.json();

        const answerBox = document.getElementById("irrigationNeededAnswer");
        const updateTime = document.getElementById("irrigationNeededUpdated");

        if (data.needed) {
            answerBox.textContent = "YES";
            answerBox.classList.add("text-green-600");
            answerBox.classList.remove("text-red-600");
        } else {
            answerBox.textContent = "NO";
            answerBox.classList.add("text-red-600");
            answerBox.classList.remove("text-green-600");
        }

        updateTime.textContent = new Date().toLocaleTimeString();

    } catch (err) {
        console.error("Failed to fetch irrigation prediction:", err);
    }
}

// Call on load and every 5 seconds
document.addEventListener("DOMContentLoaded", () => {
    updateIrrigationCard();
    setInterval(updateIrrigationCard, 5000);
});




