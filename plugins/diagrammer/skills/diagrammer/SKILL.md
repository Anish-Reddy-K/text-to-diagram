---
name: diagrammer
description: Render a clean blueprint-style SVG diagram from a JSON spec. Use when the user asks to draw, sketch, or diagram a flow, neural net, system architecture, state machine, or any node-and-edge picture they want as an SVG.
allowed-tools: Bash, Write, Read
---

# diagrammer

Turns a JSON spec into a hand-crafted SVG diagram. No design tool, no rendering deps — just `render(spec) -> svg_string`.

## When to use

The user asks for a visual: "draw an MLP," "diagram this request flow," "sketch the system architecture," "make a state machine for X." If they want an SVG file (or one that's about to be embedded in a blog post / doc), this is the tool.

Skip it if they want a chart with axes (use a plotting tool), a UML class diagram with stereotypes, or a precise floorplan.

## How to use

1. Read the full spec format from `src/diagrammer/prompt.md` (or run `python -m diagrammer prompt`).
2. Write a JSON spec for what the user asked for.
3. Save it and render:

```bash
echo '<JSON>' | python -m diagrammer - > out.svg
# or
python -m diagrammer path/to/spec.json > out.svg
```

4. Show the user the SVG path. If they want to view it: `open out.svg` (macOS) or print the contents.

### If `python -m diagrammer` fails with `No module named diagrammer`

The package isn't installed in the active python. Locate the repo (it contains `src/diagrammer/__init__.py`) and run with `PYTHONPATH` instead — no install needed:

```bash
PYTHONPATH=/path/to/diagrammer/src python -m diagrammer path/to/spec.json > out.svg
```

If you don't know the repo path, find it: `find ~ -type d -name diagrammer -path '*/src/diagrammer' 2>/dev/null | head -1` and use the parent's parent (drop `/src/diagrammer`).

## Spec essentials

```json
{
  "direction": "LR" | "TB",
  "router": "straight" | "ortho",
  "nodes": [{"id": "a", "type": "box", "label": "..."}],
  "edges": [{"from": "a", "to": "b", "label": "?", "style": "dashed", "weight": "thick"}]
}
```

Built-in node types: `box`, `circle`, `text`, `database`, `stack` (param `count`), `note`, `group` (param `children: [ids]`), `custom` (params `svg`, `w`, `h`).

Auto-layout fills `x`/`y`/`w`/`h` from edge depth — don't hand-place nodes. For shapes the built-ins don't cover, use `type: "custom"` with raw SVG anchored at `(0,0)`.

See `src/diagrammer/prompt.md` for three worked examples (linear flow, MLP, system architecture) and the custom escape hatch.
