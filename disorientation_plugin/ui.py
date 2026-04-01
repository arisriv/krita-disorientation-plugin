# UI code for the plugin will go here.

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QGroupBox
)
from .interventions import test_intervention

class DisorientationUI(QWidget):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self.setWindowTitle("Disorientation Interventions")
        self.setMinimumWidth(320)

        layout = QVBoxLayout()
        layout.setContentsMargins(16,16,16,16)
        layout.setSpacing(12)

        title = QLabel("Disorientation Interventions")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Prototype controls for creative workflow interventions")
        subtitle.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(subtitle)

        testing_group = QGroupBox("Testing")
        testing_layout = QVBoxLayout()

        self.test_button = QPushButton("Test Intervention")
        self.test_button.clicked.connect(test_intervention)
        self.test_button.setStyleSheet("padding: 6px;")
        testing_layout.addWidget(self.test_button)
        
        testing_group.setLayout(testing_layout)
        layout.addWidget(testing_group)

        permanence_group = QGroupBox("Permanence + Revision")  # ADDED
        permanence_layout = QVBoxLayout()  # ADDED

        self.mark_fading_checkbox = QCheckBox("Mark Fading")
        permanence_layout.addWidget(self.mark_fading_checkbox)

        self.status_label = QLabel("Status: Off")
        self.status_label.setStyleSheet("color: gray; font-size: 11px; padding-left: 2px;")  # ADDED
        permanence_layout.addWidget(self.status_label)

        self.mark_fading_checkbox.setChecked(self.plugin.mark_fading_enabled)
        self.toggle_mark_fading()

        self.mark_fading_checkbox.stateChanged.connect(self.toggle_mark_fading)

        permanence_group.setLayout(permanence_layout)
        layout.addWidget(permanence_group)

        self.setLayout(layout)

    def toggle_mark_fading(self):
        self.plugin.mark_fading_enabled = self.mark_fading_checkbox.isChecked()

        if self.mark_fading_checkbox.isChecked():
            self.status_label.setText("Status: On")
        else:
            self.status_label.setText("Status: Off")