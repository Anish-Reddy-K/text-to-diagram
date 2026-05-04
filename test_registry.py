import diagrammer


def render_diamond(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    cx, cy = x + w / 2, y + h / 2
    label = node.get("label", "")
    pts = f"{cx},{y} {x + w},{cy} {cx},{y + h} {x},{cy}"
    return (
        f'<polygon points="{pts}" fill="none" stroke="black" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="13">{label}</text>'
    )


diagrammer.register_component("diamond", render_diamond, default_w=100, default_h=80)

spec = {
    "nodes": [
        {"id": "a", "type": "box", "label": "start"},
        {"id": "d", "type": "diamond", "label": "decide"},
        {"id": "b", "type": "box", "label": "end"},
    ],
    "edges": [
        {"from": "a", "to": "d"},
        {"from": "d", "to": "b"},
    ],
}

print(diagrammer.render(spec))
