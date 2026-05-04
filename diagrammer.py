def render(spec):
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    _apply_defaults(nodes)
    if any("x" not in n or "y" not in n for n in nodes):
        _auto_layout(nodes, edges)
    by_id = {n["id"]: n for n in nodes}

    width = spec.get("width") or _fit_width(nodes)
    height = spec.get("height") or _fit_height(nodes)

    body = []
    for node in nodes:
        if node["type"] == "box":
            body.append(_box(node))
    for edge in edges:
        body.append(_edge(edge, by_id))
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


def _edge(edge, by_id):
    a = by_id[edge["from"]]
    b = by_id[edge["to"]]
    x1, y1 = _border_point(a, _center(b))
    x2, y2 = _border_point(b, _center(a))
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="black" stroke-width="1.5" '
        f'marker-end="url(#arrow)"/>'
    )


def _center(node):
    return (node["x"] + node["w"] / 2, node["y"] + node["h"] / 2)


def _border_point(node, target):
    cx, cy = _center(node)
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return (cx, cy)
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
        n.setdefault("w", DEFAULT_W)
        n.setdefault("h", DEFAULT_H)


def _auto_layout(nodes, edges):
    depth = _compute_depths(nodes, edges)
    cols = {}
    for n in nodes:
        cols.setdefault(depth[n["id"]], []).append(n)

    col_widths = {c: max(n["w"] for n in ns) for c, ns in cols.items()}
    x_of = {}
    cursor = MARGIN
    for c in sorted(cols):
        x_of[c] = cursor
        cursor += col_widths[c] + COL_GAP

    for c, ns in cols.items():
        col_h = sum(n["h"] for n in ns) + ROW_GAP * (len(ns) - 1)
        y = MARGIN
        for n in ns:
            n["x"] = x_of[c] + (col_widths[c] - n["w"]) / 2
            n["y"] = y
            y += n["h"] + ROW_GAP
        _ = col_h


def _compute_depths(nodes, edges):
    ids = [n["id"] for n in nodes]
    incoming = {i: [] for i in ids}
    for e in edges:
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
