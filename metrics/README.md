# Eye Health Monitor - Metrics & Landmarks Module

## Module Structure

```
metrics/
├── __init__.py
├── metrics.py                 # Eye metrics calculations (EyeMetrics class)
├── facial_landmarks.py        # MediaPipe facial landmark detection (NEW)
└── ML_Model/
    ├── model_train.ipynb
    ├── testing.py
    └── Dataset/
        └── dataset-eye_blink_data.csv
```

## Architecture Overview

The metrics module is divided into two complementary components:

### 1. **facial_landmarks.py** - Frontend Processor
Handles MediaPipe processing and facial landmark extraction.

**Responsibilities:**
- Initialize and manage MediaPipe FaceMesh model
- Process video frames to extract facial landmarks
- Extract eye and iris coordinates from 468-point face mesh
- Provide visualization/drawing capabilities
- Return structured landmark data

**Key Classes:**
- `MediaPipeProcessor`: Main processor for facial landmark detection
- `FacialLandmarks`: Data container for landmark coordinates

**When to Use:**
- Need to extract eye landmarks from video frames
- Building new features that require facial landmark data
- Any module that processes video for facial analysis

### 2. **metrics.py** - Backend Calculator
Performs calculations and metrics computation based on landmark data.

**Responsibilities:**
- Calculate Eye Aspect Ratio (EAR)
- Detect and count blinks
- Calculate blink rate, duration, and inter-blink interval (IBI)
- Track incomplete blinks
- Calculate PERCLOS (Percentage of eyelid closure)
- Maintain statistics across frames

**Key Classes:**
- `EyeMetrics`: Core metrics engine

**When to Use:**
- Calculate eye metrics from landmark coordinates
- Track blink events over time
- Generate metrics data for analysis

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Video Frame (OpenCV)                        │
│                    (BGR format from camera)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │     MediaPipeProcessor                  │
        │   (facial_landmarks.py)                 │
        │                                         │
        │  • Convert BGR → RGB                   │
        │  • Run FaceMesh detection              │
        │  • Extract landmarks                  │
        │  • Return FacialLandmarks object       │
        └─────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │      FacialLandmarks                    │
        │   (Structured Data Container)           │
        │                                         │
        │  • left_eye: [(x,y), ...]             │
        │  • right_eye: [(x,y), ...]            │
        │  • left_iris: [(x,y), ...]            │
        │  • right_iris: [(x,y), ...]           │
        │  • all_landmarks: [(x,y), ...]        │
        │  • face_detected: bool                │
        └─────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │        EyeMetrics                       │
        │      (metrics.py)                       │
        │                                         │
        │  • compute_ear(eye_points) → float    │
        │  • update(left_eye, right_eye)        │
        │    → metrics_dict, blinked_bool       │
        └─────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │         Metrics Dictionary              │
        │                                         │
        │  {                                      │
        │    'EAR': 0.45,                        │
        │    'Blink Rate': 12.5,                 │
        │    'Blink Duration': 0.15,             │
        │    'IBI': 4.2,                         │
        │    'Incomplete Blink Ratio': 0.1,     │
        │    'PERCLOS': 5.2                      │
        │  }                                      │
        └─────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │   Display / Store / Analyze             │
        │                                         │
        │  • GUI Display (ObservationTab)        │
        │  • CSV Recording (ExaminationTab)      │
        │  • ML Analysis                         │
        │  • Real-time Dashboard                 │
        └─────────────────────────────────────────┘
```

## Integration Pattern

### For GUI Components (ObservationTab, ExaminationTab)

```python
# Step 1: Import the processor
from metrics.facial_landmarks import MediaPipeProcessor
from metrics.metrics import EyeMetrics

# Step 2: Initialize in __init__()
self.landmark_processor = MediaPipeProcessor()
self.metrics_engine = EyeMetrics()

# Step 3: Process frames in update method
landmarks = self.landmark_processor.process_frame(frame)

if landmarks.face_detected:
    # Step 4: Calculate metrics
    metrics_values, blinked = self.metrics_engine.update(
        landmarks.left_eye, 
        landmarks.right_eye
    )
    
    # Step 5: Use metrics (display, store, analyze)
    print(f"EAR: {metrics_values['EAR']:.2f}")
    
    # Step 6 (Optional): Visualize landmarks
    frame = self.landmark_processor.draw_landmarks(frame, landmarks)

# Step 7: Clean up when done
self.landmark_processor.release()
```

## File Responsibilities

### facial_landmarks.py
- **Single Responsibility**: Face and eye landmark detection
- **Dependencies**: MediaPipe, OpenCV (cv2)
- **Does NOT**: Calculate metrics, make decisions, store data
- **Can be used by**: Any module that needs facial landmarks
- **Size**: ~350 lines (well-documented)

### metrics.py
- **Single Responsibility**: Eye metrics calculation
- **Dependencies**: Python standard library (time, collections, math)
- **Does NOT**: Process video frames, initialize ML models, handle GUI
- **Can be used by**: Metrics engines, analysis modules, ML pipelines
- **Size**: ~150 lines

### observation.py (GUI)
- **Uses**: MediaPipeProcessor, EyeMetrics
- **Responsibility**: Display real-time eye metrics
- **Imports**: `from metrics.facial_landmarks import MediaPipeProcessor`

### examination.py (GUI)
- **Uses**: MediaPipeProcessor, EyeMetrics
- **Responsibility**: Record eye metrics during examination
- **Imports**: `from metrics.facial_landmarks import MediaPipeProcessor`

## Key Design Principles

### 1. **Separation of Concerns**
- Detection (facial_landmarks.py) ≠ Calculation (metrics.py)
- Backend processing ≠ Frontend UI (GUI modules)

### 2. **Single Responsibility**
- Each class has one reason to change
- MediaPipeProcessor: Only changes if MediaPipe API changes
- EyeMetrics: Only changes if metric formulas change

### 3. **Reusability**
- No duplicate MediaPipe initialization code
- Landmark extraction can be used by any feature
- Metrics calculation decoupled from detection

### 4. **Extensibility**
- Easy to add new landmarks (face contours, hand poses)
- Easy to add new metrics (blink quality, gaze direction)
- Easy to add new drawing methods

### 5. **Testability**
- Each module can be tested independently
- No complex dependencies
- Clear input/output contracts

## Configuration Parameters

### MediaPipeProcessor Settings

For **real-time tracking** (Observation Tab):
```python
MediaPipeProcessor(
    static_image_mode=False,      # Continuous tracking
    max_num_faces=1,
    refine_landmarks=True,        # Better iris detection
    min_detection_confidence=0.5,  # Balanced accuracy/speed
    min_tracking_confidence=0.5
)
```

For **still images** or **high accuracy**:
```python
MediaPipeProcessor(
    static_image_mode=True,       # Detect every frame
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7, # High confidence
    min_tracking_confidence=0.7
)
```

### EyeMetrics Settings (in metrics.py)

```python
self.ear_threshold = 0.20        # Threshold for detecting eye closure
self.fps = 30                    # Expected frames per second
```

## Performance Characteristics

| Component | Time per Frame | Memory | GPU |
|-----------|-----------------|--------|-----|
| MediaPipeProcessor | 30-50ms | ~150MB | Not required |
| EyeMetrics | <1ms | Minimal | No |
| Total | 30-50ms | ~150MB | Optional |

## Future Extensibility

The module structure allows for easy addition of:

1. **New Landmarks**
   - Add to `MediaPipeProcessor._extract_*_points()` methods
   - Return in `FacialLandmarks` dataclass

2. **New Metrics**
   - Add calculation methods to `EyeMetrics` class
   - Return in metrics dictionary

3. **New Visualizations**
   - Add drawing methods to `MediaPipeProcessor`
   - Use `draw_landmarks()` as template

4. **Multi-face Support**
   - Extend `MediaPipeProcessor` to handle `max_num_faces > 1`
   - Return list of `FacialLandmarks` objects

## Troubleshooting

### Import Errors
```python
# ❌ Wrong (MediaPipe not properly installed)
from metrics.facial_landmarks import MediaPipeProcessor

# ✅ Fix: Ensure MediaPipe is installed
pip install mediapipe
```

### No Face Detected
- Improve lighting conditions
- Ensure face is clearly visible
- Lower `min_detection_confidence` parameter
- Check camera resolution and angle

### Slow Performance
- Reduce frame resolution
- Increase `min_detection_confidence` threshold
- Set `static_image_mode=False` (allows tracking optimization)
- Disable iris refinement if not needed: `refine_landmarks=False`

### Inaccurate Landmarks
- Use `static_image_mode=True` for still images
- Use `static_image_mode=False` for video (default, enables tracking)
- Ensure consistent lighting
- Check face size (not too small, not too large)

## Related Files

- `GUI/observation.py` - Uses both modules for real-time display
- `GUI/examination.py` - Uses both modules for data recording
- `MEDIAPIPE_MODULE_GUIDE.md` - Detailed usage documentation
- `metrics/ML_Model/` - Model training and testing

## Summary

The refactored metrics module provides a **clean, reusable architecture** for eye detection and metrics calculation:

- ✅ **No code duplication** - Single source of truth for MediaPipe
- ✅ **Clean separation** - Detection vs. calculation vs. UI
- ✅ **Easy to extend** - Add new features without touching core logic
- ✅ **Well documented** - Both code and usage guides
- ✅ **Maintainable** - Clear responsibilities and interfaces
