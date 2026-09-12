"""Main stylesheet definitions for Eye Health Monitor."""

MAIN_STYLESHEET = """
QMainWindow {
    background: #11131a;
    color: #e8eef9;
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: #161a24;
    color: #c7d0e4;
    min-width: 170px;
    min-height: 50px;
    margin: 4px 4px 0 4px;
    padding: 10px 16px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border: 1px solid transparent;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #274270, stop:1 #3468b7);
    color: #f7fbff;
    border-color: #3f72d1;
}
QTabBar::tab:hover {
    background: #1f2736;
}
QWidget {
    background: #11131a;
    color: #e8eef9;
    font-family: "Segoe UI", "Arial", sans-serif;
}
QLabel {
    color: #c7d0e4;
}
QPushButton {
    background: #192029;
    color: #f4f7ff;
    border: 1px solid #263042;
    border-radius: 16px;
    padding: 14px 18px;
    font-size: 16px;
}
QPushButton:hover {
    background: #26344d;
}
QPushButton#primaryButton {
    background: #4aa3ff;
    color: #ffffff;
    border: 1px solid #4aa3ff;
}
QPushButton#secondaryButton {
    background: #1f2838;
    color: #d1d9eb;
}
QPushButton#cardButton {
    background: #182230;
    color: #f5f9ff;
    border: 1px solid #2d3a55;
    border-radius: 24px;
    text-align: left;
}
QPushButton#cardButton:hover {
    background: #23304b;
    border-color: #4aa3ff;
}
QLineEdit, QComboBox, QTextEdit {
    background: #161a24;
    border: 1px solid #282e40;
    border-radius: 12px;
    padding: 10px;
    color: #ebeff7;
}
QComboBox {
    padding-right: 24px;
}
QTextEdit {
    min-height: 220px;
}
QFrame {
    background: #151a25;
    border: 1px solid #202a38;
    border-radius: 20px;
}
QScrollArea, QScrollBar {
    background: transparent;
}
"""
