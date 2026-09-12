from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QHBoxLayout, QApplication,
)
from PyQt5.QtCore import Qt


GUIDE_HTML = """
<h2 style="color:#4aa3ff;">Welcome to Eye Health Monitor</h2>
<p>This application helps you monitor eye health while reading or watching content on your computer.
It uses your webcam and MediaPipe face tracking to measure blink patterns and detect signs of
fatigue or dryness.</p>

<h3 style="color:#7eb8ff;">App Tabs</h3>
<p>The app has four main sections, accessible from the tab bar at the top:</p>

<h4>1. Home</h4>
<ul>
<li>Click <b>Open PDF Mode</b> to browse and open a PDF in your default reader.</li>
<li>Click <b>Open Video Mode</b> to browse and open a video in your default player.</li>
<li>After you select a file, the webcam starts automatically and eye monitoring begins.</li>
<li>A <b>30-second warmup</b> runs first (shown as &quot;Initializing&quot;). Live blink metrics
update during this period.</li>
<li>When warmup finishes, the <b>session timer</b> starts and the app classifies your eye state
as <b>Normal</b> or <b>Fatigue / Dryness</b>.</li>
<li>If fatigue or dryness is detected, an <b>alarm sound</b> plays until your state returns to normal.</li>
<li>Overlays on the right show the timer, live metrics, and status alerts.</li>
</ul>

<h4>2. Observation</h4>
<ul>
<li>Switch to this tab to see a <b>live webcam view</b> with facial landmarks drawn on your face.</li>
<li>The left panel shows real-time metrics: EAR, Blink Rate, Blink Duration, IBI,
Incomplete Blink Ratio, and PERCLOS.</li>
<li>The camera activates only when you open this tab and turns off when you leave it.</li>
<li>Use this mode to watch your metrics directly without opening a PDF or video.</li>
</ul>

<h4>3. Examination</h4>
<ul>
<li>Select a reading language: <b>English</b> or <b>中文</b>.</li>
<li>Press <b>Start Examination</b> when you are ready.</li>
<li>Wait 5 seconds, then the app records eye metrics from your webcam while you read the text.</li>
<li>A 20-second stabilization period runs before data is saved to <b>eye_metrics.csv</b>.</li>
<li>Press <b>End of Examination</b> when you finish reading.</li>
<li>Press <b>Review Analysis</b> to go to the Analysis tab with your recorded data.</li>
</ul>

<h4>4. Analysis</h4>
<ul>
<li>Fill in your <b>personal information</b> (age, gender, country, occupation).</li>
<li>Click <b>Analyze</b> to load statistics from <b>eye_metrics.csv</b> (from your last examination).</li>
<li>View minimum, maximum, and average values compared to normal ranges.</li>
<li>Click <b>Graphs</b> to display an EAR chart over time.</li>
<li>Use <b>Store to Database</b>, <b>Export</b>, or <b>Print</b> to save or share your results.</li>
</ul>

<h3 style="color:#7eb8ff;">Tips for Best Results</h3>
<ul>
<li>Sit facing the camera with your face clearly visible and good lighting.</li>
<li>Keep a comfortable distance from the screen (about 50–70 cm).</li>
<li>Allow camera access when prompted by your system.</li>
<li>Only one monitoring session should run at a time (Home or Observation).</li>
</ul>

<p style="color:#9aa7bf;"><i>Click <b>Get Started</b> below to begin using the app.</i></p>
"""


class UserGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Guide — Eye Health Monitor")
        self.setModal(True)
        self.setMinimumSize(1280, 1140)
        self.resize(1280, 1140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("How to Use Eye Health Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: 700; color: #f7fbff; padding-bottom: 4px;")
        layout.addWidget(title)

        self.content = QTextBrowser()
        self.content.setOpenExternalLinks(False)
        self.content.setHtml(GUIDE_HTML)
        self.content.setStyleSheet(
            "QTextBrowser { background: #151a25; border: 1px solid #202a38; border-radius: 12px; "
            "padding: 12px; font-size: 28px; color: #c7d0e4; }"
        )
        layout.addWidget(self.content, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.start_btn = QPushButton("Get Started")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setMinimumWidth(160)
        self.start_btn.setStyleSheet("font-size: 24px; padding: 12px 24px;")
        self.start_btn.clicked.connect(self.accept)
        button_row.addWidget(self.start_btn)
        button_row.addStretch()
        layout.addLayout(button_row)

        self.setStyleSheet(
            "QDialog { background: #11131a; color: #e8eef9; }"
            "QPushButton#primaryButton { background: #4aa3ff; color: #ffffff; border-radius: 12px; }"
            "QPushButton#primaryButton:hover { background: #3b8de0; }"
        )

    def show_centered(self):
        self.adjustSize()
        screen = QApplication.primaryScreen()
        if screen is not None:
            center = screen.availableGeometry().center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())
        self.exec_()


def show_user_guide(parent=None):
    UserGuideDialog(parent).show_centered()
