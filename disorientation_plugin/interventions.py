# Logic for creative interventions will go here.

from krita import *
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from pathlib import Path

def test_intervention():
    QMessageBox.information(
        None,
        "Intervention",
        "Test intervention triggered!"
    )

def canvas_toss():
    app = Krita.instance()
    doc = app.activeDocument()

    if doc is None:
        QMessageBox.information(None, "Canvas Toss", "No active document to toss")
        return

    backup_dir = Path.home() / "KritaCanvasTossBackups"
    backup_dir.mkdir(exist_ok=True)

    # Create a timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"canvas_toss_backup_{timestamp}.kra"

    # Export/save a backup copy before tossing
    success = doc.saveAs(str(backup_path))  # ADDED: safer first version

    if not success:
        QMessageBox.warning(None, "Canvas Toss", "Could not save backup before tossing canvas.")
        return

    # Create a fresh blank document using the same size/resolution as the old one
    new_doc = app.createDocument(
        doc.width(),
        doc.height(),
        "Canvas Toss",
        "RGBA",
        "U8",
        "",
        doc.xRes()
    )

    # Show the new document in the current window
    window = app.activeWindow()
    if window is not None:
        window.addView(new_doc)

    # Close the old document after the new one is open
    doc.close()

    # Tell the user where the backup went
    QMessageBox.information(
        None,
        "Canvas Toss",
        f"Old canvas saved to:\n{backup_path}\n\nA new blank canvas has been opened."
    )

# Registry mapping intervention keys to executable functions
INTERVENTION_FUNCTIONS = {
    "test_intervention": test_intervention,
    "canvas_toss": canvas_toss
}