# diagrammer

Turn a JSON spec into a clean, blueprint-style SVG diagram. Designed so an LLM can write the spec from a plain-English description — describe → JSON → SVG → drop into post.

No dependencies. Stdlib only. Python 3.8+.

![LLM inference pipeline](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/hero.png)

## Install

```bash
pipx install diagrammer
```

Or use it directly from Claude Code as a skill:

```
/plugin marketplace add Anish-Reddy-K/diagrammer
/plugin install diagrammer@diagrammer-tools
```

Then ask Claude: *"draw an SVG diagram of a request flow: client → api → db"*.

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

## Examples

Each SVG below is rendered by the tool itself from the matching JSON spec in [`examples/`](examples/).

### Request flow with edge labels

![flow](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/flow.png)

```json
{
  "nodes": [
    {"id": "a", "type": "box", "label": "client"},
    {"id": "b", "type": "box", "label": "server"},
    {"id": "c", "type": "box", "label": "db"}
  ],
  "edges": [
    {"from": "a", "to": "b", "label": "request"},
    {"from": "b", "to": "c", "label": "query"}
  ]
}
```

### Neural network (fan-in / fan-out)

![mlp](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/mlp.png)

Just `box` and `circle` nodes plus edges — auto-layout handles the column flow and vertical centering.

### Transformer block (stack component)

![transformer](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/transformer.png)

```json
{
  "nodes": [
    {"id": "tok",    "type": "box",   "label": "tokens"},
    {"id": "blocks", "type": "stack", "label": "transformer", "count": 6},
    {"id": "head",   "type": "box",   "label": "lm_head"}
  ],
  "edges": [
    {"from": "tok",    "to": "blocks"},
    {"from": "blocks", "to": "head"}
  ]
}
```

### LLM inference pipeline

The hero image at the top of this README. A prompt flows through tokenization, embeddings, transformer layers, normalization, the language-model head, and returns the next token — see [`examples/inference.json`](examples/inference.json).

### System architecture (group + database)

![system architecture](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/system.png)

Combines `box`, `database`, `group`, and edge labels — see [`examples/system.json`](examples/system.json).

### Custom shapes

![custom](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/custom.png)

When no built-in shape fits, drop in raw SVG with `type: "custom"`:

```json
{
  "id": "tri", "type": "custom", "w": 80, "h": 80,
  "svg": "<polygon points='40,5 75,75 5,75' fill='none' stroke='black' stroke-width='1.5'/>"
}
```

### Custom + shared `defs` (gradients, markers)

![gradient](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/gradient.png)

A spec-level `"defs"` block injects shared SVG defs (gradients, custom markers, filters) that any `custom` node can reference by id. See [`examples/defs.json`](examples/defs.json).

## Spec reference

Top-level keys:

- `nodes` (required) — list of nodes, each with `id`, `type`, optional `label`.
- `edges` (required) — list of edges, each with `from`, `to`, optional `label`, `style` (`"dashed"` / `"solid"`), `weight` (`"thin"` / `"thick"`).
- `direction` — `"LR"` (default) or `"TB"`.
- `router` — `"straight"` (default) or `"ortho"` for right-angle bends.
- `col_gap`, `row_gap`, `margin` — layout tuning.
- `defs` — raw SVG defs string injected into `<defs>` (markers, gradients, filters).

Built-in node types: `box`, `circle`, `text`, `database`, `stack` (param: `count`), `note`, `group` (param: `children: [nodeIds]`), `custom` (params: `svg`, `w`, `h`).

Auto-layout fills in any missing `x` / `y` / `w` / `h`. Don't hand-place nodes unless you need to.

## LLM workflow

`prompt.md` (printable via `diagrammer prompt`) is a one-page doc you can paste into Claude/GPT to teach the spec format. The intended loop:

```bash
# in a chat with an LLM, paste the output of `diagrammer prompt`, then ask:
#   "draw a 3-layer MLP with a softmax head"
# copy the JSON it returns, then:
pbpaste | diagrammer - > mlp.svg && open mlp.svg
```

Or skip the copy/paste and use the Claude Code plugin (see Install above).

## Python API extension

For Python-side extension, `register_component(name, render_fn, default_w, default_h)` lets you add new node types without modifying the package. See [`registry_demo.py`](registry_demo.py).

## Tests

```bash
python -m unittest
```

Refresh snapshots after intentional visual changes:

```bash
UPDATE_SNAPSHOTS=1 python -m unittest discover tests
```
