# Logic for creative interventions will go here.

from krita import *
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from pathlib import Path
import random
from .dialogs import CountdownDialog

# Keep references to open dialogs so they do not get garbage-collected
# immediately after being shown.
active_dialogs = []

def test_intervention():
    QMessageBox.information(
        None,
        "Intervention",
        "Test intervention triggered!"
    )

# =====================================================================
# PERMANENCE + REVISION INTERVENTIONS
# =====================================================================

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

# =====================================================================
# ARTISTIC MILIEU INTERVENTIONS
# =====================================================================

def perception_reframe():
    prompts = [
        "Imagine this artwork will be viewed from twenty feet away.",
        "Imagine this artwork will appear briefly in a fast-scrolling social media feed.",
        "Imagine this artwork will be printed very small in a book.",
        "Imagine this artwork will be scaled into a large mural.",
        "Imagine this artwork will hang in the corner of a gallery."
        #TKTKTK Add more for variance?
    ]

    prompt = random.choice(prompts)

    QMessageBox.information(
        None,
        "Placement / Perception Reframing",
        f"{prompt}\n\nMake at least one change to your artwork based on this new viewing context."
    )

# =====================================================================
# SOMAESTHETICS + PHYSICAL ENVIRONMENT INTERVENTIONS
# =====================================================================

def body_reorientation():
    prompts = [
        ("Rotate your tablet or device 90° and continue drawing.", 120),
        ("Stand while drawing for the next minute.", 60),
        ("Use your non-dominant hand for the next minute.", 60),
        ("Lean back and observe the composition for 30 seconds before continuing.", 30),
        ("Move farther from the canvas and make broader strokes for two minutes.", 120)
    ]

    # Randomly choose one prompt-duration pair.
    prompt, duration = random.choice(prompts)

    # Create the combined prompt + timer dialog.
    dialog = CountdownDialog(
        "Body Reorientation",
        prompt,
        duration
    )

    # Store the dialog so it stays open after this function ends.
    active_dialogs.append(dialog)

    # Show the dialog without blocking Krita, so the user can keep drawing
    # while the timer runs.
    dialog.show()


def memory_reflection():
    # TO ADD FUNCTIONALITY FOR BLOCKING EDITS WHILE TIMER
    prompts = [
        ("Think of a place you lived as a child. Sit with that memory before returning to the canvas.", 45),
        ("Think of the last place where you felt calm. Reflect on it before returning to the canvas.", 45),
        ("Think of a person who shaped how you see the world. Hold them in mind before returning to the canvas.", 60),
        ("Think of a conversation that stayed with you longer than you expected. Reflect on it before returning to the canvas.", 45),
        ("Think of a moment when you felt unexpectedly proud of something small. Sit with that memory before returning to the canvas.", 45),
        ("Think of the first memory that comes to mind from this morning. Reflect on it before returning to the canvas.", 30),
        ("Think of a moment where something ordinary suddenly felt strange or unfamiliar. Sit with that memory before returning to the canvas.", 45),
        ("Think of a moment when time seemed to slow down. Reflect on it before returning to the canvas.", 60),
        ("Think of a vivid sensory memory — a smell, sound, or texture you remember clearly. Sit with that memory before returning to the canvas.", 45),
        ("Think of a memory tied to a particular object you once owned. Reflect on it before returning to the canvas.", 45),
        ("Think of a moment when you changed your mind about something important. Sit with that memory before returning to the canvas.", 60),
        ("Think of a memory that feels distant but still emotionally vivid. Reflect on it before returning to the canvas.", 60),
        ("Think of a place you returned to after a long time away. Sit with that memory before returning to the canvas.", 45),
        ("Think of a moment where you noticed something others seemed to overlook. Reflect on it before returning to the canvas.", 45),
    ]

    prompt, duration = random.choice(prompts)

    dialog = CountdownDialog(
        "Memory-Based Reflection",
        prompt,
        duration
    )

    # Keep a reference so the dialog stays alive after this function ends
    active_dialogs.append(dialog)
    dialog.show()

# Registry mapping intervention keys to executable functions
INTERVENTION_FUNCTIONS = {
    "test_intervention": test_intervention,
    "canvas_toss": canvas_toss,
    "scenius_prompt": test_intervention,
    "posture_check": test_intervention,
    "perception_reframe": perception_reframe,
    "creation_interval": test_intervention,
    "body_reorientation": body_reorientation,
    "memory_reflection": memory_reflection
}