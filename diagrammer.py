def render(spec):
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    direction = spec.get("direction", "LR")
    gaps = {
        "col_gap": spec.get("col_gap", COL_GAP),
        "row_gap": spec.get("row_gap", ROW_GAP),
        "margin": spec.get("margin", MARGIN),
    }
    _apply_defaults(nodes)
    if any("x" not in n or "y" not in n for n in nodes):
        _auto_layout(nodes, edges, direction, gaps)
    by_id = {n["id"]: n for n in nodes}

    width = spec.get("width") or _fit_width(nodes)
    height = spec.get("height") or _fit_height(nodes)

    router = spec.get("router", "straight")
    body = []
    for edge in edges:
        body.append(_edge(edge, by_id, router, direction))
    for node in nodes:
        if node["type"] == "box":
            body.append(_box(node))
        elif node["type"] == "circle":
            body.append(_circle(node))
        elif node["type"] == "text":
            body.append(_text(node))
        elif node["type"] == "database":
            body.append(_database(node))
        elif node["type"] == "stack":
            body.append(_stack(node))
    return _svg(width, height, body)


def _box(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    label = node.get("label", "")
    cx, cy = x + w / 2, y + h / 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'fill="none" stroke="black" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="14">{label}</text>'
    )


def _text(node):
    cx, cy = _center(node)
    label = node.get("label", "")
    return (
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="14">{label}</text>'
    )


def _stack(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    count = node.get("count", 3)
    offset = 6
    label = node.get("label", "")
    cx, cy = x + w / 2, y + h / 2
    style = 'fill="white" stroke="black" stroke-width="1.5"'
    rects = []
    for i in range(count - 1, -1, -1):
        rx = x + i * offset
        ry = y - i * offset
        rects.append(f'<rect x="{rx}" y="{ry}" width="{w}" height="{h}" {style}/>')
    text = (
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="14">{label}</text>'
    )
    return "".join(rects) + text


def _database(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    label = node.get("label", "")
    cx, cy = x + w / 2, y + h / 2
    rx, ry = w / 2, 8
    style = 'fill="none" stroke="black" stroke-width="1.5"'
    top = f'<ellipse cx="{cx}" cy="{y + ry}" rx="{rx}" ry="{ry}" {style}/>'
    left = f'<line x1="{x}" y1="{y + ry}" x2="{x}" y2="{y + h - ry}" {style}/>'
    right = f'<line x1="{x + w}" y1="{y + ry}" x2="{x + w}" y2="{y + h - ry}" {style}/>'
    bottom = (
        f'<path d="M {x} {y + h - ry} A {rx} {ry} 0 0 0 {x + w} {y + h - ry}" '
        f'fill="none" stroke="black" stroke-width="1.5"/>'
    )
    text = (
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="14">{label}</text>'
    )
    return top + left + right + bottom + text


def _circle(node):
    cx, cy = _center(node)
    r = node["w"] / 2
    label = node.get("label", "")
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" '
        f'fill="none" stroke="black" stroke-width="1.5"/>'
        f'<text x="{cx}" y="{cy}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="14">{label}</text>'
    )


def _edge(edge, by_id, router, direction):
    a = by_id[edge["from"]]
    b = by_id[edge["to"]]
    stroke_w = 3 if edge.get("weight") == "thick" else 1.5
    dash = ' stroke-dasharray="6,4"' if edge.get("style") == "dashed" else ""

    if edge["from"] == edge["to"]:
        return _self_loop(a, stroke_w, dash, edge.get("label"))

    if router == "ortho":
        line, x1, y1, x2, y2 = _ortho_edge(a, b, stroke_w, dash, direction)
    else:
        x1, y1 = _border_point(a, _center(b))
        x2, y2 = _border_point(b, _center(a))
        line = (
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="black" stroke-width="{stroke_w}"{dash} '
            f'marker-end="url(#arrow)"/>'
        )
    label = edge.get("label")
    if not label:
        return line
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    pad = 4
    char_w = 7.2
    rect_w = len(label) * char_w + pad * 2
    rect_h = 16
    bg = (
        f'<rect x="{mx - rect_w / 2}" y="{my - rect_h / 2}" '
        f'width="{rect_w}" height="{rect_h}" fill="white" stroke="none"/>'
    )
    text = (
        f'<text x="{mx}" y="{my}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="12">{label}</text>'
    )
    return line + bg + text


def _ortho_edge(a, b, stroke_w, dash, direction):
    ax, ay = _center(a)
    bx, by = _center(b)
    horiz = direction == "LR"
    bias = 0.3  # bend at 30% from source so 70% is straight approach into target
    if horiz:
        x1 = a["x"] + a["w"] if bx > ax else a["x"]
        y1 = ay
        x2 = b["x"] if bx > ax else b["x"] + b["w"]
        y2 = by
        mid = x1 + (x2 - x1) * bias
        d = f"M {x1} {y1} L {mid} {y1} L {mid} {y2} L {x2} {y2}"
    else:
        x1 = ax
        y1 = a["y"] + a["h"] if by > ay else a["y"]
        x2 = bx
        y2 = b["y"] if by > ay else b["y"] + b["h"]
        mid = y1 + (y2 - y1) * bias
        d = f"M {x1} {y1} L {x1} {mid} L {x2} {mid} L {x2} {y2}"
    line = (
        f'<path d="{d}" fill="none" stroke="black" '
        f'stroke-width="{stroke_w}"{dash} marker-end="url(#arrow)"/>'
    )
    return line, x1, y1, x2, y2


def _self_loop(node, stroke_w, dash, label):
    cx, _ = _center(node)
    top = node["y"]
    p1x, p2x = cx - node["w"] * 0.15, cx + node["w"] * 0.15
    cy = top - 45
    path = (
        f'<path d="M {p1x} {top} C {p1x} {cy}, {p2x} {cy}, {p2x} {top}" '
        f'fill="none" stroke="black" stroke-width="{stroke_w}"{dash} '
        f'marker-end="url(#arrow)"/>'
    )
    if not label:
        return path
    rect_w = len(label) * 7.2 + 8
    rect_h = 16
    ly = cy - 4
    bg = (
        f'<rect x="{cx - rect_w / 2}" y="{ly - rect_h / 2}" '
        f'width="{rect_w}" height="{rect_h}" fill="white" stroke="none"/>'
    )
    text = (
        f'<text x="{cx}" y="{ly}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="monospace" '
        f'font-size="12">{label}</text>'
    )
    return path + bg + text


def _center(node):
    return (node["x"] + node["w"] / 2, node["y"] + node["h"] / 2)


def _border_point(node, target):
    cx, cy = _center(node)
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return (cx, cy)
    if node["type"] == "circle":
        r = node["w"] / 2
        d = (dx * dx + dy * dy) ** 0.5
        return (cx + dx * r / d, cy + dy * r / d)
    hw, hh = node["w"] / 2, node["h"] / 2
    sx = hw / abs(dx) if dx != 0 else float("inf")
    sy = hh / abs(dy) if dy != 0 else float("inf")
    s = min(sx, sy)
    return (cx + dx * s, cy + dy * s)


DEFAULT_W = 120
DEFAULT_H = 60
COL_GAP = 80
ROW_GAP = 30
MARGIN = 40


def _apply_defaults(nodes):
    for n in nodes:
        if n["type"] == "circle":
            if "r" in n:
                n.setdefault("w", n["r"] * 2)
                n.setdefault("h", n["r"] * 2)
            n.setdefault("w", 50)
            n.setdefault("h", 50)
        elif n["type"] == "text":
            n.setdefault("w", len(n.get("label", "")) * 8 + 16)
            n.setdefault("h", 24)
        elif n["type"] == "database":
            n.setdefault("w", 80)
            n.setdefault("h", 80)
        elif n["type"] == "stack":
            n.setdefault("w", DEFAULT_W)
            n.setdefault("h", DEFAULT_H)
        else:
            n.setdefault("w", DEFAULT_W)
            n.setdefault("h", DEFAULT_H)


def _auto_layout(nodes, edges, direction, gaps):
    depth = _compute_depths(nodes, edges)
    cols = {}
    for n in nodes:
        cols.setdefault(depth[n["id"]], []).append(n)

    margin = gaps["margin"]
    # primary axis = depth direction; secondary axis = stacking within a column
    if direction == "TB":
        prim, sec = "h", "w"
        prim_xy, sec_xy = "y", "x"
        prim_gap, sec_gap = gaps["row_gap"], gaps["col_gap"]
    else:  # LR
        prim, sec = "w", "h"
        prim_xy, sec_xy = "x", "y"
        prim_gap, sec_gap = gaps["col_gap"], gaps["row_gap"]

    # widen gaps between adjacent columns to fit edge labels with breathing room
    label_gap = {}
    if direction == "LR":
        for e in edges:
            if "label" not in e:
                continue
            src_d, dst_d = depth[e["from"]], depth[e["to"]]
            if dst_d - src_d == 1:
                needed = len(e["label"]) * 7.2 + 8 + 80  # text + bg pad + breathing
                label_gap[src_d] = max(label_gap.get(src_d, 0), needed)

    col_prim = {c: max(n[prim] for n in ns) for c, ns in cols.items()}
    prim_of = {}
    cursor = margin
    for c in sorted(cols):
        prim_of[c] = cursor
        gap_after = max(prim_gap, label_gap.get(c, 0))
        cursor += col_prim[c] + gap_after

    col_sec = {
        c: sum(n[sec] for n in ns) + sec_gap * (len(ns) - 1)
        for c, ns in cols.items()
    }
    tallest = max(col_sec.values())

    for c, ns in cols.items():
        s = margin + (tallest - col_sec[c]) / 2
        for n in ns:
            n[prim_xy] = prim_of[c] + (col_prim[c] - n[prim]) / 2
            n[sec_xy] = s
            s += n[sec] + sec_gap


def _compute_depths(nodes, edges):
    ids = [n["id"] for n in nodes]
    incoming = {i: [] for i in ids}
    for e in edges:
        if e["from"] != e["to"]:
            incoming[e["to"]].append(e["from"])
    depth = {}

    def d(i, seen=()):
        if i in depth:
            return depth[i]
        if i in seen:
            return 0
        if not incoming[i]:
            depth[i] = 0
        else:
            depth[i] = 1 + max(d(p, seen + (i,)) for p in incoming[i])
        return depth[i]

    for i in ids:
        d(i)
    return depth


def _fit_width(nodes):
    return max((n["x"] + n["w"] for n in nodes), default=0) + MARGIN


def _fit_height(nodes):
    return max((n["y"] + n["h"] for n in nodes), default=0) + MARGIN


def _svg(width, height, body):
    defs = (
        '<defs>'
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="black"/>'
        '</marker>'
        '</defs>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        + defs
        + "".join(body)
        + "</svg>"
    )


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "-":
        spec = json.load(sys.stdin)
    else:
        with open(sys.argv[1]) as f:
            spec = json.load(f)
    sys.stdout.write(render(spec))

