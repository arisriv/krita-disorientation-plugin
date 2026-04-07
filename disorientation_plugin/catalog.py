# separate file to store intervention catalog, for sake of cleanliness of __init__.py

INTERVENTION_CATALOG = {
    "Permanence + Revision": [
        {
            "key": "mark_fading",
            "title": "Mark Fading",
            "description": "Gradually destabilizes the permanence of marks over time. For now, this is a stored toggle only.",
            "control": "checkbox",
            "label": "Enable Mark Fading",
            "state_attr": "mark_fading_enabled"
        },
        {
            "key": "canvas_toss",
            "title": "Canvas Toss",
            "description": "Introduces the possibility of abandoning the current canvas and beginning again.",
            "control": "button",
            "label": "Test Canvas Toss",
            "state_attr": "canvas_toss_enabled" # Currently unused, until change back to checkbox
        },
        {
            "key": "undo_restriction",
            "title": "Undo Restriction",
            "description": "Temporarily blocks access to the undo and redo toolbar buttons for a fixed duration. Restored when the timer expires.",
            "control": "button",
            "label": "Test Undo Restriction"
        },
        {
            "key": "diagnose_actions",
            "title": "Diagnostic",
            "description": "",
            "control": "button",
            "label": "Run Diagnostics",
        },
        {
            "key": "test_tool_overlay",
            "title": "Test Tool Overlay",
            "description": "Tests the tool overlay in isolation.",
            "control": "button",
            "label": "Test Tool Overlay",
        }
    ],
    "Process + Temporality": [
        {
            "key": "creation_interval",
            "title": "Creation Interval",
            "description": "Temporarily blocks access to the canvas and prompts the artist to step away from their work. Canvas access is restored when the timer expires.",
            "control": "button",
            "label": "Test Creation Interval"
        },
        {
            "key": "brush_restriction",
            "title": "Brush Restriction",
            "description": "Temporarily replaces your current brush with a different one. Attempting to switch back will redirect you to the replacement brush. Your original brush is restored when the timer expires.",
            "control": "button",
            "label": "Test Brush Restriction"
        },
        {
            "key": "tool_restriction",
            "title": "Tool Restriction",
            "description": "Temporarily restricts a randomly selected tool for a fixed duration. Attempting to use it will redirect you to the freehand brush. The tool is restored when the timer expires.",
            "control": "button",
            "label": "Test Tool Restriction"
        },
        {
            "key": "subtractive_drawing",
            "title": "Subtractive Drawing",
            "description": "Forces eraser-only mode for a fixed duration. You are restricted to the freehand brush in eraser mode. All other tools are redirected back to the brush.",
            "control": "button",
            "label": "Test Subtractive Drawing"
        },
        {
            "key": "canvas_transformation",
            "title": "Canvas Transformation",
            "description": "Temporarily applies a random transformation to the canvas — mirroring, rotation, or both. The canvas is restored to its original state when the timer expires.",
            "control": "button",
            "label": "Test Canvas Transformation"
        }
    ],
    "Artistic Milieu": [
        {
            "key": "scenius_prompt",
            "title": "Scenius Prompt",
            "description": "Prompts engagement with another artwork, artist, or reference before continuing.",
            "control": "button",
            "label": "Test Scenius Prompt"
        },
        {
            "key": "perception_reframe",
            "title": "Placement / Perception Reframing",
            "description": "Reframe the artwork according to a new imagined viewing context.",
            "control": "button",
            "label": "Generate Reframing Prompt"
        },
        {
            "key": "memory_reflection",
            "title": "Memory-Based Reflection",
            "description": "Provides a prompt tied to memory and asks the artist to reflect before returning to the canvas.",
            "control": "button",
            "label": "Start Memory Reflection"
        }
    ],
    "Somaesthetics + Physical Environment": [
        {
            "key": "posture_check",
            "title": "Posture Check",
            "description": "Interrupts the digital workflow with a brief prompt about bodily posture.",
            "control": "button",
            "label": "Test Posture Check"
        },
        {
            "key": "body_reorientation",
            "title": "Body Reorientation",
            "description": "Interrupts digital workflow with a brief prompt on how to physically reorient your body and its orientation relative to your workspace and device.",
            "control": "button",
            "label": "Generate Body Reorientation Prompt"
        }
    ]
}