# diagrammer

Turn a JSON spec into a clean, blueprint-style SVG diagram. Designed so an LLM can write the spec from a plain-English description — describe → JSON → SVG → drop into post.

No dependencies. Stdlib only. Python 3.8+.

## Install

```bash
pip install -e .
```

## 30-second example

```bash
echo '{
  "nodes": [
    {"id": "x",  "type": "box",    "label": "input"},
    {"id": "h1", "type": "circle", "label": "h1"},
    {"id": "h2", "type": "circle", "label": "h2"},
    {"id": "y",  "type": "box",    "label": "output"}
  ],
  "edges": [
    {"from": "x", "to": "h1"}, {"from": "x", "to": "h2"},
    {"from": "h1", "to": "y"}, {"from": "h2", "to": "y"}
  ]
}' | diagrammer - > mlp.svg && open mlp.svg
```

Or from a file: `diagrammer examples/mlp.json > out.svg`.

## Spec reference

Top-level keys:

- `nodes` (required) — list of nodes, each with `id`, `type`, optional `label`.
- `edges` (required) — list of edges, each with `from`, `to`, optional `label`, `style` (`"dashed"`/`"solid"`), `weight` (`"thin"`/`"thick"`).
- `direction` — `"LR"` (default) or `"TB"`.
- `router` — `"straight"` (default) or `"ortho"` for right-angle bends.
- `col_gap`, `row_gap`, `margin` — layout tuning.
- `defs` — raw SVG defs string injected into `<defs>` (markers, gradients, filters).

Built-in node types: `box`, `circle`, `text`, `database`, `stack` (param: `count`), `note`, `group` (param: `children: [nodeIds]`), `custom` (params: `svg`, `w`, `h`).

Auto-layout fills in any missing `x`/`y`/`w`/`h`. Don't hand-place nodes unless you need to.

## LLM workflow

`prompt.md` (printable via `diagrammer prompt`) is a one-page doc you can paste into Claude/GPT to teach the spec format. The intended loop:

```bash
# in a chat with an LLM, paste prompt.md, then ask:
#   "draw a 3-layer MLP with a softmax head"
# copy the JSON it returns, then:
pbpaste | diagrammer - > mlp.svg && open mlp.svg
```

## Custom components

When no built-in shape fits, use `type: "custom"` and supply raw SVG anchored at `(0,0)`:

```json
{
  "id": "tri", "type": "custom", "w": 80, "h": 80, "label": "split",
  "svg": "<polygon points='40,5 75,75 5,75' fill='none' stroke='black' stroke-width='1.5'/>"
}
```

The renderer wraps your SVG in `<g transform="translate(x,y)">` and uses `w`/`h` for arrow termination. For shared defs (gradients, custom markers), put them in the spec-level `"defs"` string and reference by id.

For Python-side extension, `register_component(name, render_fn, default_w, default_h)` lets you add new types without modifying the package. See `test_registry.py`.

## Tests

```bash
python -m unittest discover tests
```

Refresh snapshots after intentional visual changes:

```bash
UPDATE_SNAPSHOTS=1 python -m unittest discover tests
```
