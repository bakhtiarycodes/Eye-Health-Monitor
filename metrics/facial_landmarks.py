import cv2
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List


@dataclass
class FacialLandmarks:
        
    # Eye landmarks (6 points each)
    left_eye: List[Tuple[int, int]]
    right_eye: List[Tuple[int, int]]
    
    # Iris landmarks (5 points each)
    left_iris: List[Tuple[int, int]]
    right_iris: List[Tuple[int, int]]
    
    # All face landmarks (468 points)
    all_landmarks: Optional[List[Tuple[float, float]]] = None
    
    # Face detected
    face_detected: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'left_eye': self.left_eye,
            'right_eye': self.right_eye,
            'left_iris': self.left_iris,
            'right_iris': self.right_iris,
            'all_landmarks': self.all_landmarks,
            'face_detected': self.face_detected
        }


class MediaPipeProcessor:
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 max_num_faces: int = 1,
                 refine_landmarks: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Eye landmark indices for 468-point model
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
        # Iris landmark indices (if refine_landmarks=True)
        self.LEFT_IRIS_INDICES = [468, 469, 470, 471, 472]
        self.RIGHT_IRIS_INDICES = [473, 474, 475, 476, 477]
        
        # Store frame dimensions for coordinate scaling
        self.frame_height = 0
        self.frame_width = 0
    
    def process_frame(self, frame: cv2.Mat) -> Optional[FacialLandmarks]:
        # Update frame dimensions
        self.frame_height, self.frame_width, _ = frame.shape
        
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_mesh.process(frame_rgb)
        
        # If no face detected, return empty landmarks
        if not results.multi_face_landmarks:
            return FacialLandmarks(
                left_eye=[],
                right_eye=[],
                left_iris=[],
                right_iris=[],
                face_detected=False
            )
        
        # Extract landmarks from first detected face
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extract eye points
        left_eye = self._extract_eye_points(face_landmarks, self.LEFT_EYE_INDICES)
        right_eye = self._extract_eye_points(face_landmarks, self.RIGHT_EYE_INDICES)
        
        # Extract iris points
        left_iris = self._extract_iris_points(face_landmarks, self.LEFT_IRIS_INDICES)
        right_iris = self._extract_iris_points(face_landmarks, self.RIGHT_IRIS_INDICES)
        
        # Extract all landmarks (optional, for advanced processing)
        all_landmarks = [
            (lm.x, lm.y) for lm in face_landmarks.landmark
        ]
        
        return FacialLandmarks(
            left_eye=left_eye,
            right_eye=right_eye,
            left_iris=left_iris,
            right_iris=right_iris,
            all_landmarks=all_landmarks,
            face_detected=True
        )
    
    def _extract_eye_points(self, face_landmarks, eye_indices: List[int]) -> List[Tuple[int, int]]:
        points = []
        for idx in eye_indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * self.frame_width)
            y = int(landmark.y * self.frame_height)
            points.append((x, y))
        return points
    
    def _extract_iris_points(self, face_landmarks, iris_indices: List[int]) -> List[Tuple[int, int]]:
        points = []
        for idx in iris_indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * self.frame_width)
            y = int(landmark.y * self.frame_height)
            points.append((x, y))
        return points
    
    def draw_landmarks(self, frame: cv2.Mat, landmarks: FacialLandmarks, 
                      draw_eyes: bool = True, draw_iris: bool = False) -> cv2.Mat:
        
        frame_copy = frame.copy()
        
        if not landmarks.face_detected:
            return frame_copy
        
        # Draw eye landmarks
        if draw_eyes:
            frame_copy = self._draw_eye_contour(frame_copy, landmarks.left_eye, color=(255, 255, 255))
            frame_copy = self._draw_eye_contour(frame_copy, landmarks.right_eye, color=(255, 255, 255))
        
        # Draw iris landmarks
        if draw_iris:
            frame_copy = self._draw_iris_contour(frame_copy, landmarks.left_iris, color=(0, 255, 0))
            frame_copy = self._draw_iris_contour(frame_copy, landmarks.right_iris, color=(0, 255, 0))
        
        return frame_copy
    
    def _draw_eye_contour(self, frame: cv2.Mat, eye_points: List[Tuple[int, int]], 
                         color: Tuple[int, int, int] = (255, 255, 255)) -> cv2.Mat:
        
        if not eye_points:
            return frame
        
        # Draw points
        for point in eye_points:
            cv2.circle(frame, point, 2, color, -1)
        
        # Draw contour lines
        for i in range(len(eye_points)):
            cv2.line(frame, eye_points[i], eye_points[(i + 1) % len(eye_points)], color, 1)
        
        return frame
    
    def _draw_iris_contour(self, frame: cv2.Mat, iris_points: List[Tuple[int, int]], 
                          color: Tuple[int, int, int] = (0, 255, 0)) -> cv2.Mat:
        
        if not iris_points:
            return frame
        
        # Draw points
        for point in iris_points:
            cv2.circle(frame, point, 1, color, -1)
        
        return frame
    
    def release(self):
       
        if self.face_mesh:
            self.face_mesh.close()
    
    def __enter__(self):
       
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
       
        self.release()
