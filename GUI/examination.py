from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import cv2
import time
import csv
import os
from metrics.metrics import EyeMetrics
from metrics.facial_landmarks import MediaPipeProcessor
from GUI.validation import show_alert, validate_examination_language

class ExaminationTab(QWidget):
    request_analysis = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.metrics_engine = EyeMetrics()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        self.csv_file = None
        self.csv_writer = None

        # -------------------------
        # MediaPipe Processor Setup
        # -------------------------
        self.landmark_processor = MediaPipeProcessor(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.recording_started = False
        self.stabilization_time = 20
        self.recording_start_time = None

        self.text_en = (
            "The human eye is a delicate organ that allows us to see the world clearly. " "Proper eye care is essential to avoid dryness, strain, and fatigue when using laptops, smartphones, or desktop monitors. " "Maintain a comfortable distance from screens, adjust brightness and contrast, take regular breaks, and avoid staring for long periods. " "Simple exercises like blinking often, rolling your eyes, and focusing on distant objects help reduce fatigue. " "Hydration and a balanced diet with vitamins A, C, E, omega-3, and zinc support eye health. " "Proper workspace ergonomics, including chair height, monitor angle, and lighting, also prevent strain. " "Following these routines helps reduce discomfort and maintain long-term visual clarity."
        )
        self.text_cn = (
            "人眼是一个精密的器官，它让我们能够清晰、生动地感知世界。" "保持眼睛健康对于避免干涩、疲劳和视觉不适非常重要，尤其是在长时间使用笔记本电脑、智能手机和桌面显示器时。" "为保持舒适，应养成一些良好习惯：保持与屏幕的安全距离，调节亮度和对比度以减少眩光，" "定期短暂休息，避免长时间盯屏。" "进行简单眼部运动，如经常眨眼、眼球旋转及注视远处物体，可显著减轻疲劳。" "此外，保持水分摄入和均衡饮食，摄取富含维生素A、C、E、欧米伽-3脂肪酸及锌的食物，有助于眼睛健康。" "优化工作空间的人体工学，包括椅子高度、显示器角度和光线，也能防止眼睛疲劳。" "儿童、学生及长时间使用电子设备的人应特别注意这些习惯，以避免早期疲劳、干涩或不适。"
        )

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Instruction + Language Selection
        self.instruction_label = QLabel("Please select your language\n请选择您的语言")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("font-size:32px; font-weight:bold; padding:20px;")

        language_layout = QHBoxLayout()
        self.btn_en = QPushButton("English")
        self.btn_cn = QPushButton("中文")
        for btn in (self.btn_en, self.btn_cn):
            btn.setFixedWidth(180)
            btn.setStyleSheet("font-size:24px; padding:10px;")
            language_layout.addWidget(btn)

        self.start_btn = QPushButton("Start Examination")
        self.start_btn.setFixedWidth(250)
        self.start_btn.setStyleSheet("font-size:24px; padding:10px")

        self.ready_label = QLabel("If you are ready for this examination, press Start Examination.")
        self.ready_label.setAlignment(Qt.AlignCenter)
        self.ready_label.setStyleSheet("font-size:24px; padding:20px")

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setText("")
        self.text_display.setStyleSheet("font-size:128px; padding:30px; line-height:1.4;")
        self.text_display.setMinimumHeight(840)

        self.end_btn = QPushButton("End of Examination")
        self.end_btn.setFixedWidth(250)
        self.end_btn.setStyleSheet("font-size:24px; padding:10px")

        self.review_analysis_btn = QPushButton("Review Analysis")
        self.review_analysis_btn.setObjectName("primaryButton")
        self.review_analysis_btn.setFixedWidth(240)

        main_layout.addWidget(self.instruction_label)
        main_layout.addLayout(language_layout)
        main_layout.addWidget(self.start_btn, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.ready_label)
        main_layout.addWidget(self.text_display)
        main_layout.addWidget(self.end_btn, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.review_analysis_btn, alignment=Qt.AlignHCenter)

        self.setLayout(main_layout)

        # Connect buttons
        self.btn_en.clicked.connect(lambda: self.text_display.setText(self.text_en))
        self.btn_cn.clicked.connect(lambda: self.text_display.setText(self.text_cn))
        self.start_btn.clicked.connect(self.start_examination)
        self.end_btn.clicked.connect(self.end_examination)
        self.review_analysis_btn.clicked.connect(self.goto_analysis)

    def start_examination(self):
        if not validate_examination_language(self.text_display):
            show_alert(self, "Please select at least one language.")
            return

        self.ready_label.setText("Please wait 5 seconds...")
        QTimer.singleShot(5000, self.start_recording)

    def start_recording(self):
        self.ready_label.setText("Recording...")
        self.cap = cv2.VideoCapture(0)

        filename = "eye_metrics.csv"
        filepath = os.path.join(os.getcwd(), filename)
        self.csv_file = open(filepath, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            "timestamp","EAR","Blink Rate","Blink Duration","IBI",
            "Incomplete Blink Ratio","PERCLOS"
        ])

        self.recording_start_time = time.time()
        self.recording_started = False
        self.timer.start(33)

    def process_frame(self):
        """Process a video frame and record metrics to CSV."""
        ret, frame = self.cap.read()
        if not ret:
            return

        # Handle stabilization period
        if not self.recording_started:
            elapsed = time.time() - self.recording_start_time
            if elapsed < self.stabilization_time:
                return
            else:
                self.recording_started = True
                self.ready_label.setText("Recording in progress...")

        # Process frame to extract facial landmarks
        landmarks = self.landmark_processor.process_frame(frame)

        if landmarks.face_detected:
            # Update metrics with eye landmarks
            metrics_values, _ = self.metrics_engine.update(landmarks.left_eye, landmarks.right_eye)

            # Record metrics to CSV
            timestamp = time.time() - self.recording_start_time
            self.csv_writer.writerow([
                f"{timestamp:.3f}",
                f"{metrics_values['EAR']:.4f}",
                f"{metrics_values['Blink Rate']:.2f}",
                f"{metrics_values['Blink Duration']:.4f}",
                f"{metrics_values['IBI']:.4f}",
                f"{metrics_values['Incomplete Blink Ratio']:.4f}",
                f"{metrics_values['PERCLOS']:.2f}"
            ])

    def end_examination(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        self.landmark_processor.release()
        self.ready_label.setText("Examination Finished")
        print("Examination ended")

    def goto_analysis(self):
        self.request_analysis.emit()
