import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
from collections import deque

pyautogui.FAILSAFE = False

# Screen size
screen_w, screen_h = pyautogui.size()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Smoothing buffers
x_buf = deque(maxlen=7)
y_buf = deque(maxlen=7)

last_click = 0
desktop_toggled = False

def fingers_up(lm):
    tips = [8, 12, 16, 20]
    return [lm[t].y < lm[t - 2].y for t in tips]

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        fingers = fingers_up(lm)

        # ☝ MOVE CURSOR (index only)
        if fingers == [True, False, False, False]:
            ix = int(lm[8].x * w)
            iy = int(lm[8].y * h)

            sx = np.interp(ix, [0, w], [0, screen_w])
            sy = np.interp(iy, [0, h], [0, screen_h])

            x_buf.append(sx)
            y_buf.append(sy)

            pyautogui.moveTo(
                sum(x_buf) / len(x_buf),
                sum(y_buf) / len(y_buf)
            )

        # 🤏 CLICK (thumb + index)
        thumb_x = int(lm[4].x * w)
        thumb_y = int(lm[4].y * h)

        index_x = int(lm[8].x * w)
        index_y = int(lm[8].y * h)

        pinch_distance = math.hypot(
            thumb_x - index_x,
            thumb_y - index_y
        )

        # Debug visuals (can remove later)
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 2)
        cv2.putText(frame, f"Pinch: {int(pinch_distance)}",
                    (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 0), 2)

        if pinch_distance < 35 and time.time() - last_click > 0.7:
            pyautogui.click()
            last_click = time.time()
            cv2.putText(frame, "CLICK", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # ✊ FIST CLOSED → MINIMIZE ALL
        if fingers.count(True) == 0 and not desktop_toggled:
            pyautogui.hotkey('win', 'd')
            desktop_toggled = True
            time.sleep(0.6)

        # 🖐 OPEN PALM → RESTORE ALL
        if fingers.count(True) == 4 and desktop_toggled:
            pyautogui.hotkey('win', 'd')
            desktop_toggled = False
            time.sleep(0.6)

    cv2.imshow("Gesture Control (Stable)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
