/**
 * GestureWave AI – Frontend Logic
 * Polls gesture status and updates the UI in real time.
 */

const GESTURE_ICONS = {
  "Open Palm":     "✋",
  "Pointing":      "☝️",
  "Pinch":         "🤏",
  "Thumbs Up":     "👍",
  "Peace Sign":    "✌️",
  "Three Fingers": "🖖",
  "Four Fingers":  "🖐",
  "Rock Sign":     "🤘",
  "Call Sign":     "🤙",
  "Fist":          "✊",
  "None":          "🖐",
  "Unknown":       "❓"
};

let gestureCount   = 0;
let lastGesture    = "";
let lastActionTime = 0;
let pollInterval   = null;
let camReady       = false;

/* ── DOM refs ──────────────────────────────────────────────────────────────── */
const gestureIcon   = document.getElementById("gestureIcon");
const gestureName   = document.getElementById("gestureName");
const gestureAction = document.getElementById("gestureAction");
const confFill      = document.getElementById("confFill");
const confValue     = document.getElementById("confValue");
const fpsVal        = document.getElementById("fpsVal");
const handVal       = document.getElementById("handVal");
const totalVal      = document.getElementById("totalVal");
const actionLog     = document.getElementById("actionLog");
const statusText    = document.getElementById("statusText");
const statusPill    = document.getElementById("statusPill");
const camOverlay    = document.getElementById("camOverlay");
const videoFeed     = document.getElementById("videoFeed");


/* ── Camera ready detection ─────────────────────────────────────────────────── */
videoFeed.addEventListener("load", () => {
  camOverlay.classList.add("hidden");
  camReady = true;
  updateStatus("Live", true);
});

videoFeed.addEventListener("error", () => {
  updateStatus("Camera Error", false);
});


/* ── Status helper ──────────────────────────────────────────────────────────── */
function updateStatus(msg, ok) {
  statusText.textContent = msg;
  statusPill.style.borderColor = ok ? "var(--green2)" : "var(--red)";
  statusPill.style.background  = ok ? "rgba(0,229,160,0.08)" : "rgba(255,68,68,0.08)";
  statusPill.style.color        = ok ? "var(--green)"         : "var(--red)";
  document.querySelector(".status-dot").style.background = ok ? "var(--green)" : "var(--red)";
}


/* ── Poll gesture status ─────────────────────────────────────────────────────── */
async function pollGestureStatus() {
  try {
    const res  = await fetch("/gesture_status");
    const data = await res.json();

    const fps       = parseFloat(data.fps || 0).toFixed(1);
    const gesture   = data.current_gesture  || "None";
    const action    = data.action_performed || "–";
    const handFound = data.hand_detected    || false;
    const conf      = parseFloat(data.confidence || 0);

    // FPS & hand
    fpsVal.textContent  = fps;
    handVal.textContent = handFound ? "✅" : "❌";
    handVal.style.color = handFound ? "var(--green)" : "var(--red)";

    // Gesture display
    const icon = GESTURE_ICONS[gesture] || "❓";
    gestureIcon.textContent   = icon;
    gestureName.textContent   = gesture;
    gestureAction.textContent = action;

    // Confidence bar
    const pct = Math.round(conf * 100);
    confFill.style.width  = pct + "%";
    confValue.textContent = pct + "%";

    // Log new gesture
    const now = Date.now();
    if (gesture !== "None" && gesture !== lastGesture && now - lastActionTime > 600) {
      addLogEntry(gesture, action);
      gestureCount++;
      totalVal.textContent = gestureCount;
      lastGesture    = gesture;
      lastActionTime = now;
    }

    // Status pill
    if (handFound) {
      updateStatus("Hand Detected", true);
    } else {
      updateStatus("No Hand", false);
    }

  } catch (err) {
    updateStatus("Connection Lost", false);
    console.error("Poll error:", err);
  }
}


/* ── Action log ──────────────────────────────────────────────────────────────── */
function addLogEntry(gesture, action) {
  // Remove empty placeholder
  const empty = actionLog.querySelector(".log-empty");
  if (empty) empty.remove();

  const li   = document.createElement("li");
  const time = new Date().toLocaleTimeString("en-GB", { hour12: false });

  li.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="log-gesture">${GESTURE_ICONS[gesture] || "❓"} ${gesture}</span>
    <span class="log-action-text">→ ${action}</span>
  `;

  actionLog.insertBefore(li, actionLog.firstChild);

  // Keep only last 20 entries
  while (actionLog.children.length > 20) {
    actionLog.removeChild(actionLog.lastChild);
  }
}

function clearLog() {
  actionLog.innerHTML = '<li class="log-empty">Waiting for gestures…</li>';
  gestureCount = 0;
  totalVal.textContent = 0;
}


/* ── Camera controls ─────────────────────────────────────────────────────────── */
async function stopCamera() {
  try {
    await fetch("/stop_camera", { method: "POST" });
    videoFeed.src = "";
    camOverlay.classList.remove("hidden");
    camOverlay.querySelector("p").textContent = "📷 Camera Stopped";
    updateStatus("Camera Stopped", false);
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  } catch (err) {
    console.error("Stop camera error:", err);
  }
}

function refreshFeed() {
  const src = videoFeed.src;
  videoFeed.src = "";
  setTimeout(() => {
    videoFeed.src = src + "?t=" + Date.now();
    camOverlay.classList.remove("hidden");
    camOverlay.querySelector("p").textContent = "📷 Reconnecting…";
    updateStatus("Reconnecting…", true);
  }, 300);

  if (!pollInterval) {
    pollInterval = setInterval(pollGestureStatus, 300);
  }
}


/* ── Init ─────────────────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  updateStatus("Initializing…", true);
  pollInterval = setInterval(pollGestureStatus, 300);

  // Fallback: hide overlay after 3 s if img hasn't fired load event
  setTimeout(() => {
    if (!camReady) {
      camOverlay.classList.add("hidden");
      camReady = true;
    }
  }, 3000);
});
