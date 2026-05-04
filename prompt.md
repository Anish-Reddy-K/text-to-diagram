# Diagrammer spec — LLM guide

You are emitting a JSON spec that gets rendered to SVG by `diagrammer`. Output **one JSON object only** — no prose, no code fences, no commentary.

## Spec shape

```json
{
  "direction": "LR" | "TB",          // optional, default "LR"
  "router": "straight" | "ortho",    // optional, default "straight"
  "col_gap": 80, "row_gap": 30, "margin": 40,  // optional layout tuning
  "defs": "<marker.../>...",         // optional shared SVG defs
  "nodes": [...],
  "edges": [...]
}
```

Auto-layout places nodes by the depth of their incoming edges (left→right or top→bottom). **Do not set `x`/`y`** unless you have a reason — let layout handle it. `w`/`h` are also optional; defaults work for most cases.

## Node types

Every node needs `id` (unique string) and `type`. `label` is optional but usually wanted.

- `box` — rectangle, the default for most things.
- `circle` — round node; neurons, states.
- `text` — label only, no border; annotations.
- `database` — cylinder; datastores.
- `stack` — layered rectangles for repeated blocks. Extra: `count` (default 3).
- `note` — callout with folded corner; sidebar comments.
- `group` — dashed box around children. Extra: `children: [nodeIds]`.
- `custom` — escape hatch, you supply raw SVG. Extra: `svg`, `w`, `h`.

## Edges

```json
{"from": "a", "to": "b", "label": "?", "style": "dashed", "weight": "thick"}
```

- `label` optional. `style`: `"solid"` (default) or `"dashed"`. `weight`: `"thin"` (default) or `"thick"`.
- `from == to` draws a self-loop.
- The `router` is set per-spec, not per-edge.

## Worked examples

### 1. Linear flow

```json
{
  "nodes": [
    {"id": "in",  "type": "box", "label": "request"},
    {"id": "api", "type": "box", "label": "api"},
    {"id": "db",  "type": "database", "label": "users"},
    {"id": "out", "type": "box", "label": "response"}
  ],
  "edges": [
    {"from": "in",  "to": "api"},
    {"from": "api", "to": "db",  "label": "query"},
    {"from": "db",  "to": "api", "style": "dashed"},
    {"from": "api", "to": "out"}
  ]
}
```

### 2. MLP (fan-out, fan-in)

```json
{
  "nodes": [
    {"id": "x",  "type": "box",    "label": "input"},
    {"id": "h1", "type": "circle", "label": "h1"},
    {"id": "h2", "type": "circle", "label": "h2"},
    {"id": "h3", "type": "circle", "label": "h3"},
    {"id": "y",  "type": "box",    "label": "output"},
    {"id": "hidden", "type": "group", "label": "hidden", "children": ["h1","h2","h3"]}
  ],
  "edges": [
    {"from": "x", "to": "h1"}, {"from": "x", "to": "h2"}, {"from": "x", "to": "h3"},
    {"from": "h1", "to": "y"}, {"from": "h2", "to": "y"}, {"from": "h3", "to": "y"}
  ]
}
```

### 3. System architecture

```json
{
  "direction": "TB",
  "router": "ortho",
  "nodes": [
    {"id": "client", "type": "box", "label": "client"},
    {"id": "lb",     "type": "box", "label": "load balancer"},
    {"id": "api",    "type": "stack", "label": "api", "count": 3},
    {"id": "cache",  "type": "database", "label": "redis"},
    {"id": "db",     "type": "database", "label": "postgres"},
    {"id": "note",   "type": "note", "label": "sticky sessions"}
  ],
  "edges": [
    {"from": "client", "to": "lb"},
    {"from": "lb",     "to": "api"},
    {"from": "api",    "to": "cache", "label": "read"},
    {"from": "api",    "to": "db",    "label": "write", "weight": "thick"},
    {"from": "lb",     "to": "note",  "style": "dashed"}
  ]
}
```

## The `custom` escape hatch

When no built-in shape fits, emit a `custom` node with raw SVG anchored at `(0,0)`. The renderer wraps it in `<g transform="translate(x,y)">` and uses `w`/`h` for arrow clipping.

```json
{
  "id": "tri",
  "type": "custom",
  "w": 80, "h": 80,
  "label": "split",
  "svg": "<polygon points='40,5 75,75 5,75' fill='none' stroke='black' stroke-width='1.5'/>"
}
```

For shared defs (gradients, custom markers, filters), put them in the spec-level `"defs"` string and reference by id from your `custom` SVG.

## Rules

- Output only the JSON object. No markdown, no explanation.
- Prefer built-in types. Reach for `custom` only when nothing fits.
- Keep `id`s short and descriptive (`api`, `h1`, `db`) — they appear in edges.
- Don't set `x`/`y`. Don't set `width`/`height` on the spec.
- If asked for a shape that doesn't exist (triangle, hexagon, cloud, etc.), use `custom`.
