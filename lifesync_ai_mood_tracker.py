import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt


class LifeSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D-LifeSync - AI Mood & Routine Tracker")
        self.setGeometry(100, 100, 600, 700)
        self.setup_ui()
        self.create_db()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("🧠 D-LifeSync")
        self.title.setFont(QFont("Arial", 20))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.mood_label = QLabel("How are you feeling today?")
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["😊 Happy", "😐 Okay", "😔 Sad", "😡 Angry", "😴 Tired", "😕 Anxious"])
        layout.addWidget(self.mood_label)
        layout.addWidget(self.mood_combo)

        self.journal_label = QLabel("Write something about your day:")
        self.journal_text = QTextEdit()
        layout.addWidget(self.journal_label)
        layout.addWidget(self.journal_text)

        self.submit_btn = QPushButton("Save Entry")
        self.submit_btn.clicked.connect(self.save_entry)
        layout.addWidget(self.submit_btn)

        self.suggestion_btn = QPushButton("Get Smart Suggestion")
        self.suggestion_btn.clicked.connect(self.show_suggestion)
        layout.addWidget(self.suggestion_btn)

        self.view_log_btn = QPushButton("View Mood History")
        self.view_log_btn.clicked.connect(self.view_logs)
        layout.addWidget(self.view_log_btn)

        self.view_chart_btn = QPushButton("Show Mood Chart")
        self.view_chart_btn.clicked.connect(self.show_chart)
        layout.addWidget(self.view_chart_btn)

        self.setLayout(layout)

    def create_db(self):
        self.conn = sqlite3.connect("lifesync.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                mood TEXT,
                journal TEXT
            )
        ''')
        self.conn.commit()

    def save_entry(self):
        date = datetime.date.today().isoformat()
        mood = self.mood_combo.currentText()
        journal = self.journal_text.toPlainText()

        self.cursor.execute("INSERT INTO moods (date, mood, journal) VALUES (?, ?, ?)",
                            (date, mood, journal))
        self.conn.commit()
        QMessageBox.information(self, "Saved", "Your entry has been saved!")

    def show_suggestion(self):
        today = datetime.date.today().isoformat()
        self.cursor.execute("SELECT mood FROM moods WHERE date=?", (today,))
        result = self.cursor.fetchone()

        if not result:
            QMessageBox.warning(self, "No Entry", "Please save a mood entry for today first!")
            return

        mood = result[0]
        suggestion = self.generate_ai_suggestion(mood)
        QMessageBox.information(self, "Smart Suggestion", suggestion)

    def generate_ai_suggestion(self, mood):
        if "Happy" in mood:
            return "Keep spreading that joy! ✨ Maybe share it with a friend today."
        elif "Sad" in mood:
            return "It's okay to feel down. Maybe try writing your thoughts or listening to calming music."
        elif "Tired" in mood:
            return "You seem tired — try a short walk or a power nap."
        elif "Angry" in mood:
            return "Deep breaths can help. Maybe write what's bothering you?"
        elif "Anxious" in mood:
            return "Try meditation or a breathing app for 5 minutes."
        else:
            return "You’ve been consistent this week — great job! Keep the streak going! 🔥"

    def view_logs(self):
        self.cursor.execute("SELECT date, mood, journal FROM moods ORDER BY date DESC LIMIT 7")
        rows = self.cursor.fetchall()

        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Date", "Mood", "Journal"])
        table.resize(600, 400)

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)
                table.setItem(i, j, item)

        log_window = QWidget()
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Your Last 7 Entries"))
        log_layout.addWidget(table)
        log_window.setLayout(log_layout)
        log_window.setWindowTitle("Mood History")
        log_window.resize(600, 300)
        log_window.show()
        self.child_window = log_window

    def show_chart(self):
        self.cursor.execute("SELECT date, mood FROM moods ORDER BY date DESC LIMIT 7")
        data = self.cursor.fetchall()[::-1]
        dates = [d[0][-5:] for d in data]
        moods = [self.mood_to_value(m[1]) for m in data]

        plt.figure(figsize=(8, 4))
        plt.plot(dates, moods, marker='o', linestyle='-', color='skyblue')
        plt.title("Mood Trend (Last 7 Days)")
        plt.ylabel("Mood Score")
        plt.xlabel("Date")
        plt.grid(True)
        plt.ylim(0, 6)
        plt.yticks([1, 2, 3, 4, 5, 6],
                   ["😕", "😴", "😡", "😔", "😐", "😊"])
        plt.tight_layout()
        plt.show()

    def mood_to_value(self, mood):
        mapping = {
            "😊 Happy": 6,
            "😐 Okay": 5,
            "😔 Sad": 4,
            "😡 Angry": 3,
            "😴 Tired": 2,
            "😕 Anxious": 1
        }
        return mapping.get(mood, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LifeSyncApp()
    window.show()
    sys.exit(app.exec_())
