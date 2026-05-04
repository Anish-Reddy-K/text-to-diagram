import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import diagrammer

spec = {
    "nodes": [
        {"id": "x", "type": "box", "label": "input"},
        {"id": "h1", "type": "circle", "label": "h1"},
        {"id": "h2", "type": "circle", "label": "h2"},
        {"id": "h3", "type": "circle", "label": "h3"},
        {"id": "y", "type": "box", "label": "output"},
    ],
    "edges": [
        {"from": "x", "to": "h1"},
        {"from": "x", "to": "h2"},
        {"from": "x", "to": "h3"},
        {"from": "h1", "to": "y"},
        {"from": "h2", "to": "y"},
        {"from": "h3", "to": "y"},
    ],
}

print(diagrammer.render(spec))
