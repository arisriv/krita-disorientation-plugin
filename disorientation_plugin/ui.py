# UI code for the plugin will go here.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox
from .interventions import test_intervention

class DisorientationUI(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Disorientation Interventions")
        layout.addWidget(title)

        self.test_button = QPushButton("Test Intervention")
        layout.addWidget(self.test_button)

        self.test_button.clicked.connect(test_intervention)

        self.mark_fading_checkbox = QCheckBox("Mark Fading")
        layout.addWidget(self.mark_fading_checkbox)

        self.status_label = QLabel("Status: Off")
        layout.addWidget(self.status_label)

        self.mark_fading_checkbox.stateChanged.connect(self.toggle_mark_fading)

        self.setLayout(layout)

    def toggle_mark_fading(self):

        if self.mark_fading_checkbox.isChecked():
            self.status_label.setText("Status: On")
        else:
            self.status_label.setText("Status: Off")