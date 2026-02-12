
from typing import Dict, List, TypedDict

class TemplateStep(TypedDict):
    pass # Structure implied by usage, effectively just a list of strings for now in the simple case, 
         # but let's stick to the plan's structure: "steps": ["clean", "summarize", "keypoints"]

PREDEFINED_TEMPLATES = {
    "quick": {
        "label": "Quick Understanding", 
        "description": "Clean text, summarize it, and extract key points.",
        "steps": ["clean", "summarize", "keypoints"]
    },
    "simplify": {
        "label": "Simplify", 
        "description": "Clean text, rewrite it simply, and provide an analogy.",
        "steps": ["clean", "simplify", "analogy"]
    },
    "office": {
        "label": "Office Assistant", 
        "description": "Clean text, classify it, and analyze the tone.",
        "steps": ["clean", "classify", "tone"]
    }
}
