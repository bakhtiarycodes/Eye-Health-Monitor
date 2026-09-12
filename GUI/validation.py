from PyQt5.QtWidgets import QMessageBox

REQUIRED_METRIC_NAMES = [
    "EAR",
    "Blink Rate",
    "Blink Duration",
    "IBI",
    "Incomplete Blink Ratio",
    "PERCLOS"
]


def show_alert(parent, message, title="Alert"):
    """Show an alert message to the user."""
    QMessageBox.warning(parent, title, message)


def show_info(parent, message, title="Info"):
    """Show a confirmation or informational message to the user."""
    QMessageBox.information(parent, title, message)


def validate_examination_language(text_display):
    """Return True if at least one language text is selected and visible."""
    return bool(text_display.toPlainText().strip())


def validate_personal_info(age_text, gender_text, country_text, occupation_text):
    """Return True if required personal fields are not empty."""
    return all(
        bool(field and field.strip())
        for field in [age_text, gender_text, country_text, occupation_text]
    )


def validate_metric_labels(metric_labels):
    """Return True if all required metric labels contain valid values."""
    for metric_name in REQUIRED_METRIC_NAMES:
        if metric_name not in metric_labels:
            return False
        values = metric_labels[metric_name]
        for state in ("min", "max", "avg"):
            value = values[state].text().strip()
            if not value or value == "--":
                return False
    return True


def validate_analysis_fields(age_text, gender_text, country_text, occupation_text, metric_labels):
    """Return True when analysis fields and metrics are complete."""
    return (
        validate_personal_info(age_text, gender_text, country_text, occupation_text)
        and validate_metric_labels(metric_labels)
    )
