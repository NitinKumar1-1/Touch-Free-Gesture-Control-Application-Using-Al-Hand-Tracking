import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

pyautogui.FAILSAFE = False

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
smooth = 0.25

mouse_down = False

def fingers_up(lm):
    tips = [8, 12, 16, 20]
    return [lm[t].y < lm[t-2].y for t in tips]

while True:

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame,1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark

        fingers = fingers_up(lm)
        index_up, middle_up, ring_up, pinky_up = fingers

        # =========================
        # CURSOR MOVE
        # =========================
        if index_up and not middle_up and not ring_up and not pinky_up:

            ix, iy = int(lm[8].x*w), int(lm[8].y*h)

            sx = np.interp(ix,[0,w],[0,screen_w])
            sy = np.interp(iy,[0,h],[0,screen_h])

            curr_x = prev_x + (sx-prev_x)*smooth
            curr_y = prev_y + (sy-prev_y)*smooth

            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

        # =========================
        # OPEN PALM → DRAG
        # =========================
        open_palm = index_up and middle_up and ring_up and pinky_up

        if open_palm:
            if not mouse_down:
                pyautogui.mouseDown()
                mouse_down = True
        else:
            if mouse_down:
                pyautogui.mouseUp()
                mouse_down = False

    cv2.imshow("Gesture Cursor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()