# Main entry point for the Krita plugin.

from krita import *
from PyQt5.QtWidgets import QMessageBox
from .ui import DisorientationUI

class DisorientationPlugin(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.mark_fading_enabled = False

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
        self.panel = DisorientationUI(self)
        self.panel.show()

Krita.instance().addExtension(
    DisorientationPlugin(Krita.instance())
)