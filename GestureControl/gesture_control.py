import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# Screen size
screen_w, screen_h = pyautogui.size()

# Webcam
cap = cv2.VideoCapture(0)

# Mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# smoothing variables
prev_x, prev_y = 0, 0
smoothening = 7

click_cooldown = 0

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

while True:

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    h, w, c = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []

            for id, lm in enumerate(hand_landmarks.landmark):

                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))

            if len(landmarks) != 0:

                index_tip = landmarks[8]
                thumb_tip = landmarks[4]
                middle_tip = landmarks[12]
                ring_tip = landmarks[16]

                # Convert to screen coordinates
                screen_x = np.interp(index_tip[0], (0, w), (0, screen_w))
                screen_y = np.interp(index_tip[1], (0, h), (0, screen_h))

                # Smooth movement
                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening

                pyautogui.moveTo(curr_x, curr_y)

                prev_x, prev_y = curr_x, curr_y

                # PINCH distance
                pinch_dist = distance(index_tip, thumb_tip)

                # LEFT CLICK (pinch)
                if pinch_dist < 35 and time.time() - click_cooldown > 0.7:
                    pyautogui.click()
                    click_cooldown = time.time()

                # RIGHT CLICK (index + middle close)
                mid_dist = distance(index_tip, middle_tip)

                if mid_dist < 30 and time.time() - click_cooldown > 0.7:
                    pyautogui.rightClick()
                    click_cooldown = time.time()

                # SCROLL (middle finger move)
                if middle_tip[1] < index_tip[1] - 40:
                    pyautogui.scroll(40)

                if middle_tip[1] > index_tip[1] + 40:
                    pyautogui.scroll(-40)

                # DRAW VISUAL CIRCLES
                cv2.circle(frame, index_tip, 10, (0,255,0), cv2.FILLED)
                cv2.circle(frame, thumb_tip, 10, (255,0,0), cv2.FILLED)

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# Screen size
screen_w, screen_h = pyautogui.size()

# Webcam
cap = cv2.VideoCapture(0)

# Mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# smoothing variables
prev_x, prev_y = 0, 0
smoothening = 7

click_cooldown = 0

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

while True:

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    h, w, c = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []

            for id, lm in enumerate(hand_landmarks.landmark):

                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))

            if len(landmarks) != 0:

                index_tip = landmarks[8]
                thumb_tip = landmarks[4]
                middle_tip = landmarks[12]
                ring_tip = landmarks[16]

                # Convert to screen coordinates
                screen_x = np.interp(index_tip[0], (0, w), (0, screen_w))
                screen_y = np.interp(index_tip[1], (0, h), (0, screen_h))

                # Smooth movement
                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening

                pyautogui.moveTo(curr_x, curr_y)

                prev_x, prev_y = curr_x, curr_y

                # PINCH distance
                pinch_dist = distance(index_tip, thumb_tip)

                # LEFT CLICK (pinch)
                if pinch_dist < 35 and time.time() - click_cooldown > 0.7:
                    pyautogui.click()
                    click_cooldown = time.time()

                # RIGHT CLICK (index + middle close)
                mid_dist = distance(index_tip, middle_tip)

                if mid_dist < 30 and time.time() - click_cooldown > 0.7:
                    pyautogui.rightClick()
                    click_cooldown = time.time()

                # SCROLL (middle finger move)
                if middle_tip[1] < index_tip[1] - 40:
                    pyautogui.scroll(40)

                if middle_tip[1] > index_tip[1] + 40:
                    pyautogui.scroll(-40)

                # DRAW VISUAL CIRCLES
                cv2.circle(frame, index_tip, 10, (0,255,0), cv2.FILLED)
                cv2.circle(frame, thumb_tip, 10, (255,0,0), cv2.FILLED)

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()