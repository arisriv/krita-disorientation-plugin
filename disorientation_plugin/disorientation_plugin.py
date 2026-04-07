# Main entry point for the Krita plugin.

from krita import *
from PyQt5.QtWidgets import QMessageBox
from .ui import DisorientationUI

class DisorientationPlugin(Extension):
    def __init__(self):
        super().__init__()
        self.mark_fading_enabled = False
        self.canvas_toss_enabled = False

    def setup(self):
        pass
    
    def createActions(self, window):
        action = window.createAction(
            "disorientation_plugin_test",
            "Disorientation Plugin Test",
            "tools/scripts"
        )
        action.triggered.connect(self.say_hello)

    def say_hello(self):
        from PyQt5.QtWidgets import QApplication, QMainWindow  # ADDED
        qwin = None                                             # ADDED
        for widget in QApplication.topLevelWidgets():          # ADDED
            if isinstance(widget, QMainWindow):                # ADDED
                qwin = widget                                  # ADDED
                break                                          # ADDED
        self.panel = DisorientationUI(self, parent=qwin)       # CHANGED
        self.panel.show()
    
    # ==================================================================
    # TO BUILD: TIMER-BASED PROBABILISTIC TRIGGER FOR INTERVENTIONS
    # ==================================================================

Krita.instance().addExtension(
    DisorientationPlugin(Krita.instance())
)