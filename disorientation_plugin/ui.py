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

        # Store reference to main plugin so UI can read/write plugin state
        super().__init__()
        self.plugin = plugin

        self.setWindowTitle("Disorientation Interventions")
        self.setMinimumWidth(320)

        # ==================================================
        # Main layout setup
        # ==================================================
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16,16,16,16)
        layout.setSpacing(12)

        title = QLabel("Disorientation Interventions")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Prototype controls for creative workflow interventions")
        subtitle.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(subtitle)

        # --- Testing controls ---
        testing_group, testing_layout = self.make_section("Testing")

        self.test_button = QPushButton("Test Intervention")
        self.test_button.clicked.connect(test_intervention)
        self.test_button.setStyleSheet("padding: 6px;")
        testing_layout.addWidget(self.test_button)

        layout.addWidget(testing_group)

        # ==================================================
        # Permanence + Revision interventions
        # ==================================================
        permanence_group, permanence_layout = self.make_section("Permanence + Revision")

        self.mark_fading_checkbox = QCheckBox("Mark Fading")
        permanence_layout.addWidget(self.mark_fading_checkbox)

        self.status_label = QLabel("Status: Off")
        self.status_label.setStyleSheet("color: gray; font-size: 11px; padding-left: 2px;")
        permanence_layout.addWidget(self.status_label)

        # Initialize checkbox from stored plugin state so that UI reflects
        # current intervention state when dialog opens; second line updates
        # label immediately to match stored state
        self.mark_fading_checkbox.setChecked(self.plugin.mark_fading_enabled)
        self.toggle_mark_fading()

        # Directs connection between UI checkbox and updating the plugin state
        self.mark_fading_checkbox.stateChanged.connect(self.toggle_mark_fading)

        layout.addWidget(permanence_group)
        
        self.setLayout(layout)

    def toggle_mark_fading(self):
        # Persist checkbox state on plugin to survive dialog close/reopen
        self.plugin.mark_fading_enabled = self.mark_fading_checkbox.isChecked()

        if self.mark_fading_checkbox.isChecked():
            self.status_label.setText("Status: On")
        else:
            self.status_label.setText("Status: Off")
    
    # Helper to create consistently styled UI
    def make_section(self, title):
        group = QGroupBox(title)

        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        group.setLayout(group_layout)
        return group, group_layout