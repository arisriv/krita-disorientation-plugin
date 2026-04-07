# Logic for creative interventions will go here.

from krita import *
from PyQt5.QtWidgets import QMessageBox, QAction
from PyQt5.QtCore import QTimer
from datetime import datetime
from pathlib import Path
import random
from .dialogs import CountdownDialog

# Keep references to open dialogs so they do not get garbage-collected
# immediately after being shown.
active_dialogs = []

def _get_main_window():
    from PyQt5.QtWidgets import QApplication, QMainWindow  # ADDED
    for widget in QApplication.topLevelWidgets():          # ADDED
        if isinstance(widget, QMainWindow):                # ADDED
            return widget                                  # ADDED
    return None                                            # ADDED

def test_intervention(panel=None):
    QMessageBox.information(
        None,
        "Intervention",
        "Test intervention triggered!"
    )

def _create_canvas_overlay():
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    from PyQt5.QtCore import Qt

    # Find the main Krita window
    qwin = _get_main_window()
    if qwin is None:
        return None

    # Find the canvas viewport widget by name
    view = qwin.findChild(QWidget, "view_0")
    if view is None:
        return None

    # Create a frameless overlay widget parented to the canvas viewport.
    # Parenting to view_0 means it moves with the canvas and closes with Krita.
    overlay = QWidget(view)                                        # ADDED
    overlay.setWindowFlags(Qt.FramelessWindowHint)                 # ADDED

    # Semi-transparent dark tint — rgba(0, 0, 0, 120) is visible but
    # still lets the artwork show through underneath
    overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);") # ADDED

    # Match the canvas viewport exactly
    overlay.setGeometry(view.rect())                               # ADDED

    # Raise it above the canvas so it intercepts mouse events
    overlay.raise_()                                               # ADDED
    overlay.show()                                                 # ADDED

    return overlay                                                 # ADDED


def _remove_canvas_overlay(overlay):
    if overlay is not None:
        overlay.hide()    # ADDED
        overlay.deleteLater()  # ADDED


def diagnose_actions(panel=None):
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    output_path = Path.home() / "krita_actions_diagnostic.txt"
    with open(output_path, "w") as f:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                view = widget.findChild(QWidget, "view_0")
                f.write(f"view_0 found: {view is not None}\n")
                if view is not None:
                    f.write(f"view_0 geometry: {view.geometry()}\n")
                    f.write(f"view_0 isVisible: {view.isVisible()}\n")
    QMessageBox.information(None, "Diagnose", f"Written to:\n{output_path}")

def test_overlay(panel=None):
    overlay = _create_canvas_overlay()

    if overlay is None:
        QMessageBox.warning(None, "Test Overlay", "Could not create overlay.")
        return

    QTimer.singleShot(10000, lambda: _remove_canvas_overlay(overlay))

# =====================================================================
# PROCESS + TEMPORALITY INTERVENTIONS
# =====================================================================

# BRUSH RESTRICTION INTERVENTION
def brush_restriction(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Brush Restriction", "No active Krita window.")
        return

    view = window.activeView()

    if view is None:
        QMessageBox.warning(None, "Brush Restriction", "No active view.")
        return

    # Store the current preset as the one to ban for the duration
    banned_preset = view.currentBrushPreset()

    if banned_preset is None:
        QMessageBox.warning(None, "Brush Restriction", "Could not read current brush preset.")
        return

    banned_name = banned_preset.name()

    # Get all available presets as a dictionary of {name: resource}
    all_presets = app.resources("preset")

    # Filter out presets with names too similar to the banned one.
    # We split both names into words and exclude any preset that shares
    # a word with the banned preset name, case-insensitive.
    banned_words = set(banned_name.lower().split())

    candidates = []
    for name, preset in all_presets.items():
        preset_words = set(name.lower().split())
        # If no words overlap, this preset is dissimilar enough to use
        if not banned_words.intersection(preset_words):
            candidates.append(preset)

    if not candidates:
        QMessageBox.warning(None, "Brush Restriction", "Could not find a dissimilar brush preset.")
        return

    # Pick one disorienting preset randomly and keep it fixed for the duration
    disorienting_preset = random.choice(candidates)

    # Switch the user to the disorienting preset immediately
    view.setCurrentBrushPreset(disorienting_preset)

    # QUESTION: is this long enough? too long? too short?
    duration = random.randint(240,420)

    # Set up a poll timer that checks every 300ms whether the user has
    # switched back to the banned preset, and bounces them away if so
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    # Use a mutable container so the lambda can reference the timer
    # and view without relying on closure-captured variables changing
    state = {
        "banned_name": banned_name,
        "disorienting_preset": disorienting_preset,
        "view": view,
    }

    def poll():
        current = state["view"].currentBrushPreset()
        if current is not None and current.name() == state["banned_name"]:
            # User switched back to the banned preset — bounce them away
            state["view"].setCurrentBrushPreset(state["disorienting_preset"])

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    # Show the countdown dialog for the duration
    dialog = CountdownDialog(
        "Brush Restriction",
        f"Your brush has been temporarily restricted.\nFind another way forward.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    # After the duration, stop polling and restore the original preset
    QTimer.singleShot(
        duration * 1000,
        lambda: _restore_brush(poll_timer, view, banned_preset, dialog)
    )


def _restore_brush(poll_timer, view, original_preset, dialog):
    # Stop the poll timer so we stop intercepting preset changes
    poll_timer.stop()

    # Restore the user's original preset
    view.setCurrentBrushPreset(original_preset)

    # Clean up the dialog reference
    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    QMessageBox.information(
        None,
        "Brush Restriction Lifted",
        "Your original brush has been restored."
    )


# SUBTRACTIVE DRAWING INTERVENTION
def subtractive_drawing(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Subtractive Drawing", "No active Krita window.")
        return

    view = window.activeView()

    if view is None:
        QMessageBox.warning(None, "Subtractive Drawing", "No active view.")
        return

    # Store the user's current preset so we can restore it after
    original_preset = view.currentBrushPreset()

    if original_preset is None:
        QMessageBox.warning(None, "Subtractive Drawing", "Could not read current brush preset.")
        return

    # Find all eraser presets by filtering for "erase" in the name
    all_presets = app.resources("preset")
    eraser_presets = [
        preset for name, preset in all_presets.items()
        if "erase" in name.lower()
    ]

    if not eraser_presets:
        QMessageBox.warning(None, "Subtractive Drawing", "No eraser presets found.")
        return

    # Pick one eraser preset randomly and keep it fixed for the duration
    eraser_preset = random.choice(eraser_presets)

    # Switch to freehand brush tool and eraser preset immediately
    brush_action = app.action("KritaShape/KisToolBrush")
    if brush_action is None:
        QMessageBox.warning(None, "Subtractive Drawing", "Could not find freehand brush action.")
        return

    brush_action.trigger()
    view.setCurrentBrushPreset(eraser_preset)
    view.setEraserMode(True)

    eraser_preset_name = eraser_preset.name()
    original_preset_name = original_preset.name()

    duration = random.randint(240, 420)

    # Poll every 300ms — unconditionally enforce brush tool, eraser preset,
    # and eraser mode so the user cannot escape to any other tool or preset
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    state = {
        "view": view,
        "brush_action": brush_action,
        "eraser_preset": eraser_preset,
        "eraser_preset_name": eraser_preset_name,
        "original_preset_name": original_preset_name,
    }

    def poll():
        # Always force back to freehand brush tool
        state["brush_action"].trigger()

        # If user switched to a non-eraser preset, force back to the eraser preset.
        # Allow switching freely between eraser presets.
        current = state["view"].currentBrushPreset()
        if current is not None and "erase" not in current.name().lower():  # CHANGED
            state["view"].setCurrentBrushPreset(state["eraser_preset"])

        # Always force eraser mode on since we can't reliably read its state
        state["view"].setEraserMode(True)

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    dialog = CountdownDialog(
        "Subtractive Drawing",
        "You are in eraser-only mode.\nFind another way forward.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    QTimer.singleShot(
        duration * 1000,
        lambda: _restore_subtractive(poll_timer, view, original_preset, dialog)
    )


def _restore_subtractive(poll_timer, view, original_preset, dialog):
    # Stop polling
    poll_timer.stop()

    # Restore original preset and turn eraser mode off
    view.setCurrentBrushPreset(original_preset)
    view.setEraserMode(False)

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    QMessageBox.information(
        None,
        "Subtractive Drawing Lifted",
        "Your original brush has been restored."
    )

# CANVAS TRANSFORMATION INTERVENTION
def canvas_transformation(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Canvas Transformation", "No active Krita window.")
        return

    view = window.activeView()

    if view is None:
        QMessageBox.warning(None, "Canvas Transformation", "No active view.")
        return

    canvas = view.canvas()

    # Store original state so we can restore exactly after the timer
    original_mirror = canvas.mirror()
    original_rotation = canvas.rotation()

    # Weighted random choice between three transformation types:
    # 25% mirror only, 25% rotation only, 50% both
    transformation = random.choices(
        ["mirror", "rotation", "both"],
        weights=[25, 25, 50]
    )[0]

    # Pick a random angle between 35 and 145 degrees, excluding the range
    # 80-100 degrees to avoid near-90 which feels too orderly, and we also
    # pick from both positive and negative to get left and right tilts
    angle_pool = list(range(35, 80)) + list(range(100, 145))
    angle = random.choice(angle_pool)

    # Randomly apply positive or negative rotation for more variance
    if random.random() < 0.5:
        angle = -angle

    # Apply the chosen transformation
    if transformation == "mirror":
        canvas.setMirror(not original_mirror)  # ADDED: flip mirror state
    elif transformation == "rotation":
        canvas.setRotation(angle)              # ADDED: apply rotation
    elif transformation == "both":
        canvas.setMirror(not original_mirror)  # ADDED
        canvas.setRotation(angle)              # ADDED

    duration = random.randint(180, 300)

    dialog = CountdownDialog(
        "Canvas Transformation",
        "Your canvas has been transformed.\nFind another way forward.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    QTimer.singleShot(
        duration * 1000,
        lambda: _restore_canvas_transformation(
            canvas, original_mirror, original_rotation, dialog
        )
    )


def _restore_canvas_transformation(canvas, original_mirror, original_rotation, dialog):
    # Restore canvas to exactly its pre-intervention state
    canvas.setMirror(original_mirror)
    canvas.setRotation(original_rotation)

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Canvas Transformation Lifted",
        "Your canvas has been restored."
    )


# TOOL RESTRICTION INTERVENTION: to revisit, not working as intended
def tool_restriction(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Tool Restriction", "No active Krita window.")
        return

    view = window.activeView()

    if view is None:
        QMessageBox.warning(None, "Tool Restriction", "No active view.")
        return

    # All confirmed-found tool action IDs except the freehand brush,
    # which is our neutral redirect target and should never be restricted
    candidates = [
        ("Fill Tool",        "KritaFill/KisToolFill"),
        ("Color Picker",     "KritaSelected/KisToolColorSampler"),
        ("Crop Tool",        "KisToolCrop"),
        ("Line Tool",        "KritaShape/KisToolLine"),
        ("Rectangle Tool",   "KritaShape/KisToolRectangle"),
        ("Move Tool",        "KritaTransform/KisToolMove"),
        ("Multibrush Tool",  "KritaShape/KisToolMultiBrush"),
    ]

    # Pick one tool to restrict at random
    tool_name, action_id = random.choice(candidates)

    # Get the action for the restricted tool and the freehand brush redirect
    banned_action = app.action(action_id)
    brush_action = app.action("KritaShape/KisToolBrush")

    if banned_action is None or brush_action is None:
        QMessageBox.warning(
            None,
            "Tool Restriction",
            "Could not locate required actions. Restriction skipped."
        )
        return

    # Trigger the freehand brush immediately as the starting redirect
    brush_action.trigger()

    duration = random.randint(240, 420)

    # Poll every 300ms — if the banned tool's action gets triggered,
    # immediately redirect back to the freehand brush
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    def poll():
        # isChecked() didn't work, so instead we re-trigger the brush tool
        # preemptively on every poll to keep pulling the user back.
        # This is a blunt approach but reliable given API limitations.
        pass

    # Since we can't detect current tool state, we use triggered signal
    # on the banned action to intercept and redirect
    def on_banned_triggered():
        # User triggered the restricted tool — bounce them back immediately
        brush_action.trigger()

    banned_action.triggered.connect(on_banned_triggered)  # ADDED

    dialog = CountdownDialog(
        "Tool Restriction",
        f"The {tool_name} has been temporarily restricted.\nFind another way forward.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    QTimer.singleShot(
        duration * 1000,
        lambda: _restore_tool(banned_action, brush_action, on_banned_triggered, dialog)
    )


def _restore_tool(banned_action, brush_action, on_banned_triggered, dialog):
    # Disconnect the intercept signal so the tool works normally again
    try:
        banned_action.triggered.disconnect(on_banned_triggered)  # ADDED
    except TypeError:
        pass

    # Clean up dialog reference
    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    QMessageBox.information(
        None,
        "Tool Restriction Lifted",
        "The restricted tool is now available again."
    )


def creation_interval(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Creation Interval", "No active Krita window.")
        return

    doc = app.activeDocument()
    if doc is None:
        QMessageBox.warning(None, "Creation Interval", "No active document.")
        return

    prompts = [
        "Step away from your work.\nLook at something far away for a moment.\nReturn when the timer expires.",
        "Put down your stylus.\nWalk away from your screen.\nReturn when the timer expires.",
        "Close your eyes and breathe.\nLet your mind wander away from the canvas.\nReturn when the timer expires.",
        "Stand up and stretch.\nDon't think about your work.\nReturn when the timer expires.",
        "Look away from all screens.\nGive your eyes and mind a rest.\nReturn when the timer expires.",
    ]

    prompt = random.choice(prompts)
    duration = random.randint(15, 30)

    # Block the canvas with an overlay
    overlay = _create_canvas_overlay()  # ADDED

    dialog = CountdownDialog(
        "Creation Interval",
        prompt,
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_creation_interval(overlay, dialog)
    )  # ADDED


def _restore_creation_interval(overlay, dialog):
    # Remove the canvas overlay so the user can paint again
    _remove_canvas_overlay(overlay)  # ADDED

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Creation Interval",
        "Your creation interval has ended.\nReturn to your work."
    )

# =====================================================================
# PERMANENCE + REVISION INTERVENTIONS
# =====================================================================

def canvas_toss(panel=None):
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

def perception_reframe(panel=None):
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

def body_reorientation(panel=None):
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
        duration,
        parent=_get_main_window()
    )

    # Store the dialog so it stays open after this function ends.
    active_dialogs.append(dialog)

    # Show the dialog without blocking Krita, so the user can keep drawing
    # while the timer runs.
    dialog.show()


def memory_reflection(panel=None):
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
        duration,
        parent=_get_main_window()
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
    "creation_interval": creation_interval,
    "body_reorientation": body_reorientation,
    "memory_reflection": memory_reflection,
    "brush_restriction": brush_restriction,
    "diagnose_actions": diagnose_actions,
    "tool_restriction": tool_restriction,
    "subtractive_drawing": subtractive_drawing,
    "canvas_transformation": canvas_transformation,
    "test_overlay": test_overlay
}