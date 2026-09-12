from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import sys
import cv2
from metrics.metrics import EyeMetrics
from metrics.facial_landmarks import MediaPipeProcessor


class ObservationTab(QWidget):
    def __init__(self):
        super().__init__()

        self.landmark_processor = None
        self.cap = None
        self._camera_active = False

        # -------------------------
        # Main Layout (Vertical)
        # -------------------------
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        top_layout = QHBoxLayout()

        # -------------------------
        # Metrics Panel (Left)
        # -------------------------
        self.param_panel = QFrame()
        self.param_panel.setObjectName("infoPanel")
        self.param_panel.setFrameShape(QFrame.StyledPanel)
        self.param_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.param_panel.setMinimumWidth(420)

        self.param_layout = QVBoxLayout()
        self.param_layout.setSpacing(36)
        self.param_layout.setContentsMargins(24, 24, 24, 24)
        self.param_panel.setLayout(self.param_layout)

        title = QLabel("Eye Metrics")
        title.setObjectName("sectionTitle")
        self.param_layout.addWidget(title)

        self.ear_label = QLabel("EAR (ratio):")
        self.ear_value = QLabel("--")

        self.blink_rate_label = QLabel("Blink Rate (blinks/min):")
        self.blink_rate_value = QLabel("--")

        self.blink_duration_label = QLabel("Blink Duration (s):")
        self.blink_duration_value = QLabel("--")

        self.ibi_label = QLabel("IBI (s):")
        self.ibi_value = QLabel("--")

        self.incomplete_blink_label = QLabel("Incomplete Blink Ratio (ratio):")
        self.incomplete_blink_value = QLabel("--")

        self.perclos_label = QLabel("PERCLOS (%):")
        self.perclos_value = QLabel("--")

        metrics = [
            (self.ear_label, self.ear_value),
            (self.blink_rate_label, self.blink_rate_value),
            (self.blink_duration_label, self.blink_duration_value),
            (self.ibi_label, self.ibi_value),
            (self.incomplete_blink_label, self.incomplete_blink_value),
            (self.perclos_label, self.perclos_value),
        ]

        for name, value in metrics:
            name.setStyleSheet("font-size:36px;")
            value.setStyleSheet("font-size:36px; font-weight:bold;")
            row = QHBoxLayout()
            row.addWidget(name)
            row.addStretch()
            row.addWidget(value)
            self.param_layout.addLayout(row)

        self.param_layout.addStretch()

        # -------------------------
        # Webcam Panel
        # -------------------------
        webcam_panel = QFrame()
        webcam_panel.setObjectName("videoPanel")
        webcam_panel.setFrameShape(QFrame.StyledPanel)
        webcam_layout = QVBoxLayout()
        webcam_layout.setContentsMargins(24, 24, 24, 24)
        webcam_panel.setLayout(webcam_layout)

        self.camera_label = QLabel("Camera inactive")
        self.camera_label.setObjectName("cameraView")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("font-size:28px; color:#9aa7bf;")
        # Fixed live view size for consistent display on laptops (16:9)
        self.camera_label.setFixedSize(2320, 1380)
        self.camera_label.setMinimumSize(2320, 1080)
        self.camera_label.setMaximumSize(2320, 1080)
        webcam_layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        top_layout.addWidget(self.param_panel)
        top_layout.addWidget(webcam_panel, 1)

        main_layout.addLayout(top_layout, 3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.eye_metrics = EyeMetrics()

    def start_camera(self):
        if self._camera_active:
            return

        self.landmark_processor = MediaPipeProcessor(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        if sys.platform == "win32":
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        self.eye_metrics = EyeMetrics()
        self._camera_active = True
        self.timer.start(30)

    def stop_camera(self):
        if not self._camera_active:
            return

        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.landmark_processor is not None:
            self.landmark_processor.release()
            self.landmark_processor = None

        self._camera_active = False
        self.camera_label.clear()
        self.camera_label.setText("Camera inactive")
        self.camera_label.setStyleSheet("font-size:28px; color:#9aa7bf;")

    def update_frame(self):
        if not self._camera_active or self.cap is None or self.landmark_processor is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Process frame to extract facial landmarks
        landmarks = self.landmark_processor.process_frame(frame)

        if landmarks.face_detected:
            # Update metrics with eye landmarks
            metrics_values, _ = self.eye_metrics.update(landmarks.left_eye, landmarks.right_eye)

            # Update UI labels with metrics
            self.ear_value.setText(f"{metrics_values['EAR']:.2f}")
            self.blink_rate_value.setText(f"{metrics_values['Blink Rate']:.1f}")
            self.blink_duration_value.setText(f"{metrics_values['Blink Duration']:.2f}")
            self.ibi_value.setText(f"{metrics_values['IBI']:.2f}")
            self.incomplete_blink_value.setText(f"{metrics_values['Incomplete Blink Ratio']:.2f}")
            self.perclos_value.setText(f"{metrics_values['PERCLOS']:.1f}")

            # Draw landmarks on frame
            frame = self.landmark_processor.draw_landmarks(frame, landmarks, draw_eyes=True, draw_iris=False)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(self.camera_label.width(), self.camera_label.height(), Qt.KeepAspectRatio)
        self.camera_label.setPixmap(pixmap)

    # -------------------------
    # Close Webcam
    # -------------------------
    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)
