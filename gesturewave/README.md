# GestureWave AI – Touch-Free Gesture Control Application Using AI Hand Tracking

## Project Overview
GestureWave AI is a touch-free human-computer interaction system that uses **AI-powered hand tracking** and **real-time gesture recognition** to let users control their computer without any physical contact.

Built with **MediaPipe** (Google's hand-landmark detection framework) and **OpenCV**, the system runs entirely on a standard webcam — no specialized hardware required.

---

## Supported Gestures

| Gesture      | Fingers                   | Action          |
|--------------|---------------------------|-----------------|
| Open Palm    | All 5 fingers open        | Pause / Play    |
| Pointing     | Index finger only         | Move Cursor     |
| Pinch        | Thumb + Index close       | Mouse Click     |
| Thumbs Up    | Thumb only up             | Volume Up       |
| Peace Sign   | Index + Middle up         | Screenshot      |
| Three Fingers| Index + Middle + Ring     | Next Slide →    |
| Four Fingers | All except thumb          | Previous Slide ← |
| Rock Sign    | Index + Pinky up          | Scroll Down     |
| Call Sign    | Thumb + Pinky up          | Scroll Up       |
| Fist         | All fingers closed        | No Action       |

---

## Installation

### Prerequisites
- Python 3.10 or 3.11
- A working webcam
- Windows / Linux / macOS

### Setup
```bash
# 1. Clone or extract the project
cd gesturewave

# 2. (Recommended) Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

### Access
Open your browser and navigate to:
```
http://localhost:5000
```

---

## Project Structure
```
gesturewave/
├── app.py                  # Main Flask application + gesture engine
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/
│   ├── index.html          # Main camera feed page
│   └── gesture_map.html    # Gesture reference guide page
└── static/
    ├── css/
    │   └── style.css       # Dark-themed UI stylesheet
    └── js/
        └── app.js          # Frontend polling + UI updates
```

---

## How It Works

1. **Camera Capture** – OpenCV captures frames from the webcam at up to 30 FPS.
2. **Hand Detection** – MediaPipe's `Hands` model detects 21 hand landmarks per frame.
3. **Gesture Classification** – A rule-based classifier maps finger states to predefined gestures.
4. **Action Execution** – PyAutoGUI translates gestures into system commands (cursor movement, clicks, key presses, etc.).
5. **Live Web Dashboard** – Flask streams the annotated video feed and exposes a `/gesture_status` JSON endpoint polled by the frontend every 300 ms.

---

## Technologies Used

| Technology   | Purpose                          |
|--------------|----------------------------------|
| Python 3.10  | Core programming language        |
| Flask        | Web server & REST API            |
| MediaPipe    | AI hand landmark detection       |
| OpenCV       | Camera capture & frame rendering |
| PyAutoGUI    | System action execution          |
| NumPy        | Numerical computations           |
| HTML/CSS/JS  | Web dashboard UI                 |

---

## Hardware Requirements
- CPU: Intel Core i5 or equivalent (i7+ recommended)
- RAM: 4 GB minimum (8 GB recommended)
- Webcam: 720p or higher
- OS: Windows 10/11, Ubuntu 20.04+, macOS 12+

---

## Academic Information
- **Project Title:** Touch-Free Gesture Control Application Using AI Hand Tracking
- **System Name:** GestureWave AI
- **University:** GLA University, Mathura
- **Department:** Computer Engineering & Applications
- **Academic Year:** 2025–2026

---

## License
This project is developed for academic purposes at GLA University, Mathura.
