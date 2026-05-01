"""
GestureWave AI - Touch-Free Gesture Control Application Using AI Hand Tracking
Main Flask Application
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import json
import time
import pyautogui
import math
import threading

app = Flask(__name__)

# ─── MediaPipe Setup ──────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# ─── Global State ─────────────────────────────────────────────────────────────
camera = None
camera_lock = threading.Lock()
gesture_state = {
    "current_gesture": "None",
    "action_performed": "",
    "confidence": 0.0,
    "hand_detected": False,
    "fps": 0,
    "landmarks": []
}

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01

# ─── Pinch Hold State ─────────────────────────────────────────────────────────
_pinch_held = False          # True while mouse button is being held down
_pinch_start_time = None     # When pinch gesture first started

# ─── Gesture Recognition Logic ────────────────────────────────────────────────

def get_finger_states(landmarks):
    """Return which fingers are extended (True/False) for [thumb, index, middle, ring, pinky]."""
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]

    fingers = []
    # Thumb: compare x axis
    if landmarks[tips[0]].x < landmarks[pips[0]].x:
        fingers.append(True)
    else:
        fingers.append(False)

    # Other fingers: compare y axis (lower y = higher on screen)
    for i in range(1, 5):
        fingers.append(landmarks[tips[i]].y < landmarks[pips[i]].y)

    return fingers


def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def recognize_gesture(landmarks, frame_shape):
    """Classify hand gesture from landmarks."""
    fingers = get_finger_states(landmarks)
    thumb, index, middle, ring, pinky = fingers

    # Pinch gesture: thumb tip close to index tip
    pinch_dist = distance(landmarks[4], landmarks[8])

    # Fist: all fingers closed
    if not any(fingers):
        return "Fist", "No Action"

    # Open Palm: all fingers open
    if all(fingers):
        return "Open Palm", "Pause / Play"

    # Thumbs Up
    if thumb and not index and not middle and not ring and not pinky:
        return "Thumbs Up", "Volume Up"

    # Thumbs Down
    if not thumb and not index and not middle and not ring and not pinky:
        return "Fist", "No Action"

    # Peace / Victory Sign: index + middle up → Scroll Up
    if not thumb and index and middle and not ring and not pinky:
        return "Peace Sign", "Scroll Up"

    # Pointing: only index up
    if not thumb and index and not middle and not ring and not pinky:
        return "Pointing", "Move Cursor"

    # Pinch: index + thumb close → Click / Click & Hold
    if pinch_dist < 0.05:
        return "Pinch", "Pinch Action"

    # Three fingers: index + middle + ring up → Scroll Down
    if not thumb and index and middle and ring and not pinky:
        return "Three Fingers", "Scroll Down"

    # All four fingers (no thumb)
    if not thumb and index and middle and ring and pinky:
        return "Four Fingers", "Previous Slide"

    # Rock sign: index + pinky up
    if not thumb and index and not middle and not ring and pinky:
        return "Rock Sign", "Scroll Down"

    # Call sign: thumb + pinky up
    if thumb and not index and not middle and not ring and pinky:
        return "Call Sign", "Scroll Up"

    return "Unknown", "No Action"


def process_frame(frame):
    """Run hand detection and gesture recognition on a single frame."""
    global gesture_state

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    h, w = frame.shape[:2]
    overlay = frame.copy()

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            gesture, action = recognize_gesture(hand_landmarks.landmark, frame.shape)

            # Perform system action
            perform_action(action, hand_landmarks.landmark, w, h)

            # Update state — show friendly label for pinch hold state
            display_action = action
            if action == "Pinch Action":
                display_action = "Click & Hold" if _pinch_held else "Click"
            gesture_state["current_gesture"] = gesture
            gesture_state["action_performed"] = display_action
            gesture_state["hand_detected"] = True
            gesture_state["confidence"] = 0.95

            # Draw gesture label box
            cv2.rectangle(frame, (10, 10), (400, 80), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 10), (400, 80), (0, 200, 100), 2)
            cv2.putText(frame, f"Gesture: {gesture}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 150), 2)
            cv2.putText(frame, f"Action : {display_action}", (20, 68),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 220, 0), 2)

    else:
        release_pinch_if_held()  # Safety: release mouse if hand disappears mid-hold
        gesture_state["current_gesture"] = "None"
        gesture_state["action_performed"] = "No hand detected"
        gesture_state["hand_detected"] = False
        gesture_state["confidence"] = 0.0

        cv2.rectangle(frame, (10, 10), (380, 50), (0, 0, 0), -1)
        cv2.putText(frame, "No Hand Detected", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 255), 2)

    # FPS counter
    cv2.putText(frame, f"FPS: {gesture_state['fps']:.1f}", (w - 130, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame


_last_action_time = {}
_cursor_smooth = [960, 540]

def release_pinch_if_held():
    """Safely release mouse button if a pinch-hold is active."""
    global _pinch_held, _pinch_start_time
    if _pinch_held:
        pyautogui.mouseUp()
        _pinch_held = False
        _pinch_start_time = None

def perform_action(action, landmarks, w, h):
    """Map recognized gesture to system action."""
    global _cursor_smooth, _pinch_held, _pinch_start_time

    now = time.time()
    cooldown = _last_action_time.get(action, 0)

    # Pinch: press-and-hold mouse on first frame; release happens when gesture ends
    if action == "Pinch Action":
        if not _pinch_held:
            _pinch_start_time = now
            pyautogui.mouseDown()
            _pinch_held = True
        return  # keep holding while pinch continues

    # Any non-pinch gesture: release the held mouse button
    if _pinch_held:
        pyautogui.mouseUp()
        _pinch_held = False
        _pinch_start_time = None
        # mouseDown+mouseUp from a quick pinch already behaves as a click

    if action == "Move Cursor":
        ix = int(landmarks[8].x * w)
        iy = int(landmarks[8].y * h)
        screen_w, screen_h = pyautogui.size()
        sx = int(np.interp(ix, [0, w], [0, screen_w]))
        sy = int(np.interp(iy, [0, h], [0, screen_h]))
        _cursor_smooth[0] += (sx - _cursor_smooth[0]) * 0.2
        _cursor_smooth[1] += (sy - _cursor_smooth[1]) * 0.2
        pyautogui.moveTo(int(_cursor_smooth[0]), int(_cursor_smooth[1]))

    elif action == "Scroll Up" and now - cooldown > 0.3:
        pyautogui.scroll(3)
        _last_action_time[action] = now

    elif action == "Scroll Down" and now - cooldown > 0.3:
        pyautogui.scroll(-3)
        _last_action_time[action] = now

    elif action == "Volume Up" and now - cooldown > 1.5:
        pyautogui.press('volumeup')
        _last_action_time[action] = now

    elif action == "Next Slide" and now - cooldown > 1.5:
        pyautogui.press('right')
        _last_action_time[action] = now

    elif action == "Previous Slide" and now - cooldown > 1.5:
        pyautogui.press('left')
        _last_action_time[action] = now

    elif action == "Pause / Play" and now - cooldown > 1.5:
        pyautogui.press('space')
        _last_action_time[action] = now


# ─── Camera Generator ─────────────────────────────────────────────────────────

def generate_frames():
    global camera
    prev_time = time.time()

    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        with camera_lock:
            if camera is None:
                break
            success, frame = camera.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        curr_time = time.time()
        gesture_state["fps"] = 1.0 / (curr_time - prev_time + 1e-9)
        prev_time = curr_time

        frame = process_frame(frame)

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/gesture_status')
def gesture_status():
    return jsonify(gesture_state)


@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
    return jsonify({"status": "Camera stopped"})


@app.route('/gesture_map')
def gesture_map():
    gesture_map_data = [
        {"gesture": "Open Palm", "fingers": "All 5 fingers open", "action": "Pause / Play Media", "icon": "✋"},
        {"gesture": "Pointing", "fingers": "Index finger only", "action": "Move Cursor", "icon": "☝️"},
        {"gesture": "Pinch", "fingers": "Thumb + Index close (quick)", "action": "Mouse Click", "icon": "🤏"},
        {"gesture": "Pinch & Hold", "fingers": "Thumb + Index close (hold)", "action": "Click & Hold (Drag)", "icon": "🤏"},
        {"gesture": "Thumbs Up", "fingers": "Thumb only up", "action": "Volume Up", "icon": "👍"},
        {"gesture": "Peace Sign", "fingers": "Index + Middle up", "action": "Scroll Up", "icon": "✌️"},
        {"gesture": "Three Fingers", "fingers": "Index + Middle + Ring", "action": "Scroll Down", "icon": "🖖"},
        {"gesture": "Four Fingers", "fingers": "All except thumb", "action": "Previous Slide ←", "icon": "🖐"},
        {"gesture": "Rock Sign", "fingers": "Index + Pinky up", "action": "Scroll Down", "icon": "🤘"},
        {"gesture": "Call Sign", "fingers": "Thumb + Pinky up", "action": "Scroll Up", "icon": "🤙"},
        {"gesture": "Fist", "fingers": "All fingers closed", "action": "No Action", "icon": "✊"},
    ]
    return render_template('gesture_map.html', gestures=gesture_map_data)


if __name__ == '__main__':
    print("=" * 60)
    print("  GestureWave AI - Touch-Free Gesture Control System")
    print("  Running at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
