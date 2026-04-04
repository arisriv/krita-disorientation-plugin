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
        }
    ],
    "Process + Temporality": [
        {
            "key": "canvas_toss",
            "title": "Canvas Toss",
            "description": "Introduces the possibility of abandoning the current canvas and beginning again.",
            "control": "button",
            "label": "Test Canvas Toss",
            "state_attr": "canvas_toss_enabled"
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
        }
    ],
    "Somaesthetics + Physical Environment": [
        {
            "key": "posture_check",
            "title": "Posture Check",
            "description": "Interrupts the digital workflow with a brief prompt about bodily position and orientation.",
            "control": "button",
            "label": "Test Posture Check"
        }
    ]
}