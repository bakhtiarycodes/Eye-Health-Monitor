from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QFileDialog, QLineEdit, QComboBox, QGridLayout, QCompleter
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import Qt
from DataBase.database import EyeMetricsDatabase
from GUI.validation import show_alert, show_info, validate_analysis_fields
import csv
import statistics
import io
import matplotlib.pyplot as plt

class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.db = EyeMetricsDatabase()  # دیتابیس باز می‌شود یا ساخته می‌شود

        # ============================
        # PERSONAL INFORMATION PANEL
        # ============================
        self.personal_panel = QFrame()
        self.personal_panel.setObjectName("infoPanel")
        self.personal_panel.setFrameShape(QFrame.StyledPanel)

        personal_layout = QGridLayout()
        personal_layout.setVerticalSpacing(32)
        personal_layout.setHorizontalSpacing(40)
        personal_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Personal Information")
        title.setObjectName("sectionTitle")
        personal_layout.addWidget(title, 0, 0, 1, 4)

        self.age_label = QLabel("Age")
        self.age_input = QLineEdit()
        self.age_input.setMinimumHeight(30)
        self.gender_label = QLabel("Gender")
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        self.gender_input.setMinimumHeight(30)
        self.country_label = QLabel("Country")
        self.country_input = QComboBox()
        self.country_input.setEditable(True)
        countries = ["Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria",
                     "Bangladesh", "Belgium", "Brazil", "Canada", "Chile", "China", "Colombia",
                     "Denmark", "Egypt", "Finland", "France", "Germany", "Greece", "Hungary",
                     "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
                     "Japan", "Kazakhstan", "Kenya", "Malaysia", "Mexico", "Morocco",
                     "Netherlands", "New Zealand", "Nigeria", "Norway", "Pakistan",
                     "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania",
                     "Russia", "Saudi Arabia", "Singapore", "South Africa", "South Korea",
                     "Spain", "Sweden", "Switzerland", "Thailand", "Turkey",
                     "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
                     "Uzbekistan", "Vietnam", "Yemen", "Zimbabwe"]
        self.country_input.addItems(countries)
        completer = QCompleter(countries)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.country_input.setCompleter(completer)
        self.country_input.setMinimumHeight(30)
        self.job_label = QLabel("Occupation")
        self.job_input = QComboBox()
        self.job_input.addItems(["Student", "Teacher", "Engineer", "Doctor", "Researcher",
                                 "Programmer", "Office Worker", "Designer", "Driver", "Business", "Other"])
        self.job_input.setMinimumHeight(30)

        personal_layout.addWidget(self.age_label, 1, 0)
        personal_layout.addWidget(self.age_input, 1, 1)
        personal_layout.addWidget(self.gender_label, 1, 2)
        personal_layout.addWidget(self.gender_input, 1, 3)
        personal_layout.addWidget(self.country_label, 2, 0)
        personal_layout.addWidget(self.country_input, 2, 1)
        personal_layout.addWidget(self.job_label, 2, 2)
        personal_layout.addWidget(self.job_input, 2, 3)
        self.personal_panel.setLayout(personal_layout)

        # ============================
        # MIDDLE PANEL: Measured Metrics
        # ============================
        self.metrics_panel = QFrame()
        self.metrics_panel.setObjectName("infoPanel")
        self.metrics_panel.setFrameShape(QFrame.StyledPanel)

        metrics_layout = QGridLayout()
        metrics_layout.setVerticalSpacing(32)
        metrics_layout.setHorizontalSpacing(40)
        metrics_layout.setContentsMargins(30, 30, 30, 30)

        title_metrics = QLabel("Measured Metrics")
        title_metrics.setObjectName("sectionTitle")
        metrics_layout.addWidget(title_metrics, 0, 0, 1, 5)

        headers = ["Metric", "Minimum", "Maximum", "Average", "Normal Range", "Unit"]
        for col, text in enumerate(headers):
            label = QLabel(text)
            label.setStyleSheet("font-weight:bold;")
            metrics_layout.addWidget(label, 1, col)

        parameters = [("EAR", "0.20 - 0.35", "ratio"),
                      ("Blink Rate", "15 - 25", "blinks/min"),
                      ("Blink Duration", "0.1 - 0.4", "s"),
                      ("IBI", "1 - 6", "s"),
                      ("Incomplete Blink Ratio", "0 - 0.4", "ratio"),
                      ("PERCLOS", "5 - 20", "%")]

        self.metric_labels = {}
        for i, (name, normal_range, unit) in enumerate(parameters, start=2):
            metrics_layout.addWidget(QLabel(name), i, 0)
            min_label = QLabel("--")
            max_label = QLabel("--")
            avg_label = QLabel("--")
            normal_label = QLabel(normal_range)
            unit_label = QLabel(unit)
            metrics_layout.addWidget(min_label, i, 1)
            metrics_layout.addWidget(max_label, i, 2)
            metrics_layout.addWidget(avg_label, i, 3)
            metrics_layout.addWidget(normal_label, i, 4)
            metrics_layout.addWidget(unit_label, i, 5)
            self.metric_labels[name] = {"min": min_label, "max": max_label, "avg": avg_label,
                                        "normal": normal_label, "unit": unit_label}

        self.metrics_panel.setLayout(metrics_layout)

        # ============================
        # GRAPH PANEL
        # ============================
        self.graph_panel = QFrame()
        self.graph_panel.setObjectName("infoPanel")
        self.graph_panel.setFrameShape(QFrame.StyledPanel)
        graph_layout = QVBoxLayout()
        self.graph_title = QLabel("Graphs")
        self.graph_title.setObjectName("sectionTitle")
        graph_layout.addWidget(self.graph_title)

        sub_graph_layout = QHBoxLayout()

        #EAR Graph
        self.ear_graph_label = QLabel("EAR graph will appear here.")
        self.ear_graph_label.setAlignment(Qt.AlignTop)
        self.ear_graph_label.setFixedHeight(500)

        ear_frame = QVBoxLayout()
        ear_frame.addWidget(QLabel("EAR Graph"))
        ear_frame.addWidget(self.ear_graph_label)

        ear_widget = QFrame()
        ear_widget.setLayout(ear_frame)

        sub_graph_layout.addWidget(ear_widget)

        graph_layout.addLayout(sub_graph_layout)
        self.graph_panel.setLayout(graph_layout)

        # ============================
        # BUTTONS
        # ============================
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setStyleSheet("font-size:24px; font-weight:bold;")
        self.analyze_btn.clicked.connect(self.analyze_data)
        self.graph_btn = QPushButton("Graphs")
        self.graph_btn.setStyleSheet("font-size:24px; font-weight:bold;")
        self.graph_btn.clicked.connect(self.draw_graph)

        main_layout.addWidget(self.personal_panel)
        main_layout.addWidget(self.analyze_btn)
        main_layout.addWidget(self.metrics_panel)
        main_layout.addWidget(self.graph_btn)
        main_layout.addWidget(self.graph_panel)

        button_layout = QHBoxLayout()
        self.store_btn = QPushButton("Store to Database")
        self.store_btn.setStyleSheet("font-size:24px; font-weight:bold;")
        self.export_btn = QPushButton("Export")
        self.export_btn.setStyleSheet("font-size:24px; font-weight:bold;")
        self.print_btn = QPushButton("Print")
        self.print_btn.setStyleSheet("font-size:24px; font-weight:bold;")
        button_layout.addWidget(self.store_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.print_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.store_btn.clicked.connect(self.store_to_database)
        self.export_btn.clicked.connect(self.export_result)
        self.print_btn.clicked.connect(self.print_result)
        self.last_saved_file = None

    # =================================
    # Analyze Data
    # =================================
    def analyze_data(self):
        csv_file = "eye_metrics.csv"
        data_dict = {"EAR": [], "Blink Rate": [], "Blink Duration": [], "IBI": [],
                     "Incomplete Blink Ratio": [], "PERCLOS": []}
        try:
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key in data_dict.keys():
                        value = row.get(key)
                        if value is not None:
                            try:
                                data_dict[key].append(float(value))
                            except ValueError:
                                pass
            for param, values in data_dict.items():
                if values:
                    self.metric_labels[param]["min"].setText(str(round(min(values), 3)))
                    self.metric_labels[param]["max"].setText(str(round(max(values), 3)))
                    self.metric_labels[param]["avg"].setText(str(round(statistics.mean(values), 3)))
                else:
                    self.metric_labels[param]["min"].setText("--")
                    self.metric_labels[param]["max"].setText("--")
                    self.metric_labels[param]["avg"].setText("--")
            print("Analysis completed successfully!")
        except FileNotFoundError:
            print(f"CSV file not found: {csv_file}")

    # =================================
    # Draw Graphs
    # =================================
    def draw_graph(self):

        csv_file = "eye_metrics.csv"
        data_dict = {"EAR": []}

        try:

            with open(csv_file, newline='') as f:

                reader = csv.DictReader(f)

                for row in reader:

                    value = row.get("EAR")

                    if value is not None:

                        try:

                            data_dict["EAR"].append(float(value))

                        except ValueError:

                            pass

            frames_per_20s = 300

            ear_values = data_dict["EAR"]

            if len(ear_values) >= frames_per_20s:

                start_index = len(ear_values) // 2 - frames_per_20s // 2
                end_index = start_index + frames_per_20s

            else:

                start_index = 0
                end_index = len(ear_values)

            data_dict["EAR"] = data_dict["EAR"][start_index:end_index]

            time = [i * 100 for i in range(len(data_dict["EAR"]))]

            # اندازه بزرگ‌تر برای گراف

            width = 45
            height = 5

            fig, ax = plt.subplots(figsize=(width, height))

            ax.plot(
                time,
                data_dict["EAR"],
                color="blue",
                label="EAR"
            )

            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("EAR")

            ax.set_title("EAR Over 30s (Middle of Trial)")

            ax.grid(True)
            ax.legend()

            self.ear_graph_label.setPixmap(
                self.fig_to_pixmap(fig)
            )

            plt.close(fig)

            print("EAR graph drawn successfully!")

        except FileNotFoundError:

            print(f"CSV file not found: {csv_file}")
    def fig_to_pixmap(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        from PyQt5.QtGui import QImage, QPixmap
        img = QImage.fromData(buf.getvalue())
        return QPixmap.fromImage(img)

    # =================================
    # Store, Export, Print (unchanged)
    # =================================
    def store_to_database(self):
        personal_info = {
            "age": self.age_input.text(),
            "gender": self.gender_input.currentText(),
            "country": self.country_input.currentText(),
            "occupation": self.job_input.currentText()
        }

        if not validate_analysis_fields(
            personal_info["age"],
            personal_info["gender"],
            personal_info["country"],
            personal_info["occupation"],
            self.metric_labels
        ):
            show_alert(self, "All required fields must be filled.")
            return

        metrics = {
            "EAR (Eye Aspect Ratio)": (self.metric_labels["EAR"]["min"].text(),
                                       self.metric_labels["EAR"]["max"].text()),
            "Blink Rate": (self.metric_labels["Blink Rate"]["min"].text(),
                           self.metric_labels["Blink Rate"]["max"].text()),
            "Blink Duration": (self.metric_labels["Blink Duration"]["min"].text(),
                               self.metric_labels["Blink Duration"]["max"].text()),
            "IBI (Inter-Blink Interval)": (self.metric_labels["IBI"]["min"].text(),
                                          self.metric_labels["IBI"]["max"].text()),
            "Incomplete Blink Ratio": (self.metric_labels["Incomplete Blink Ratio"]["min"].text(),
                                       self.metric_labels["Incomplete Blink Ratio"]["max"].text()),
            "PERCLOS": (self.metric_labels["PERCLOS"]["min"].text(),
                        self.metric_labels["PERCLOS"]["max"].text())
        }
        self.db.store_data(personal_info, metrics)
        show_info(self, "Data stored successfully in database!", "Success")

    def export_result(self):
        if not validate_analysis_fields(
            self.age_input.text(),
            self.gender_input.currentText(),
            self.country_input.currentText(),
            self.job_input.currentText(),
            self.metric_labels
        ):
            show_alert(self, "Cannot export. All required fields must be filled.")
            return

        pixmap = self.grab()
        filename, _ = QFileDialog.getSaveFileName(self, "Export Result", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        if filename:
            if filename.lower().endswith(".png"):
                pixmap.save(filename, "PNG")
            elif filename.lower().endswith(".pdf"):
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(filename)
                from PyQt5.QtGui import QPainter
                painter = QPainter()
                painter.begin(printer)
                rect = painter.viewport()
                pixmap_scaled = pixmap.scaled(rect.size(), Qt.KeepAspectRatio)
                painter.drawPixmap(0, 0, pixmap_scaled)
                painter.end()
            self.last_saved_file = filename

    def print_result(self):
        if not self.last_saved_file:
            show_alert(self, "Please export the data before printing.")
            return
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            pixmap = self.grab()
            from PyQt5.QtGui import QPainter
            painter = QPainter()
            painter.begin(printer)
            rect = painter.viewport()
            pixmap_scaled = pixmap.scaled(rect.size(), Qt.KeepAspectRatio)
            painter.drawPixmap(0, 0, pixmap_scaled)
            painter.end()
