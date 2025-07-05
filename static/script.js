const CONFIG = {
  API_BASE_URL: "http://localhost:5000",
  UPDATE_INTERVAL: 5000,
  WEATHER_UPDATE_INTERVAL: 300000,
  MOISTURE_THRESHOLD: 30,
  PH_THRESHOLD_LOW: 5.5,
  PH_THRESHOLD_HIGH: 7.5,
  WEATHER_API_KEY: "your_weatherapi_key_here"
};

const CROP_ICONS = {
  Rice: "🌾",
  Maize: "🌽",
  Potato: "🥔",
  Cotton: "🌸",
  Sugarcane: "🎋"
};

const WEATHER_ICONS = {
  "Sunny": "☀️",
  "Clear": "🌞",
  "Partly cloudy": "⛅",
  "Cloudy": "☁️",
  "Rain": "🌧️",
  "Overcast": "🌫️",
  "Mist": "🌫️",
  "Thunderstorm": "🌩️",
  "Snow": "❄️"
};

const elements = {
  connectionStatus: document.getElementById("connectionStatus"),
  connectionText: document.getElementById("connectionText"),
  moistureValue: document.getElementById("moistureValue"),
  moistureProgress: document.getElementById("moistureProgress"),
  moistureStatus: document.getElementById("moistureStatus"),
  moistureUpdated: document.getElementById("moistureUpdated"),
  nitrogenValue: document.getElementById("nitrogenValue"),
  phosphorusValue: document.getElementById("phosphorusValue"),
  potassiumValue: document.getElementById("potassiumValue"),
  npkUpdated: document.getElementById("npkUpdated"),
  temperatureValue: document.getElementById("temperatureValue"),
  humidityValue: document.getElementById("humidityValue"),
  climateStatus: document.getElementById("climateStatus"),
  climateUpdated: document.getElementById("climateUpdated"),
  phValue: document.getElementById("phValue"),
  phProgress: document.getElementById("phProgress"),
  phStatus: document.getElementById("phStatus"),
  phUpdated: document.getElementById("phUpdated"),
  irrigationStatus: document.getElementById("irrigationStatus"),
  lastWatering: document.getElementById("lastWatering"),
  waterLevel: document.getElementById("waterLevel"),
  systemUpdated: document.getElementById("systemUpdated"),
  systemModeToggle: document.getElementById("systemModeToggle"),
  systemModeText: document.getElementById("systemModeText"),
  lastSync: document.getElementById("lastSync"),
  singleCropRecommendation: document.getElementById("singleCropRecommendation"),
  npkSummary: document.getElementById("npkSummary"),
  tempSummary: document.getElementById("tempSummary"),
  humiditySummary: document.getElementById("humiditySummary"),
  moistureSummary: document.getElementById("moistureSummary"),
  cropsUpdated: document.getElementById("cropsUpdated"),
  irrigationButton: document.getElementById("irrigationButton"),
  weatherIcon: document.getElementById("weatherIcon"),
  weatherTemp: document.getElementById("weatherTemp"),
  weatherDesc: document.getElementById("weatherDesc"),
  feelsLike: document.getElementById("feelsLike"),
  pressure: document.getElementById("pressure"),
  windSpeed: document.getElementById("windSpeed"),
  weatherUpdated: document.getElementById("weatherUpdated")
};

// ===== THEME TOGGLE =====
const themeToggle = document.getElementById("themeToggle");

themeToggle.addEventListener("click", () => {
  const root = document.documentElement;
  const isDark = root.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");

  const moonIcon = themeToggle.querySelector(".fa-moon");
  const sunIcon = themeToggle.querySelector(".fa-sun");
  if (isDark) {
    moonIcon.classList.add("hidden");
    sunIcon.classList.remove("hidden");
  } else {
    moonIcon.classList.remove("hidden");
    sunIcon.classList.add("hidden");
  }
});

window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");
  const root = document.documentElement;
  const isDark = savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches);
  root.classList.toggle("dark", isDark);

  const moonIcon = themeToggle.querySelector(".fa-moon");
  const sunIcon = themeToggle.querySelector(".fa-sun");
  if (isDark) {
    moonIcon.classList.add("hidden");
    sunIcon.classList.remove("hidden");
  } else {
    moonIcon.classList.remove("hidden");
    sunIcon.classList.add("hidden");
  }

  // INITIALIZE START IRRIGATION BUTTON
  const isManual = elements.systemModeToggle.checked;
  elements.systemModeText.textContent = isManual ? "Manual" : "Auto";
  elements.irrigationButton.disabled = !isManual;
  if (isManual) {
    elements.irrigationButton.classList.remove("opacity-50", "cursor-not-allowed");
  } else {
    elements.irrigationButton.classList.add("opacity-50", "cursor-not-allowed");
  }
});

// ===== MODE TOGGLE =====
elements.systemModeToggle.addEventListener("change", () => {
  const isManual = elements.systemModeToggle.checked;
  elements.systemModeText.textContent = isManual ? "Manual" : "Auto";
  elements.irrigationButton.disabled = !isManual;

  if (isManual) {
    elements.irrigationButton.classList.remove("opacity-50", "cursor-not-allowed");
    elements.irrigationButton.classList.add("hover:-translate-y-0.5", "hover:shadow-lg", "hover:from-blue-600", "hover:to-blue-700");
  } else {
    elements.irrigationButton.classList.add("opacity-50", "cursor-not-allowed");
    elements.irrigationButton.classList.remove("hover:-translate-y-0.5", "hover:shadow-lg", "hover:from-blue-600", "hover:to-blue-700");
  }
});

// ===== SENSOR FETCH =====
async function fetchSensorData() {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/api/sensor_data`);
    if (!res.ok) throw new Error("Failed to load sensor data");
    return await res.json();
  } catch (err) {
    console.error("Sensor Fetch Error:", err);
    return null;
  }
}

// ===== WEATHER FETCH =====
async function fetchWeather() {
  try {
    const res = await fetch(`http://api.weatherapi.com/v1/current.json?key=${CONFIG.WEATHER_API_KEY}&q=auto:ip`);
    if (!res.ok) throw new Error("Failed to fetch weather");
    const data = await res.json();
    updateWeatherUI(data);
  } catch (e) {
    console.error("Weather Error:", e);
  }
}

function updateWeatherUI(data) {
  const current = data.current;
  const icon = WEATHER_ICONS[current.condition.text] || "🌤️";
  elements.weatherIcon.textContent = icon;
  elements.weatherTemp.textContent = `${current.temp_c}°C`;
  elements.weatherDesc.textContent = current.condition.text;
  elements.feelsLike.textContent = `${current.feelslike_c}°C`;
  elements.pressure.textContent = `${current.pressure_mb} hPa`;
  elements.windSpeed.textContent = `${current.wind_kph} km/h`;
  elements.weatherUpdated.textContent = new Date().toLocaleTimeString();
}

// ===== UI UPDATE =====
function updateSensorUI(data) {
  const now = new Date();
  elements.moistureValue.textContent = data.soil_moisture;
  elements.moistureProgress.style.width = `${data.soil_moisture}%`;
  elements.moistureStatus.textContent = data.soil_moisture < CONFIG.MOISTURE_THRESHOLD ? "Irrigation Needed" : "Optimal";
  elements.moistureUpdated.textContent = now.toLocaleTimeString();

  elements.nitrogenValue.textContent = data.nitrogen;
  elements.phosphorusValue.textContent = data.phosphorus;
  elements.potassiumValue.textContent = data.potassium;
  elements.npkUpdated.textContent = now.toLocaleTimeString();

  elements.temperatureValue.textContent = data.temperature;
  elements.humidityValue.textContent = data.humidity;
  elements.climateUpdated.textContent = now.toLocaleTimeString();

  elements.phValue.textContent = data.soil_pH;
  elements.phProgress.style.width = `${(data.soil_pH / 14) * 100}%`;
  elements.phStatus.textContent =
    data.soil_pH < CONFIG.PH_THRESHOLD_LOW
      ? "Too Acidic"
      : data.soil_pH > CONFIG.PH_THRESHOLD_HIGH
      ? "Too Alkaline"
      : "Optimal";
  elements.phUpdated.textContent = now.toLocaleTimeString();

  elements.irrigationStatus.innerHTML = `<span class="status-indicator-small w-2 h-2 rounded-full bg-${data.irrigation_prediction ? "green" : "gray"}-500 animate-pulse-slow"></span> ${data.irrigation_prediction ? "Active" : "Standby"}`;
  elements.systemUpdated.textContent = now.toLocaleTimeString();
  elements.lastWatering.textContent = "Just Now";
  elements.waterLevel.textContent = `${Math.floor(Math.random() * 30 + 70)}%`;
  elements.lastSync.textContent = now.toLocaleTimeString();

  elements.npkSummary.textContent = `N:${data.nitrogen} P:${data.phosphorus} K:${data.potassium}`;
  elements.tempSummary.textContent = `${data.temperature}°C`;
  elements.humiditySummary.textContent = `${data.humidity}%`;
  elements.moistureSummary.textContent = `${data.soil_moisture}%`;
}

// ===== PREDICT CROP =====
async function fetchCropPrediction(data) {
  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/predict_crop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    return result.prediction;
  } catch (err) {
    console.error("Crop Predict Error:", err);
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
    </div>
  `;
  elements.cropsUpdated.textContent = new Date().toLocaleTimeString();
}

// ===== BUTTON ACTIONS =====
window.refreshData = async () => {
  const sensor = await fetchSensorData();
  if (!sensor) return;
  updateSensorUI(sensor);
  const crop = await fetchCropPrediction(sensor);
  updateCropRecommendationUI(crop);
};

window.exportData = async () => {
  const sensor = await fetchSensorData();
  const blob = new Blob([JSON.stringify(sensor, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `sensor_data_${Date.now()}.json`;
  link.click();
};

window.manualIrrigation = () => {
  if (!elements.systemModeToggle.checked) return alert("Switch to Manual mode first.");
  alert("Manual irrigation triggered.");
};

window.dismissAlert = () => {
  document.getElementById("alertContainer").style.display = "none";
};

// ===== INIT =====
window.onload = () => {
  window.refreshData();
  fetchWeather();
  setInterval(window.refreshData, CONFIG.UPDATE_INTERVAL);
  setInterval(fetchWeather, CONFIG.WEATHER_UPDATE_INTERVAL);
};
