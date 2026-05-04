import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import diagrammer

spec = {
    "nodes": [
        {"id": "a", "type": "box", "label": "input"},
        {"id": "b", "type": "box", "label": "encode"},
        {"id": "c", "type": "box", "label": "decode"},
        {"id": "d", "type": "box", "label": "output"},
    ],
    "edges": [
        {"from": "a", "to": "b"},
        {"from": "b", "to": "c"},
        {"from": "c", "to": "d"},
    ],
}

print(diagrammer.render(spec))
