# diagrammer

Ask your coding agent for a clean technical diagram. Get back an SVG you can drop into a README, blog post, design doc, or slide.

`diagrammer` is a small Python renderer, a Claude Code skill, and an MCP server. The main workflow is simple: install the skill, ask for a diagram in plain English, and let the agent generate the SVG.

![LLM inference pipeline](https://raw.githubusercontent.com/Anish-Reddy-K/diagrammer/master/docs/img/hero.png)

## Quick Start: Claude Code

Install the renderer:

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

## Ways To Use It

### Claude Code Skill

This is the recommended path. The skill teaches Claude when to use `diagrammer`, how to write the JSON spec, and how to render the SVG.

```text
/plugin marketplace add Anish-Reddy-K/diagrammer
/plugin install diagrammer@diagrammer-tools
```

After that, ask naturally:

```text
Make a clean SVG diagram of my auth flow: browser, API, session store, Postgres.
```

### Codex And Other Coding Agents

Codex does not use Claude Code skills. Use the CLI directly and give Codex the diagram format when needed:

```bash
pipx install diagrammer
diagrammer prompt
```

Then ask Codex to create a JSON spec and render it:

```text
Create a diagrammer spec for this service flow and run diagrammer to save it as docs/auth-flow.svg.
```

The useful pattern is: agent writes `spec.json`, agent runs `diagrammer spec.json > diagram.svg`, you keep the SVG.

### MCP Server

For MCP-compatible clients, `diagrammer` also ships an MCP server exposing one tool:

```text
render_diagram(spec) -> svg_string
```

Install from GitHub with the MCP extra:

```bash
pipx install "diagrammer[mcp] @ git+https://github.com/Anish-Reddy-K/diagrammer.git"
```

Then point your MCP client at:

```bash
diagrammer-mcp
```

Use the MCP path when you want the client to call a diagram-rendering tool directly instead of shelling out to the CLI.

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
