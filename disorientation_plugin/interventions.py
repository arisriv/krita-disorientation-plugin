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

# Helper to block canvas through an overlaid window
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
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt

    qwin = _get_main_window()
    if qwin is None:
        return

    view = qwin.findChild(QWidget, "view_0")
    if view is None:
        return

    # White semi-transparent overlay — simulates brightness increase
    overlay = QWidget(view)
    overlay.setStyleSheet("background-color: rgba(255, 255, 255, 80);")
    overlay.setGeometry(view.rect())
    overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
    overlay.raise_()
    overlay.show()

    # Remove after 10 seconds so you can paint during that time
    QTimer.singleShot(10000, lambda: overlay.deleteLater())

    QMessageBox.information(None, "Diagnose", "Overlay active for 10 seconds — click OK then paint.")

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


# TOOL RESTRICTION INTERVENTION
def tool_restriction(panel=None):
    from PyQt5.QtWidgets import QToolButton

    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Tool Restriction", "No active Krita window.")
        return

    qwin = _get_main_window()
    if qwin is None:
        QMessageBox.warning(None, "Tool Restriction", "No main window found.")
        return

    # Tool categories — each is a display name and list of tool IDs
    categories = [
        (
            "Fill Tools",
            ["KritaFill/KisToolFill", "KritaSelected/KisToolColorSampler", "KritaFill/KisToolGradient"]
        ),
        (
            "Transform Tools",
            ["KritaTransform/KisToolMove", "KisToolCrop"]
        ),
        (
            "Shape Tools",
            ["KritaShape/KisToolLine", "KritaShape/KisToolRectangle", "KritaShape/KisToolMultiBrush"]
        ),
        (
            "All Tools",
            [
                "KritaFill/KisToolFill", "KritaSelected/KisToolColorSampler", "KritaFill/KisToolGradient",
                "KritaTransform/KisToolMove", "KisToolCrop",
                "KritaShape/KisToolLine", "KritaShape/KisToolRectangle", "KritaShape/KisToolMultiBrush"
            ]
        ),
    ]

    # Weighted random selection — All Tools is rarest at 10%
    category_name, tool_ids = random.choices(
        categories,
        weights=[30, 30, 30, 10]
    )[0]

    # Switch to freehand brush immediately
    brush_action = app.action("KritaShape/KisToolBrush")
    if brush_action is not None:
        brush_action.trigger()

    # Create an overlay for each tool in the selected category
    overlays = []
    for tool_id in tool_ids:
        tool_button = qwin.findChild(QToolButton, tool_id)
        if tool_button is None:
            continue
        parent_widget = tool_button.parent()
        overlay = QWidget(parent_widget)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        overlay.setGeometry(tool_button.geometry())
        overlay.raise_()
        overlay.show()
        overlays.append(overlay)

    if not overlays:
        QMessageBox.warning(None, "Tool Restriction", "Could not find any tool buttons.")
        return

    duration = random.randint(240, 420)

    dialog = CountdownDialog(
        "Tool Restriction",
        f"Your {category_name} have been temporarily restricted.\nFind another way forward.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_tool_restriction(overlays, dialog)
    )


def _restore_tool_restriction(overlays, dialog):
    # Remove all tool overlays
    for overlay in overlays:
        overlay.deleteLater()

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Tool Restriction Lifted",
        "Your tools are now available again."
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

# To figure out: block ctrl+Z
def undo_restriction(panel=None):
    from PyQt5.QtWidgets import QWidget

    qwin = _get_main_window()
    if qwin is None:
        QMessageBox.warning(None, "Undo Restriction", "No main window found.")
        return

    toolbar = qwin.findChild(QWidget, "editToolBar")
    if toolbar is None:
        QMessageBox.warning(None, "Undo Restriction", "Could not find edit toolbar.")
        return

    # Create overlay over the toolbar to block undo/redo button clicks
    overlay = QWidget(toolbar)
    overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
    overlay.setGeometry(toolbar.rect())
    overlay.raise_()
    overlay.show()

    duration = random.randint(120, 180)

    dialog = CountdownDialog(
        "Undo Restriction",
        "Undo and redo are temporarily restricted.\nCommit to your marks.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_undo_restriction(overlay, dialog)
    )

def _restore_undo_restriction(overlay, dialog):
    overlay.deleteLater()

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Undo Restriction Lifted",
        "Undo and redo are available again."
    )

# MARK FADING INTERVENTION
def mark_fading(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Mark Fading", "No active Krita window.")
        return

    view = window.activeView()
    if view is None:
        QMessageBox.warning(None, "Mark Fading", "No active view.")
        return

    doc = app.activeDocument()
    if doc is None:
        QMessageBox.warning(None, "Mark Fading", "No active document.")
        return

    original_node = doc.activeNode()
    if original_node is None:
        QMessageBox.warning(None, "Mark Fading", "No active layer found.")
        return

    # Create a new paint layer above the current one
    fading_layer = doc.createNode("Mark Fading", "paintlayer")
    root = doc.rootNode()
    root.addChildNode(fading_layer, original_node)

    # Set the new layer as active so the user paints on it
    doc.setActiveNode(fading_layer)
    doc.refreshProjection()

    # Random duration 4-7 mins
    duration = random.randint(240, 420)

    # Target opacity is random between 0 and 49 out of 255
    target_opacity = int(random.randint(0, 49) * 255 / 100)

    # Poll every 300ms to keep the fading layer active
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    state = {
        "doc": doc,
        "fading_layer": fading_layer,
    }

    def poll():
        # Only job during painting: keep fading layer active
        if state["doc"].activeNode() != state["fading_layer"]:
            state["doc"].setActiveNode(state["fading_layer"])

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    dialog = CountdownDialog(
        "Mark Fading",
        "Continue working on your canvas.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _begin_mark_fade(poll_timer, doc, fading_layer, dialog, target_opacity)
    )

def _begin_mark_fade(poll_timer, doc, fading_layer, dialog, target_opacity):
    poll_timer.stop()

    # Block canvas during fade so user can't paint while opacity is changing
    fade_overlay = _create_canvas_overlay()  # ADDED

    # Fade from 255 to target_opacity over 2 seconds
    # 10 steps at 200ms each = 2 seconds total
    fade_steps = 10
    step_size = (255 - target_opacity) / fade_steps
    state = {"steps_done": 0}

    fade_timer = QTimer()
    fade_timer.setInterval(200)  # CHANGED: 200ms per step

    def fade_step():
        state["steps_done"] += 1
        current_opacity = max(
            int(255 - step_size * state["steps_done"]),
            target_opacity
        )
        fading_layer.setOpacity(current_opacity)
        doc.refreshProjection()

        if state["steps_done"] >= fade_steps:
            fade_timer.stop()
            _restore_mark_fading(doc, fading_layer, dialog, fade_overlay)  # CHANGED

    fade_timer.timeout.connect(fade_step)
    fade_timer.start()


def _restore_mark_fading(doc, fading_layer, dialog, fade_overlay=None):
    fading_layer.mergeDown()
    doc.refreshProjection()

    # Remove the fade overlay now that merge is done
    _remove_canvas_overlay(fade_overlay)  # ADDED

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Mark Fading Complete",
        "Your faded marks have been merged into the canvas."
    )

# ANALOG REVISION INTERVENTION
def analog_revision(panel=None):
    from PyQt5.QtCore import QObject, QEvent
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtWidgets import QApplication, QWidget

    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Analog Revision", "No active Krita window.")
        return

    view = window.activeView()
    if view is None:
        QMessageBox.warning(None, "Analog Revision", "No active view.")
        return

    qwin = _get_main_window()
    if qwin is None:
        QMessageBox.warning(None, "Analog Revision", "No main window found.")
        return

    # Store original preset so we can bounce back to it if user switches to eraser
    original_preset = view.currentBrushPreset()

    # --- Block Ctrl+Z via ShortcutOverride ---
    class UndoBlocker(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.ShortcutOverride or event.type() == QEvent.KeyPress:
                seq_int = int(event.modifiers()) | event.key()
                seq = QKeySequence(seq_int)
                undo_action = Krita.instance().action("edit_undo")
                if undo_action and seq == undo_action.shortcuts()[0]:
                    event.accept()
                    return True
            return super().eventFilter(obj, event)

    blocker = UndoBlocker(QApplication.instance())
    QApplication.instance().installEventFilter(blocker)

    # --- Cover undo/redo toolbar buttons ---
    toolbar = qwin.findChild(QWidget, "editToolBar")
    toolbar_overlay = None
    if toolbar is not None:
        toolbar_overlay = QWidget(toolbar)
        toolbar_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
        toolbar_overlay.setGeometry(toolbar.rect())
        toolbar_overlay.raise_()
        toolbar_overlay.show()

    # --- Poll to block eraser mode and eraser presets ---
    brush_action = app.action("KritaShape/KisToolBrush")

    poll_timer = QTimer()
    poll_timer.setInterval(300)

    state = {
        "view": view,
        "brush_action": brush_action,
        "original_preset": original_preset,
    }

    def poll():
        # Unconditionally force eraser mode off and stay on brush tool
        state["view"].setEraserMode(False)
        if state["brush_action"] is not None:
            state["brush_action"].trigger()
        # If user switched to an eraser preset, bounce back to original
        current = state["view"].currentBrushPreset()
        if current is not None and "erase" in current.name().lower():
            state["view"].setCurrentBrushPreset(state["original_preset"])

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    duration = random.randint(180, 420)  # 3-7 minutes

    dialog = CountdownDialog(
        "Analog Revision",
        "Undo and erasing are temporarily restricted.\nCommit to your marks.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_analog_revision(blocker, toolbar_overlay, poll_timer, dialog)
    )


def _restore_analog_revision(blocker, toolbar_overlay, poll_timer, dialog):
    from PyQt5.QtWidgets import QApplication

    # Remove Ctrl+Z blocker
    QApplication.instance().removeEventFilter(blocker)

    # Remove toolbar overlay
    if toolbar_overlay is not None:
        toolbar_overlay.deleteLater()

    # Stop eraser poll
    poll_timer.stop()

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Analog Revision Lifted",
        "Undo and erasing are available again."
    )


# LOCKED MARKS INTERVENTION
def locked_marks(panel=None):
    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Locked Marks", "No active Krita window.")
        return

    view = window.activeView()
    if view is None:
        QMessageBox.warning(None, "Locked Marks", "No active view.")
        return

    doc = app.activeDocument()
    if doc is None:
        QMessageBox.warning(None, "Locked Marks", "No active document.")
        return

    original_node = doc.activeNode()
    if original_node is None:
        QMessageBox.warning(None, "Locked Marks", "No active layer found.")
        return

    # Create a new paint layer above the current one
    locked_layer = doc.createNode("Locked Marks", "paintlayer")
    root = doc.rootNode()
    root.addChildNode(locked_layer, original_node)

    # Set the new layer as active so the user paints on it
    doc.setActiveNode(locked_layer)
    doc.refreshProjection()

    duration = random.randint(15, 30)  # 4-7 minutes, 15 TO 30 FOR TESTING RN

    # Poll every 300ms to keep the locked marks layer active
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    state = {
        "doc": doc,
        "locked_layer": locked_layer,
    }

    def poll():
        if state["doc"].activeNode() != state["locked_layer"]:
            state["doc"].setActiveNode(state["locked_layer"])

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    dialog = CountdownDialog(
        "Locked Marks",
        "Paint on this layer.\nWhen the timer expires, your marks will be permanently locked.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_locked_marks(poll_timer, doc, locked_layer, original_node, dialog)
    )

def _restore_locked_marks(poll_timer, doc, locked_layer, original_node, dialog):
    poll_timer.stop()

    # Lock the layer permanently
    locked_layer.setLocked(True)
    doc.refreshProjection()

    # Create a new blank layer above the locked one so user can paint freely
    new_layer = doc.createNode("Paint Layer", "paintlayer")  # ADDED
    root = doc.rootNode()                                     # ADDED
    root.addChildNode(new_layer, locked_layer)                # ADDED: insert above locked layer
    doc.setActiveNode(new_layer)                              # ADDED: switch to new layer
    doc.refreshProjection()                                   # ADDED

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Marks Locked",
        "Your marks have been permanently locked.\nA new layer has been created above them."
    )


# UNDO/ERASE BANK INTERVENTION
def undo_erase_bank(panel=None):
    from PyQt5.QtCore import QObject, QEvent
    from PyQt5.QtGui import QKeySequence
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QDialog

    app = Krita.instance()
    window = app.activeWindow()

    if window is None:
        QMessageBox.warning(None, "Undo/Erase Bank", "No active Krita window.")
        return

    view = window.activeView()
    if view is None:
        QMessageBox.warning(None, "Undo/Erase Bank", "No active view.")
        return

    qwin = _get_main_window()
    if qwin is None:
        QMessageBox.warning(None, "Undo/Erase Bank", "No main window found.")
        return

    budget = random.randint(2, 4)
    duration = random.randint(15, 30)  # TESTING: change to randint(240, 420) for production

    original_preset = view.currentBrushPreset()

    # --- Counter dialog ---
    counter_dialog = QDialog(_get_main_window())
    counter_dialog.setWindowTitle("Actions Remaining")
    counter_dialog.setMinimumWidth(200)
    counter_layout = QVBoxLayout()
    counter_label = QLabel(f"{budget} undos/erases remaining")
    counter_label.setStyleSheet("font-size: 13px; padding: 8px;")
    counter_layout.addWidget(counter_label)
    counter_dialog.setLayout(counter_layout)
    counter_dialog.show()

    state = {
        "budget": budget,
        "locked": False,
        "last_was_eraser": False,
        "last_undo_handled": False,
        "half_count": 0,
        "view": view,
        "original_preset": original_preset,
        "toolbar_overlay": None,
    }

    def update_counter():
        if state["budget"] > 0:
            counter_label.setText(f"{state['budget']} undos/erases remaining")
            counter_label.setStyleSheet("font-size: 13px; padding: 8px;")
        else:
            counter_label.setText("No actions remaining")
            counter_label.setStyleSheet("font-size: 13px; padding: 8px; color: red;")
        counter_dialog.adjustSize()
        counter_dialog.update()

    def _do_decrement():
        state["budget"] -= 1
        update_counter()
        if state["budget"] <= 0:
            apply_full_restriction()

    def decrement_and_check():
        # For Ctrl+Z only — ShortcutOverride fires twice so only decrement every 2 calls
        if state["locked"]:
            return
        state["half_count"] += 1
        if state["half_count"] % 2 == 0:
            _do_decrement()

    def decrement_direct():
        # For toolbar button and eraser — fires once, decrement directly
        if state["locked"]:
            return
        _do_decrement()

    def apply_full_restriction():
        state["locked"] = True
        toolbar = qwin.findChild(QWidget, "editToolBar")
        if toolbar is not None:
            overlay = QWidget(toolbar)
            overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120);")
            overlay.setGeometry(toolbar.rect())
            overlay.raise_()
            overlay.show()
            state["toolbar_overlay"] = overlay

    # --- Undo interceptor ---
    class UndoInterceptor(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.ShortcutOverride:
                seq_int = int(event.modifiers()) | event.key()
                seq = QKeySequence(seq_int)
                undo_action = Krita.instance().action("edit_undo")
                if undo_action and seq == undo_action.shortcuts()[0]:
                    if state["locked"]:
                        event.accept()
                        return True
                    else:
                        if not state["last_undo_handled"]:
                            state["last_undo_handled"] = True
                            QTimer.singleShot(500, lambda: state.update({"last_undo_handled": False}))
                            decrement_and_check()
                        return False
            return super().eventFilter(obj, event)

    blocker = UndoInterceptor(QApplication.instance())
    QApplication.instance().installEventFilter(blocker)

    # --- Eraser poll ---
    poll_timer = QTimer()
    poll_timer.setInterval(300)

    def poll():
        current = state["view"].currentBrushPreset()
        if current is None:
            state["last_was_eraser"] = False
            return

        is_eraser = "erase" in current.name().lower()

        if is_eraser and not state["last_was_eraser"]:
            if state["locked"]:
                state["view"].setCurrentBrushPreset(state["original_preset"])
            else:
                decrement_direct()

        elif state["locked"] and is_eraser:
            state["view"].setCurrentBrushPreset(state["original_preset"])

        if state["locked"]:
            state["view"].setEraserMode(False)

        state["last_was_eraser"] = is_eraser

    poll_timer.timeout.connect(poll)
    poll_timer.start()

    # --- Countdown dialog ---
    dialog = CountdownDialog(
        "Undo/Erase Bank",
        f"You have {budget} undo/erase actions.\nUse them wisely.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    # Connect toolbar undo AFTER dialog is shown to avoid premature firing
    undo_action = app.action("edit_undo")
    def on_toolbar_undo():
        if not state["locked"]:
            decrement_direct()

    if undo_action:
        undo_action.triggered.connect(on_toolbar_undo)

    dialog.countdown_finished.connect(
        lambda: _restore_undo_erase_bank(
            blocker, poll_timer, counter_dialog,
            state, dialog, undo_action, on_toolbar_undo
        )
    )


def _restore_undo_erase_bank(blocker, poll_timer, counter_dialog, state, dialog, undo_action, on_toolbar_undo):
    from PyQt5.QtWidgets import QApplication

    QApplication.instance().removeEventFilter(blocker)

    if undo_action:
        try:
            undo_action.triggered.disconnect(on_toolbar_undo)
        except TypeError:
            pass

    poll_timer.stop()

    if state["toolbar_overlay"] is not None:
        state["toolbar_overlay"].deleteLater()

    counter_dialog.close()

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Undo/Erase Bank Complete",
        "Your undo and erase actions are fully restored."
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


# BRIGHTNESS SHIFT INTERVENTION
def brightness_shift(panel=None):
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt

    qwin = _get_main_window()
    if qwin is None:
        QMessageBox.warning(None, "Brightness Shift", "No main window found.")
        return

    view_widget = qwin.findChild(QWidget, "view_0")
    if view_widget is None:
        QMessageBox.warning(None, "Brightness Shift", "Could not find canvas.")
        return

    # Pick a random starting color (white = bright, black = dark)
    # and a random starting opacity between 20 and 80
    is_bright = random.choice([True, False])
    current_opacity = random.randint(20, 80)
    # Pick a random starting direction (increasing or decreasing opacity)
    direction = random.choice([1, -1])

    # Create the overlay — transparent to mouse events so user can still paint
    overlay = QWidget(view_widget)
    overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
    overlay.setGeometry(view_widget.rect())
    overlay.raise_()

    def update_overlay():
        color = "255, 255, 255" if is_bright else "0, 0, 0"
        overlay.setStyleSheet(f"background-color: rgba({color}, {current_opacity});")
        overlay.show()

    update_overlay()

    duration = random.randint(240, 420)  # 4-7 minutes

    # Shift timer — fires every 30-60 seconds
    shift_timer = QTimer()

    state = {
        "is_bright": is_bright,
        "current_opacity": current_opacity,
        "direction": direction,
    }

    def shift():
        # 75% chance to continue in same direction, 25% to reverse
        if random.random() < 0.25:
            state["direction"] *= -1

        # Apply shift
        state["current_opacity"] += state["direction"] * 20

        # Clamp and force direction reversal before hitting extremes
        if state["current_opacity"] >= 160:
            state["current_opacity"] = 160
            state["direction"] = -1
        elif state["current_opacity"] <= 20:
            state["current_opacity"] = 20
            state["direction"] = 1
            # At low end, randomly flip between bright and dark
            state["is_bright"] = random.choice([True, False])

        # Update overlay appearance
        color = "255, 255, 255" if state["is_bright"] else "0, 0, 0"
        overlay.setStyleSheet(
            f"background-color: rgba({color}, {state['current_opacity']});"
        )

    # Pick a random interval between 30 and 60 seconds for each shift
    def schedule_next_shift():
        interval = random.randint(30000, 60000)
        shift_timer.setInterval(interval)
        shift_timer.start()

    shift_timer.setSingleShot(True)
    shift_timer.timeout.connect(lambda: [shift(), schedule_next_shift()])
    schedule_next_shift()

    dialog = CountdownDialog(
        "Brightness Shift",
        "The light around your work is shifting.\nContinue painting.",
        duration,
        parent=_get_main_window()
    )

    active_dialogs.append(dialog)
    dialog.show()

    dialog.countdown_finished.connect(
        lambda: _restore_brightness_shift(shift_timer, overlay, dialog)
    )

def _restore_brightness_shift(shift_timer, overlay, dialog):
    shift_timer.stop()
    overlay.deleteLater()

    if dialog in active_dialogs:
        active_dialogs.remove(dialog)

    if dialog.isVisible():
        dialog.close()

    QMessageBox.information(
        None,
        "Brightness Shift Complete",
        "The light has returned to normal."
    )


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
    "undo_restriction": undo_restriction,
    "mark_fading": mark_fading,
    "analog_revision": analog_revision,
    "locked_marks": locked_marks,
    "brightness_shift": brightness_shift,
    "undo_erase_bank": undo_erase_bank
}