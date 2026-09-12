# Eye Health Monitor

## Table of Contents

- [Introduction]
- [Purpose]
- [Features]
- [System Architecture] 
- [Technologies Used]
- [Project Structure]
- [Usage]
- [Performance and Testing]
- [Requirements]
- [Troubleshooting]
- [Limitations]
- [Credits & License]

## Introduction

Eye Health Monitor is a Python application that analyzes eye blink behavior in real time to detect potential eye fatigue and dryness. The application combines MediaPipe face and eye landmark detection, OpenCV video processing, a PyQt5 graphical user interface, and a Random Forest machine learning model to classify eye condition into `Normal` or `Fatigue_Dryness` classes.

## Purpose

The primary goals of Eye Health Monitor are:

- Monitoring eye health using a webcam or external camera.
- Detecting signs of fatigue and eye dryness through blink behavior analysis.
- Performing real-time blink detection and feature extraction.
- Classifying eye condition using a trained Random Forest model.
- Visualizing results and metrics through an intuitive GUI for research and demonstration.

## Features

- Real-time face and eye landmark detection using MediaPipe Face Mesh.
- Blink detection and tracking (blink rate, blink duration, incomplete blink ratio).
- Feature extraction pipeline for ML inference.
- Random Forest classifier to detect `Normal` vs `Fatigue_Dryness`.
- Live visualization of current predictions and historical metrics in the PyQt5 GUI.
- Save and export session metrics (CSV) for offline analysis.

## System Architecture

The application implements a modular pipeline:

```mermaid
flowchart LR
  Camera[Camera Input] -->|Frames| Preprocess
  Preprocess --> FaceDetect[Face Detection (MediaPipe)]
  FaceDetect --> EyeLandmarks[Eye Landmark Extraction]
  EyeLandmarks --> BlinkDetect[Blink Detection]
  BlinkDetect --> FeatureExtract[Feature Extraction]
  FeatureExtract --> Model[Random Forest Classifier]
  Model --> Visualization[Result Visualization (PyQt5)]
```

Components explained:

- Camera input: Captures frames from a webcam or external camera using OpenCV.
- Face detection: Uses MediaPipe Face Mesh to find facial landmarks robustly and efficiently.
- Eye landmark extraction: Localizes eye landmarks to compute eye aspect ratio and other blink-related metrics.
- Blink detection: Detects blinks, timestamps, and duration; distinguishes complete vs incomplete blinks.
- Feature extraction: Calculates blink rate, blink duration, and incomplete blink ratio in time windows.
- Random Forest classification: Uses the trained model to classify the extracted feature vector.
- Result visualization: Displays current predictions, confidence, and historical metrics in the GUI.

## Technologies Used

| Area | Library / Framework |
|---|---|
| GUI | PyQt5 |
| Computer Vision | OpenCV |
| Face Mesh & Landmarks | MediaPipe |
| Machine Learning | scikit-learn (RandomForestClassifier) |
| Serialization | joblib |
| Numerics / Data | NumPy, pandas |

## Project Structure (example)

```
eye-health-monitor/
├─ ML_Model/
│  ├─ blink_random_forest_model.pkl        # Trained Random Forest model
│  ├─ testing.py
│  └─ model_train.ipynb
├─ GUI/
│  ├─ analysis.py
│  ├─ examination.py
│  ├─ observation.py
│  ├─ overview.py
│  └─ validation.py
├─ metrics/
│  ├─ facial_landmarks.py
│  ├─ metrics.py
│  └─ README.md
├─ DataBase/
│  └─ database.py
├─ main_app.py
├─ eye_metrics.csv
└─ style/
   └─ style.py
```

> Note: The file `[ML_Model/blink_random_forest_model.pkl](ML_Model/blink_random_forest_model.pkl)` is included in the repository and used by the inference scripts.

## Usage

1. Create and activate a Python virtual environment (recommended):

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate
```

2. Install dependencies (example):

```bash
pip install opencv-python mediapipe pyqt5 numpy pandas scikit-learn joblib
```

3. Launch the application:

```bash
# From project root
python main_app.py
```

4. Positioning and camera guidance:

- Position your face centered in the camera frame with eyes clearly visible.
- Keep a neutral forward-facing orientation (avoid large head rotations).
- Maintain approximately 40–70 cm distance from the camera for typical webcams.
- Use a stable camera (tripod or laptop stand) to reduce motion artifacts.

Lighting recommendations:

- Prefer soft, diffused lighting from the front; avoid strong backlight.
- Avoid extreme shadows across the face; ensure eyes are well illuminated.

Camera recommendations:

- Use a 720p or 1080p webcam for reliable landmark detection; 4K is supported but not required.
- External USB webcams typically give more stable exposure than built-in laptop cameras.

## Performance and Testing

- The GUI was tested on a 4K laptop display; UI scaling and layout were optimized for high-resolution screens.
- Appearance and layout on lower-resolution displays may vary depending on operating system scaling settings.
- The system was tested under different lighting conditions to validate landmark stability and blink detection robustness.

> Warning: Performance depends on CPU/GPU availability. MediaPipe can leverage GPU on supported platforms for better throughput.

## Requirements

Minimum recommended environment:

| Item | Version / Note |
|---|---|
| Python | 3.8+ |
| OpenCV | >= 4.5 |
| MediaPipe | >= 0.8 |
| PyQt5 | >= 5.12 |
| NumPy | latest stable |
| pandas | latest stable (optional for CSV exports) |
| scikit-learn | >= 0.24 |
| joblib | latest stable |

Example `pip` install:

```bash
pip install opencv-python mediapipe pyqt5 numpy pandas scikit-learn joblib
```

## Troubleshooting

- Camera not detected
  - Ensure the camera is not in use by another application.
  - Verify correct camera index in `main_app.py` or GUI settings.
  - On Windows, ensure privacy permissions allow camera access.

- Model file not found
  - Confirm `[ML_Model/blink_random_forest_model.pkl](ML_Model/blink_random_forest_model.pkl)` exists in the `ML_Model` folder.
  - If relocated, update the inference script to reference the correct path.

- Missing dependencies
  - Reinstall using `pip install -r requirements.txt` (if provided) or the `pip install` command above.

- Poor or inconsistent detections
  - Improve lighting and stabilize the camera.
  - Increase resolution or reduce camera-to-subject distance.

- Face not detected
  - Move closer to the camera and ensure face is fully within the frame.
  - Avoid obstructions (hair, glasses glare) that may occlude landmarks.

- Incorrect prediction or unexpected outputs
  - Verify input feature ranges (blink rate, duration, incomplete blink ratio) with logs.
  - Confirm the model file matches the feature order used during training.
  - Retrain the model with representative data if distribution drift is suspected.

## Limitations

- This software is NOT a medical diagnostic device.
- It is intended for educational, research, and demonstration purposes only.
- Predictions should NOT replace professional medical advice; consult a clinician for diagnosis.
- Model performance depends on training data and may not generalize to all populations or environments.

## Notes & Recommendations

- For reproducible results, keep camera settings (exposure, resolution) consistent across sessions.
- Consider recording sample sessions (with consent) to expand the dataset and improve model robustness.

## Credits & License

- Developed with OpenCV, MediaPipe, PyQt5, and scikit-learn.
---
