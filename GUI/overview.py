from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QFileDialog, QApplication

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread

import os

import sys

import cv2

import pandas as pd



try:

    import winsound

except ImportError:

    winsound = None

from metrics.metrics import EyeMetrics

from metrics.facial_landmarks import MediaPipeProcessor

from ML_Model import inference as inference_module





class EyeHealthCaptureThread(QThread):

    metrics_updated = pyqtSignal(dict)

    camera_ready = pyqtSignal()



    def __init__(self, parent=None):

        super().__init__(parent)

        self.running = True

        self.eye_metrics = EyeMetrics()

        self.processor = None

        self.cap = None

        self._camera_ready = False

        self.last_metrics = self._empty_metrics()



    @staticmethod

    def _empty_metrics():

        return {

            "Blink Rate": 0.0,

            "Blink Duration": 0.0,

            "Incomplete Blink Ratio": 0.0,

        }



    def reset_metrics(self):

        self.eye_metrics = EyeMetrics()

        self.last_metrics = self._empty_metrics()



    def run(self):

        self.processor = MediaPipeProcessor(

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

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)



        while self.running:

            ret, frame = self.cap.read()

            if not ret:

                self.msleep(30)

                continue



            landmarks = self.processor.process_frame(frame)

            if landmarks.face_detected:

                metrics_values, _ = self.eye_metrics.update(landmarks.left_eye, landmarks.right_eye)

                self.last_metrics = metrics_values

            else:

                metrics_values = self.last_metrics



            if not self._camera_ready:

                self._camera_ready = True

                self.camera_ready.emit()



            self.metrics_updated.emit(metrics_values)

            self.msleep(30)



        if self.cap is not None:

            self.cap.release()

        if self.processor is not None:

            self.processor.release()



    def stop(self):

        self.running = False

        self.wait(1000)





class OverviewTab(QWidget):

    openModeRequested = pyqtSignal(int)

    INIT_DURATION = 30



    def __init__(self):

        super().__init__()

        self.setObjectName("overviewTab")



        self.health_thread = None

        self._monitoring_active = False

        self._initializing = False

        self._inference_active = False

        self.init_seconds_remaining = self.INIT_DURATION

        self.session_seconds = 0

        self.last_inference_state = None

        self.latest_metrics = {

            "Blink Rate": 0.0,

            "Blink Duration": 0.0,

            "Incomplete Blink Ratio": 0.0,

        }



        self.countdown_label = self._create_overlay_label()
        self.countdown_label.setFixedWidth(700)
        self.metrics_overlay = self._create_overlay_label()
        self.metrics_overlay.setFixedWidth(700)
        self.alert_label = self._create_overlay_label()
        self.alert_label.setFixedWidth(700)



        self.countdown_label.setStyleSheet(

            "background: rgba(0, 0, 0, 0.82); color: #ffffff; font-size: 40px; "

            "font-weight: 700; padding: 18px 22px; border-radius: 16px;"

        )

        self.metrics_overlay.setStyleSheet(

            "background: rgba(0, 0, 0, 0.78); color: #ffffff; font-size: 40px; "

            "padding: 18px 22px; border-radius: 14px; line-height: 1.45;"

        )

        self.alert_label.setStyleSheet(

            "background: rgba(180, 30, 30, 0.9); color: #ffffff; font-size: 40px; "

            "font-weight: 600; padding: 16px 20px; border-radius: 14px;"

        )



        self.session_timer = QTimer(self)

        self.session_timer.timeout.connect(self._on_session_tick)

        self.alarm_timer = QTimer(self)

        self.alarm_timer.setInterval(450)

        self.alarm_timer.timeout.connect(self._play_alarm_sound)



        self.countdown_label.hide()

        self.metrics_overlay.hide()

        self.alert_label.hide()



        self.destroyed.connect(self.stop_health_monitor)

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(36, 36, 36, 36)

        main_layout.setSpacing(24)

        main_layout.setAlignment(Qt.AlignTop)



        hero_title = QLabel("Eye Health Monitor")

        hero_title.setObjectName("heroTitle")

        hero_title.setAlignment(Qt.AlignCenter)



        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(18)

        cards_layout.setAlignment(Qt.AlignCenter)



        self.pdf_card = self.create_card("📄", "Open PDF Mode", "Browse a PDF file and launch it in the default reader.")

        self.video_card = self.create_card("▶", "Open Video Mode", "Browse a video and launch the default player.")



        self.pdf_card.clicked.connect(self.open_pdf)

        self.video_card.clicked.connect(self.open_video)



        cards_layout.addWidget(self.pdf_card)

        cards_layout.addWidget(self.video_card)



        info_label = QLabel("Choose your preferred mode and continue to read a PDF text or watch a movie with live health monitoring of your eyes.")

        info_label.setObjectName("heroNote")

        info_label.setWordWrap(True)

        info_label.setAlignment(Qt.AlignCenter)



        main_layout.addStretch()

        main_layout.addWidget(hero_title)

        main_layout.addLayout(cards_layout)

        main_layout.addWidget(info_label)

        main_layout.addStretch()



        self.setLayout(main_layout)



    def create_card(self, icon, title, subtitle):

        card = QPushButton()

        card.setObjectName("cardButton")

        card.setCursor(Qt.PointingHandCursor)

        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card.setMinimumSize(260, 240)

        card.setText("")

        card.setToolTip(title)



        inner = QWidget(card)

        inner_layout = QVBoxLayout(inner)

        inner_layout.setContentsMargins(18, 18, 18, 18)

        inner_layout.setSpacing(8)

        inner_layout.setAlignment(Qt.AlignCenter)



        icon_label = QLabel(icon)

        icon_label.setAlignment(Qt.AlignCenter)

        icon_label.setStyleSheet("font-size:48px; margin-bottom:6px;")



        title_label = QLabel(title)

        title_label.setAlignment(Qt.AlignCenter)

        title_label.setStyleSheet("font-size:20px; font-weight:700; margin-bottom:4px;")



        subtitle_label = QLabel(subtitle)

        subtitle_label.setAlignment(Qt.AlignCenter)

        subtitle_label.setWordWrap(True)

        subtitle_label.setStyleSheet("font-size:16px; color:#9aa7bf;")

        subtitle_label.setMaximumWidth(280)



        inner_layout.addWidget(icon_label)

        inner_layout.addWidget(title_label)

        inner_layout.addWidget(subtitle_label)



        card.setLayout(QVBoxLayout())

        card.layout().addWidget(inner)

        return card



    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._position_overlays()



    def _create_overlay_label(self):

        label = QLabel(self)

        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        label.setWordWrap(True)

        label.setContentsMargins(0, 0, 0, 0)

        label.setMinimumWidth(320)

        label.setMaximumWidth(420)

        return label



    def _position_overlays(self):

        margin = 24

        x = self.width() - margin

        y = margin

        if self.countdown_label.isVisible():

            self.countdown_label.adjustSize()

            self.countdown_label.move(x - self.countdown_label.width(), y)

            y += self.countdown_label.height() + 16

        if self.metrics_overlay.isVisible():

            self.metrics_overlay.adjustSize()

            self.metrics_overlay.move(x - self.metrics_overlay.width(), y)

            y += self.metrics_overlay.height() + 16

        if self.alert_label.isVisible():

            self.alert_label.adjustSize()

            self.alert_label.move(x - self.alert_label.width(), y)



    def open_pdf(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf);;All Files (*.*)")

        if not filename:

            return

        self._start_monitoring_and_open(filename)



    def open_video(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)")

        if not filename:

            return

        self._start_monitoring_and_open(filename)



    def _ensure_health_thread(self):

        if self.health_thread is not None and self.health_thread.isRunning():

            return



        if self.health_thread is not None:

            self.health_thread.stop()



        self.health_thread = EyeHealthCaptureThread()

        self.health_thread.metrics_updated.connect(self._on_metrics_updated)

        self.health_thread.camera_ready.connect(self._on_camera_ready)

        self.health_thread.start()



    def _on_camera_ready(self):

        if not self._monitoring_active:

            return

        self._update_metrics_overlay(self.latest_metrics)



    def _reset_active_session(self):
        self.session_timer.stop()
        self._stop_alarm()
        self._initializing = False
        self._inference_active = False
        self.last_inference_state = None
        self.alert_label.hide()

    def _start_monitoring_and_open(self, filename):
        self._ensure_health_thread()

        if self._monitoring_active:
            self._reset_active_session()

        if self.health_thread is not None:
            self.health_thread.reset_metrics()

        self._monitoring_active = True

        self._initializing = True

        self._inference_active = False

        self.init_seconds_remaining = self.INIT_DURATION

        self.session_seconds = 0

        self.last_inference_state = None

        self._stop_alarm()

        self.alert_label.hide()



        self.latest_metrics = dict(self.health_thread.last_metrics) if self.health_thread else EyeHealthCaptureThread._empty_metrics()

        self._update_metrics_overlay(self.latest_metrics)



        self.countdown_label.setText(f"Initializing: {self.init_seconds_remaining}s")

        self.countdown_label.show()

        self._position_overlays()



        self.session_timer.stop()
        self.session_timer.start(1000)

        try:
            os.startfile(filename)
        except Exception as e:
            print(f"Failed to open file: {e}")
            self.stop_health_monitor()



    def _on_session_tick(self):

        if self._initializing:

            self.init_seconds_remaining -= 1

            if self.init_seconds_remaining > 0:

                self.countdown_label.setText(f"Initializing: {self.init_seconds_remaining}s")

                self._position_overlays()

                return



            self._initializing = False

            self._inference_active = True

            self.session_seconds = 0

            self.countdown_label.setText("Session: 00:00")

            self._position_overlays()

            self._evaluate_inference()

            return



        self.session_seconds += 1

        minutes = self.session_seconds // 60

        seconds = self.session_seconds % 60

        self.countdown_label.setText(f"Session: {minutes:02d}:{seconds:02d}")

        self._position_overlays()



    def _play_alarm_sound(self):

        if winsound is not None and sys.platform == "win32":

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

        else:

            QApplication.beep()



    def _start_alarm(self):

        if not self.alarm_timer.isActive():

            self.alarm_timer.start()



    def _stop_alarm(self):

        self.alarm_timer.stop()



    def _on_metrics_updated(self, metrics):

        self.latest_metrics = metrics

        if not self._monitoring_active:

            return

        self._update_metrics_overlay(metrics)

        if self._inference_active:

            self._evaluate_inference()



    def _update_metrics_overlay(self, metrics):

        text = (

            f"<b>Blink Rate:</b> {metrics['Blink Rate']:.1f} / min<br>"

            f"<b>Blink Duration:</b> {metrics['Blink Duration']:.2f} s<br>"

            f"<b>Incomplete Blink Rate:</b> {metrics['Incomplete Blink Ratio']:.2f}"

        )

        self.metrics_overlay.setText(text)

        self.metrics_overlay.show()

        self._position_overlays()



    def _evaluate_inference(self):

        sample = pd.DataFrame({

            "Blink_Rate": [self.latest_metrics.get("Blink Rate", 0.0)],

            "Blink_Duration": [self.latest_metrics.get("Blink Duration", 0.0)],

            "Incomplete_Blink_Ratio": [self.latest_metrics.get("Incomplete Blink Ratio", 0.0)],

        })



        try:

            prediction = inference_module.rf_model.predict(sample)

            result = inference_module.label_encoder.inverse_transform(prediction)[0]

        except Exception as e:

            print(f"Inference failed: {e}")

            result = "Normal"



        if result == "Fatigue_Dryness":

            self._start_alarm()

            self.alert_label.setText(

                "Fatigue / Dryness detected. \n Please take a break."

            )

            self.alert_label.setStyleSheet(

                "background: rgba(200, 30, 30, 0.92); color: #ffffff; font-size: 40px; "

                "font-weight: 600; padding: 16px 20px; border-radius: 14px;"

            )

            self.alert_label.show()

            self.last_inference_state = result

        else:

            self._stop_alarm()

            self.alert_label.setText(

                "Normal eye state detected. Continue normally."

            )

            self.alert_label.setStyleSheet(

                "background: rgba(40, 140, 40, 0.92); color: #ffffff; font-size: 40px; "

                "font-weight: 600; padding: 16px 20px; border-radius: 14px;"

            )

            self.alert_label.show()

            self.last_inference_state = result



        self._position_overlays()



    def stop_health_monitor(self):
        self._reset_active_session()
        if self.health_thread is not None:
            self.health_thread.stop()
            self.health_thread = None
        self._monitoring_active = False
        self.countdown_label.hide()
        self.metrics_overlay.hide()
        self.alert_label.hide()


