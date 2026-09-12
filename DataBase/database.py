# database.py
import sqlite3


class EyeMetricsDatabase:
    def __init__(self, db_name="eye_metrics.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # جدول یکپارچه: اطلاعات شخصی + 6 پارامتر metrics با min/max
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS eye_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age INTEGER,
                gender TEXT,
                country TEXT,
                occupation TEXT,

                ear_min TEXT,
                ear_max TEXT,

                blink_rate_min TEXT,
                blink_rate_max TEXT,

                blink_duration_min TEXT,
                blink_duration_max TEXT,

                ibi_min TEXT,
                ibi_max TEXT,

                incomplete_blink_ratio_min TEXT,
                incomplete_blink_ratio_max TEXT,

                perclos_min TEXT,
                perclos_max TEXT
            )
        """)
        self.conn.commit()

    def store_data(self, personal_info, metrics):
        """
        personal_info = {
            "age": int,
            "gender": str,
            "country": str,
            "occupation": str
        }
        metrics = {
            "EAR (Eye Aspect Ratio)": ("0.20", "0.35"),
            "Blink Rate": ("15", "25"),
            "Blink Duration": ("0.1", "0.4"),
            "IBI (Inter-Blink Interval)": ("1", "6"),
            "Incomplete Blink Ratio": ("0", "0.4"),
            "PERCLOS": ("0", "40")
        }
        """
        self.cursor.execute("""
            INSERT INTO eye_metrics (
                age, gender, country, occupation,
                ear_min, ear_max,
                blink_rate_min, blink_rate_max,
                blink_duration_min, blink_duration_max,
                ibi_min, ibi_max,
                incomplete_blink_ratio_min, incomplete_blink_ratio_max,
                perclos_min, perclos_max
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            personal_info["age"],
            personal_info["gender"],
            personal_info["country"],
            personal_info["occupation"],
            metrics["EAR (Eye Aspect Ratio)"][0],
            metrics["EAR (Eye Aspect Ratio)"][1],
            metrics["Blink Rate"][0],
            metrics["Blink Rate"][1],
            metrics["Blink Duration"][0],
            metrics["Blink Duration"][1],
            metrics["IBI (Inter-Blink Interval)"][0],
            metrics["IBI (Inter-Blink Interval)"][1],
            metrics["Incomplete Blink Ratio"][0],
            metrics["Incomplete Blink Ratio"][1],
            metrics["PERCLOS"][0],
            metrics["PERCLOS"][1]
        ))
        self.conn.commit()

    def fetch_all_data(self):
        self.cursor.execute("SELECT * FROM eye_metrics")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


# ===========================
# Example Usage
# ===========================
if __name__ == "__main__":
    db = EyeMetricsDatabase()

    personal_info = {
        "age": 28,
        "gender": "Female",
        "country": "Canada",
        "occupation": "Researcher"
    }

    metrics = {
        "EAR (Eye Aspect Ratio)": ("0.20", "0.35"),
        "Blink Rate": ("15", "25"),
        "Blink Duration": ("0.1", "0.4"),
        "IBI (Inter-Blink Interval)": ("1", "6"),
        "Incomplete Blink Ratio": ("0", "0.4"),
        "PERCLOS": ("0", "40")
    }

    db.store_data(personal_info, metrics)

    all_data = db.fetch_all_data()
    for row in all_data:
        print(row)

    db.close()
