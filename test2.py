import diagrammer

spec = {
    "width": 500,
    "height": 200,
    "nodes": [
        {"id": "a", "type": "box", "x": 50,  "y": 70, "w": 120, "h": 60, "label": "input"},
        {"id": "b", "type": "box", "x": 320, "y": 70, "w": 120, "h": 60, "label": "output"},
    ],
    "edges": [
        {"from": "a", "to": "b"},
    ],
}

print(diagrammer.render(spec))
