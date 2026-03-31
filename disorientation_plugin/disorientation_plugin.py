# Main entry point for the Krita plugin.

from krita import *
from PyQt5.QtWidgets import QMessageBox

class DisorientationPlugin(Extension):
    def __init__(self, parent):
        super().__init__(parent)

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
        QMessageBox.information(None, "Plugin", "Plugin is working!")

Krita.instance().addExtension(
    DisorientationPlugin(Krita.instance())
)