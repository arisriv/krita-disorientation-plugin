# Separate file for dialogs so interventions can create their own dialogs without
# creating circular imports between interventions and ui

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QPushButton, QWidget  # ADDED
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont


class CountdownDialog(QDialog):
    countdown_finished = pyqtSignal()  # ADDED

    def __init__(self, title, message, duration_seconds, parent=None):
        
        super().__init__(parent)

        self.time_left = duration_seconds
        self.setWindowTitle(title)
        self.setMinimumWidth(320)

        layout = QVBoxLayout()

        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        layout.addSpacing(8)

        timer_box = QFrame()
        timer_box.setFrameShape(QFrame.Box)
        timer_box.setLineWidth(2)

        timer_layout = QVBoxLayout()
        timer_layout.setContentsMargins(12, 12, 12, 12)

        # Show a neutral pre-start state instead of immediately showing the timer
        self.timer_label = QLabel("Ready?")
        self.timer_label.setAlignment(Qt.AlignCenter)

        timer_font = QFont()
        timer_font.setPointSize(16)
        timer_font.setBold(True)
        timer_font.setStyleHint(QFont.Monospace)
        self.timer_label.setFont(timer_font)

        # Keep the timer width fixed so the box does not resize as digits change
        self.timer_label.setFixedWidth(90)

        timer_layout.addWidget(self.timer_label)
        timer_box.setLayout(timer_layout)

        layout.addWidget(timer_box, alignment=Qt.AlignCenter)

        # ADDED: put the button inside its own container so the layout keeps
        # a stable slot for the button area even after the button disappears
        self.button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.start_button = QPushButton("Begin")
        self.start_button.clicked.connect(self.start_countdown)
        button_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.button_container.setLayout(button_layout)

        # ADDED: preserve the height of the button area after hiding the button
        self.button_container.setFixedHeight(self.start_button.sizeHint().height())

        layout.addWidget(self.button_container, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def start_countdown(self):
        # Hide only the button, not the container holding it, so the layout
        # keeps the same vertical spacing and nothing shifts downward.
        self.start_button.hide()

        # Switch from the "Ready?" state to the real timer
        self.timer_label.setText(self.format_time(self.time_left))

        # Start the countdown
        self.timer.start(1000)

    def update_timer(self):
        self.time_left -= 1

        if self.time_left <= 0:
            self.timer.stop()
            self.timer_label.setText("Time is up.")
            self.countdown_finished.emit()  # ADDED
            return

        self.timer_label.setText(self.format_time(self.time_left))

        if self.time_left <= 15:
            self.timer_label.setStyleSheet("color: red;")

    def format_time(self, seconds):
        # Convert seconds into MM:SS format
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def closeEvent(self, event):
        # Block closing while countdown is active
        if self.timer.isActive():
            event.ignore()
            self.show()
        else:
            self.timer.stop()
            super().closeEvent(event)