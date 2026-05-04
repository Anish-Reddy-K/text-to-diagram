# diagrammer

Ask your coding agent for a clean technical diagram. Get back an SVG you can drop into a README, blog post, design doc, or slide.

`diagrammer` is a small Python renderer plus a Claude Code skill. The skill lets Claude turn plain-English diagram requests into a JSON spec, render that spec with the CLI, and hand you the finished SVG.

![LLM inference pipeline](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/hero.png)

## Use It From Claude Code

Install the CLI:

```bash
pipx install diagrammer
```

Install the Claude Code skill:

```text
/plugin marketplace add Anish-Reddy-K/diagrammer
/plugin install diagrammer@diagrammer-tools
```

Then ask Claude Code for the diagram you want:

```text
Draw an SVG diagram of a request flow: browser -> API -> Postgres -> response.
```

Claude writes the spec, runs `diagrammer`, and gives you an SVG file.

## What It Is For

Use `diagrammer` when you need a simple, useful technical diagram:

- system architecture
- request flows
- neural nets and transformer blocks
- state machines
- data pipelines
- quick visuals for docs, posts, and PRs

It is intentionally small: black-and-white blueprint-style SVG, a fixed set of diagram primitives, and no design-tool workflow.

## How It Works

The loop is:

```text
plain English -> JSON spec -> diagrammer -> SVG
```

The JSON is the interface between the LLM and the renderer. The LLM is good at describing structure; `diagrammer` is responsible for layout, arrows, labels, and SVG output.

Example spec:

```json
{
  "nodes": [
    {"id": "client", "type": "box", "label": "client"},
    {"id": "api", "type": "box", "label": "api"},
    {"id": "db", "type": "database", "label": "postgres"}
  ],
  "edges": [
    {"from": "client", "to": "api", "label": "request"},
    {"from": "api", "to": "db", "label": "query"}
  ]
}
```

Render it:

```bash
diagrammer spec.json > diagram.svg
```

## Using Other Agents

The Claude Code skill is the easiest path because it tells Claude exactly when and how to use the renderer.

In Codex or another coding agent, use the CLI directly. Ask the agent to create a diagram spec and run:

```bash
diagrammer path/to/spec.json > diagram.svg
```

For better results, give the agent the built-in guide:

```bash
diagrammer prompt
```

That prints the JSON format and examples the agent should follow.

## Examples

Each image below is rendered by `diagrammer` from a JSON file in [`examples/`](examples/).

### Request Flow

![flow](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/flow.png)

Good for docs that need to show services, edges, and labels without a heavy architecture tool.

### Neural Network

![mlp](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/mlp.png)

Boxes, circles, fan-in, fan-out, and automatic column layout.

### Transformer Stack

![transformer](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/transformer.png)

The `stack` node is useful for repeated blocks like transformer layers, worker pools, queues, and service replicas.

### System Architecture

![system architecture](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/system.png)

Groups, databases, edge labels, and simple service topology.

### Custom Shapes

![custom](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/custom.png)

If a built-in node is not enough, a spec can include a small raw SVG fragment as a `custom` node.

### Custom SVG Defs

![gradient](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/gradient.png)

Specs can include shared SVG `defs` for markers, gradients, and other reusable SVG pieces.

## Spec Reference

Top-level keys:

- `nodes` - list of nodes, each with `id`, `type`, and optional `label`.
- `edges` - list of edges, each with `from`, `to`, and optional `label`.
- `direction` - `"LR"` by default, or `"TB"` for top-to-bottom.
- `router` - `"straight"` by default, or `"ortho"` for right-angle bends.
- `col_gap`, `row_gap`, `margin` - layout tuning.
- `defs` - raw SVG defs injected into the output.

Built-in node types:

- `box`
- `circle`
- `text`
- `database`
- `stack`
- `group`
- `note`
- `custom`

Auto-layout fills in missing `x`, `y`, `w`, and `h`. Most specs should not hand-place nodes.

## Python API

```python
from diagrammer import render

svg = render(spec)
```

For Python-side extension, `register_component(name, render_fn, default_w, default_h)` lets you add node types without modifying the package. See [`registry_demo.py`](registry_demo.py).

## Development

Run tests:

```bash
python -m unittest
```

Refresh snapshots after intentional visual changes:

```bash
UPDATE_SNAPSHOTS=1 python -m unittest discover tests
```
