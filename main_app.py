import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtCore import Qt, QTimer
from GUI.overview import OverviewTab
from GUI.observation import ObservationTab
from GUI.examination import ExaminationTab
from GUI.analysis import AnalysisTab
from GUI.user_guide import show_user_guide
from style import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye Health Monitor")
        self.setWindowState(Qt.WindowMaximized)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)

        self.home_tab = OverviewTab()
        self.observation_tab = ObservationTab()
        self.examination_tab = ExaminationTab()
        self.analysis_tab = AnalysisTab()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.observation_tab, "Observation")
        self.tabs.addTab(self.examination_tab, "Examination")
        self.tabs.addTab(self.analysis_tab, "Analysis")

        self.setCentralWidget(self.tabs)
        self.setStyleSheet(MAIN_STYLESHEET)

        self.home_tab.openModeRequested.connect(self.open_mode_from_home)
        self.examination_tab.request_analysis.connect(self.open_analysis_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def open_mode_from_home(self, section_index):
        self.tabs.setCurrentWidget(self.examination_tab)
        self.examination_tab.set_section(section_index)

    def open_analysis_tab(self):
        self.tabs.setCurrentWidget(self.analysis_tab)

    def _on_tab_changed(self, index):
        if self.tabs.widget(index) is self.observation_tab:
            self.observation_tab.start_camera()
        else:
            self.observation_tab.stop_camera()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    QTimer.singleShot(0, lambda: show_user_guide(window))
    sys.exit(app.exec_())
