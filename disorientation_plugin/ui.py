# UI code for the plugin will go here.

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QCheckBox,
    QListWidget,
    QGroupBox
)
from .interventions import test_intervention
from .catalog import INTERVENTION_CATALOG

class DisorientationUI(QWidget):

    def __init__(self, plugin):

        # Store reference to main plugin so UI can read/write plugin state
        super().__init__()
        self.plugin = plugin

        self.setWindowTitle("Disorientation Interventions")
        self.setMinimumWidth(1100)
        self.setMinimumHeight(600)

        # Set the catalog for the instance of the UI to our predefined list
        self.catalog = INTERVENTION_CATALOG

        # Keep track of what is currently selected in the dialog
        self.current_category = None
        self.current_intervention = None

        # ==================================================
        # Main layout setup
        # ==================================================
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16,16,16,16)
        layout.setSpacing(12)

        title = QLabel("Disorientation Interventions")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Prototype controls for creative workflow interventions")
        subtitle.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(subtitle)

        # ==================================================
        # Three-pane layout construction
        # ==================================================

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # --- Left pane: framework categories ---

        self.category_group = QGroupBox("Framework Categories")
        self.category_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        category_layout = QVBoxLayout()

        self.category_list = QListWidget()
        self.category_list.addItems(self.catalog.keys())
        category_layout.addWidget(self.category_list)

        self.category_group.setLayout(category_layout)
        body_layout.addWidget(self.category_group, 2)

        # --- Middle pane: interventions in selected category ---

        self.intervention_group = QGroupBox("Interventions")
        self.intervention_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        intervention_layout = QVBoxLayout()

        self.intervention_list = QListWidget()
        intervention_layout.addWidget(self.intervention_list)

        self.intervention_group.setLayout(intervention_layout)
        body_layout.addWidget(self.intervention_group, 2)

        # --- Right pane: selected intervention details ---

        self.detail_group = QGroupBox("Details")
        self.detail_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(10)

        self.detail_title = QLabel("Select an intervention")
        self.detail_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        detail_layout.addWidget(self.detail_title)

        self.detail_description = QLabel("Choose a framework category, then choose an intervention to view its details.")
        self.detail_description.setWordWrap(True)
        self.detail_description.setStyleSheet("color: gray; font-size: 11px;")
        detail_layout.addWidget(self.detail_description)


        # ==================================================
        # Detail pane controls (dynamic intervention UI)
        # ==================================================
        # Checkbox control for toggle-based interventions
        self.detail_checkbox = QCheckBox("")
        self.detail_checkbox.hide()
        detail_layout.addWidget(self.detail_checkbox)

        # Button control for action-based interventions
        self.detail_button = QPushButton("")
        self.detail_button.setStyleSheet("padding: 6px;")
        self.detail_button.hide()
        detail_layout.addWidget(self.detail_button)

        # Status label for current intervention
        self.detail_status = QLabel("")
        self.detail_status.setStyleSheet("color: gray; font-size: 11px;")
        detail_layout.addWidget(self.detail_status)

        # Push controls upward a bit
        detail_layout.addStretch()

        self.detail_group.setLayout(detail_layout)
        body_layout.addWidget(self.detail_group, 3)

        # Add 3-pane body to main layout
        layout.addLayout(body_layout)
        self.setLayout(layout)

        # ==================================================
        # Signal wiring
        # ==================================================

        # Left pane selection updates middle pane
        self.category_list.currentTextChanged.connect(self.on_category_changed)

        # Middle pane selection updates right pane
        self.intervention_list.currentTextChanged.connect(self.on_intervention_changed)

        # Checkbox in right pane updates plugin state
        self.detail_checkbox.stateChanged.connect(self.on_detail_checkbox_changed)

        # Initialize first category selection
        self.category_list.setCurrentRow(0)

    # ==================================================
    # Category/intervention selection logic
    # ==================================================
    def on_category_changed(self, category_name):
        # Update current category
        self.current_category = category_name

        # Clear and repopulate intervention list
        self.intervention_list.clear()

        if not category_name:
            return

        interventions = self.catalog.get(category_name, [])
        for intervention in interventions:
            self.intervention_list.addItem(intervention["title"])

        # Auto-select first intervention in category
        if interventions:
            self.intervention_list.setCurrentRow(0)
        else:
            self.clear_detail_pane()

    def on_intervention_changed(self, intervention_title):
        if not self.current_category or not intervention_title:
            self.clear_detail_pane()
            return

        # Find intervention metadata in current category
        interventions = self.catalog.get(self.current_category, [])
        selected = None
        for intervention in interventions:
            if intervention["title"] == intervention_title:
                selected = intervention
                break

        if selected is None:
            self.clear_detail_pane()
            return

        self.current_intervention = selected

        # Update detail text
        self.detail_title.setText(selected["title"])
        self.detail_description.setText(selected["description"])
        self.detail_status.setText("")

        # Hide both controls first, then show only the relevant one
        self.detail_checkbox.hide()
        self.detail_button.hide()

        # Remove any previous button callback before attaching a new one
        try:
            self.detail_button.clicked.disconnect()
        except TypeError:
            pass

        # Show checkbox for toggle-based interventions
        if selected["control"] == "checkbox":
            self.detail_checkbox.setText(selected["label"])

            # Sync checkbox with stored plugin state
            if selected["key"] == "mark_fading":
                self.detail_checkbox.blockSignals(True)
                self.detail_checkbox.setChecked(self.plugin.mark_fading_enabled)
                self.detail_checkbox.blockSignals(False)

                if self.plugin.mark_fading_enabled:
                    self.detail_status.setText("Currently enabled")
                else:
                    self.detail_status.setText("Currently disabled")

            self.detail_checkbox.show()

        # Show button for action-based interventions
        elif selected["control"] == "button":
            self.detail_button.setText(selected["label"])
            self.detail_button.clicked.connect(self.run_selected_button_intervention)
            self.detail_button.show()

    # ==================================================
    # Detail-pane reset logic
    # ==================================================
    def clear_detail_pane(self):
        self.current_intervention = None
        self.detail_title.setText("Select an intervention")
        self.detail_description.setText("Choose a framework category, then choose an intervention to view its details.")
        self.detail_status.setText("")
        self.detail_checkbox.hide()
        self.detail_button.hide()

    # ==================================================
    # Detail-pane control logic
    # ==================================================
    def on_detail_checkbox_changed(self):
        if not self.current_intervention:
            return

        # Persist Mark Fading state on plugin
        if self.current_intervention["key"] == "mark_fading":
            self.plugin.mark_fading_enabled = self.detail_checkbox.isChecked()

            if self.plugin.mark_fading_enabled:
                self.detail_status.setText("Currently enabled")
            else:
                self.detail_status.setText("Currently disabled")

    def run_selected_button_intervention(self):
        if not self.current_intervention:
            return

        # For now, all button-based interventions use the existing test function
        test_intervention()