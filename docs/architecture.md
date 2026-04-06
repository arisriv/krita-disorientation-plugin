--- Tool Restriction — Shelved ----
Goal: temporarily ban a specific tool, redirect to freehand brush if user tries to switch to it, restore after timer.

Why it's hard:
Brush restriction works because the API exposes both read (currentBrushPreset) and write (setCurrentBrushPreset) — we can detect state and respond to it
Tool restriction needs the same read/write pattern but the API only exposes write (action.trigger() to switch tools) — no reliable way to read what tool is currently active
currentToolName does not exist on View, Canvas, or Window objects
isChecked() on tool actions does not reflect active tool state
The notifier object (app.notifier()) does not emit a toolChanged signal
triggered.connect on a tool action does not reliably fire from canvas input — same proxy limitation as setEnabled

Result: can force a tool switch but cannot detect when the user switches back, so the poll-and-redirect pattern used by brush restriction is not possible with the current API.

Potential path forward if revisited: Qt event filter on the main canvas window at a lower level than the Python API exposes.

The only workaround I can think of right now would be unconditionally triggering the freehand brush 
  on every poll tick, which restricts all tools simultaneously rather than a 
  specific one — too blunt for the intended intervention design