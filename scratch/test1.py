import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import diagrammer

spec = {
    "width": 400,
    "height": 200,
    "nodes": [
        {"id": "a", "type": "box", "x": 50, "y": 50, "w": 120, "h": 60, "label": "hello"}
    ],
}

print(diagrammer.render(spec))
