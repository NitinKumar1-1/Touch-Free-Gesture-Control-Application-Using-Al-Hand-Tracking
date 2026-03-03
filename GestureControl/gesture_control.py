import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

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

cap = cv2.VideoCapture(0)

# Cursor smoothing
smoothening = 0.3
prev_x, prev_y = 0, 0

# Click control
pinch_state = False
last_click_time = 0
click_cooldown = 0.4

# Desktop toggle
desktop_toggled = False
last_toggle_time = 0
toggle_cooldown = 1.0


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
        index_up, middle_up, ring_up, pinky_up = fingers

        # =============================
        # CURSOR MOVEMENT (Index Only)
        # =============================
        if index_up and not middle_up and not ring_up and not pinky_up:

            ix = int(lm[8].x * w)
            iy = int(lm[8].y * h)

            sx = np.interp(ix, [0, w], [0, screen_w])
            sy = np.interp(iy, [0, h], [0, screen_h])

            curr_x = prev_x + (sx - prev_x) * smoothening
            curr_y = prev_y + (sy - prev_y) * smoothening

            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

        # =============================
        # CLICK (Stable Pinch Only)
        # =============================
        thumb_x = int(lm[4].x * w)
        thumb_y = int(lm[4].y * h)
        index_x = int(lm[8].x * w)
        index_y = int(lm[8].y * h)

        distance = math.hypot(
            thumb_x - index_x,
            thumb_y - index_y
        )

        normalized_distance = distance / w

        # Draw debug line
        cv2.line(frame, (thumb_x, thumb_y),
                 (index_x, index_y), (255, 0, 0), 2)

        cv2.putText(frame,
                    f"Pinch: {round(normalized_distance, 3)}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2)

        # Bigger threshold = easier click
        PINCH_THRESHOLD = 0.08

        if normalized_distance < PINCH_THRESHOLD:

            if not pinch_state and time.time() - last_click_time > click_cooldown:
                pyautogui.click()
                last_click_time = time.time()
                pinch_state = True

                cv2.putText(frame, "CLICK",
                            (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0), 2)
        else:
            pinch_state = False

        # =============================
        # STRICT FIST → MINIMIZE
        # =============================
        is_fist = (
            not index_up and
            not middle_up and
            not ring_up and
            not pinky_up
        )

        if (is_fist and
                not desktop_toggled and
                time.time() - last_toggle_time > toggle_cooldown):

            pyautogui.hotkey('win', 'd')
            desktop_toggled = True
            last_toggle_time = time.time()

        # =============================
        # OPEN PALM → RESTORE
        # =============================
        is_open = index_up and middle_up and ring_up and pinky_up

        if (is_open and
                desktop_toggled and
                time.time() - last_toggle_time > toggle_cooldown):

            pyautogui.hotkey('win', 'd')
            desktop_toggled = False
            last_toggle_time = time.time()

    cv2.imshow("AI Virtual Mouse - Stable Click", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()