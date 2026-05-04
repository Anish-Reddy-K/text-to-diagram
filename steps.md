# Diagrammer — Build Plan

## Context (read this first)

**What we're building.** A tiny tool that turns a JSON spec into a clean, blueprint-style SVG diagram. The target user is someone writing technical blog posts (neural nets, request flows, system architectures) who wants 3Blue1Brown-meets-Excalidraw output without opening a design tool. The spec is also designed to be easy for an LLM to write, so the primary workflow is: describe diagram in English → LLM emits JSON → tool emits SVG → drop SVG into post.

**Design philosophy (non-negotiable).**
- **One file, stdlib only, no dependencies** until a step explicitly adds one. Current core lives in `diagrammer.py` (~470 lines).
- **Hand-rolled SVG as f-strings.** No D3, no React, no headless browser, no rendering libs. SVG is just text. Layout math is *the actual product* — don't hide it behind a dep.
- **Small, fixed component set** that covers ~90% of AI/systems diagrams: box, circle, database, stack, group, note, text, arrow. Adding a new built-in component is trivial; an LLM can also define a one-off `custom` component inline (Phase 4) without touching the library.
- **Surgical changes.** Every step touches only what it must. No speculative abstractions, no "flexibility" features, no error handling for impossible cases. If a step's diff has unrelated cleanup, the step is wrong.
- **LLM-first spec.** Field names are short and obvious (`from`, `to`, `label`, `type`). Defaults are aggressive so a minimal spec — just `nodes` + `edges` with `type` and `label` — produces a usable diagram. Auto-layout fills in any missing `x`/`y`/`w`/`h`.

**Stack.** Python 3, stdlib only. No build step, no `pip install` (until packaging in Phase 9). Tests use `unittest` (stdlib). The three eventual distribution interfaces (Claude Skill, MCP server, interactive CLI) are all thin wrappers over a single function: `render(spec) -> svg_string`.

**Current state.** Phases 0–4 (steps 1–20) are done. `diagrammer.py` exports `render(spec)` and `register_component(name, fn, default_w, default_h)`. Built-in node types: `box`, `circle`, `text`, `database`, `stack`, `group`, `note`, `custom`. Edges support labels (with auto-widened column gaps for breathing room), `style` (dashed/solid), `weight` (thin/thick), self-loops, and `router: "ortho"` for right-angle bends. Layout supports `direction` (LR/TB), per-spec `col_gap`/`row_gap`/`margin`, vertical centering of columns, and a 30%-from-source bend bias for ortho. Spec accepts a top-level `defs` string for shared SVG defs (gradients, custom markers, filters) referenced from `custom` nodes. Edges are drawn behind nodes so stacks visually emerge from behind their back layers. CLI reads JSON from a path or stdin. Working examples: `mlp.json`, `ortho.json`, `transformer.json`, `grouped.json`, `note.json`, `custom.json`, `defs.json`.

**Working agreement.** Each step below is small enough to finish in one sitting and ends with a verifiable check. Don't skip ahead. Don't bundle. If a step takes more than ~30 min, it's too big — split it. After each step, the user runs the verify command and either says "pass" (move to next) or reports what's wrong (fix, then re-verify).

---

---

## Phase 0 — Core (done)

- [x] **1.** `render(spec)` for one box → open SVG, see labeled rectangle.
- [x] **2.** Multiple boxes + arrow with edge clipping → arrow ends at box border.
- [x] **3.** Auto-layout left-to-right via topological order → drop `x`/`y` from spec.
- [x] **4.** `circle` component, type-aware border clipping → MLP-style fan-out.
- [x] **5.** CLI: `python diagrammer.py spec.json > out.svg`, also reads stdin.

---

## Phase 1 — Layout polish (done)

- [x] **6.** Vertical-center each column. Verify: in the test4 MLP, circles align with the vertical midpoint of the boxes — no top-heavy clustering.
- [x] **7.** Add `direction` to spec (`"LR"` default, `"TB"` for top-to-bottom). Verify: same MLP rendered with `direction: "TB"` flows downward.
- [x] **8.** Add `gap` config (`col_gap`, `row_gap`, `margin`) overridable per spec. Verify: tighter and looser layouts of same diagram.

## Phase 2 — Edge polish (done)

- [x] **9.** Edge labels: `{"from", "to", "label"}` renders text on midpoint with a small white background rect. Verify: `a -> b "weights"` shows label without crossing the line.
- [x] **10.** Edge styles: `"style": "dashed" | "solid"`, `"weight": "thin" | "thick"`. Verify: visually distinct.
- [x] **11.** Self-loops: edge where `from == to` renders as a curved arrow back to the same node. Verify: a single-node spec with self-loop renders cleanly.
- [x] **12.** Orthogonal routing option: `"router": "ortho"` draws edges with right-angle bends instead of straight lines. Verify: top-to-bottom flow with ortho router has no diagonal lines.

## Phase 3 — Core components (done)

Each: add type, renderer, default size, border-clip rule. One PR per component.

- [x] **13.** `text` — label-only node, no border. For annotations.
- [x] **14.** `database` — cylinder shape. Border clip approximated as box.
- [x] **15.** `stack` — layered rectangle (offset duplicates) for transformer blocks etc. Param: `count`.
- [x] **16.** `group` — rectangle that contains child nodes; children laid out inside its bounds. Param: `children: [nodeIds]`. Verify: a group around `h1, h2, h3` draws a labeled box around all three.
- [x] **17.** `note` — callout box with different stroke style for sidebar comments.

## Phase 4 — Custom components (LLM extensibility) (done)

The escape hatch when the core set isn't enough. The LLM writes SVG fragments inline; layout still works because `w`/`h` are declared.

- [x] **18.** `custom` type: `{"type": "custom", "svg": "<g>...</g>", "w": N, "h": M, "label": "..."}`. The fragment is anchored at `(0,0)` and the renderer wraps it in `<g transform="translate(x,y)">`. Border clipping uses `w`/`h` like a box. Verify: a hand-written triangle node renders in the right place with correct arrow termination.
- [x] **19.** `defs` block at spec level: `{"defs": "<marker.../>...", "nodes": [...]}` injects shared SVG defs (gradients, filters, custom markers). Verify: a custom arrowhead marker referenced from a `custom` node works.
- [x] **20.** Component registry (Python-only, not for LLM use): `register_component("foo", fn)` so the CLI can be extended in code. Verify: a user-written `foo` component renders without modifying `diagrammer.py`.

## Phase 5 — Visual style

- [ ] **21.** Theme system: `"theme": "blueprint" | "minimal" | "sketch"`. Each theme is a dict of stroke colors, widths, fonts, fills. Default = blueprint (thin black lines, monospace, off-white bg).
- [ ] **22.** Sketch mode: optionally use [rough.js](https://roughjs.com/)-style hand-drawn lines. Implementation: hand-rolled jitter on path coordinates, no dep. Verify: same diagram looks hand-drawn.
- [ ] **23.** Background grid option: `"grid": true` adds a subtle dotted grid. Verify: blueprint feel.

## Phase 6 — Spec validation

- [ ] **24.** `validate(spec)` function: checks required keys, edge endpoints exist, no duplicate ids. Returns list of error strings. Verify: malformed spec returns useful errors instead of crashing.
- [ ] **25.** Wire validation into `render`: on invalid spec, raise with all errors at once (not just the first). Verify: spec missing both `nodes[0].type` and a dangling edge reports both.
- [ ] **26.** Publish JSON Schema (`spec.schema.json`) generated from the same source of truth. Verify: schema validates against the example specs.

## Phase 7 — Tests

- [ ] **27.** Set up `tests/` with `unittest` (stdlib, no deps). Add snapshot test: render a fixed spec, compare to checked-in `.svg` file. Verify: `python -m unittest` passes.
- [ ] **28.** One snapshot per component type (box, circle, text, database, stack, group, note, custom). Verify: regressions in any component break a single test.
- [ ] **29.** Layout tests: same spec with different `direction`s produces deterministic output. Verify: re-running gives identical SVG.

## Phase 8 — The prompt (the AI angle)

- [ ] **30.** Write `prompt.md` — one-page snippet teaching an LLM the spec format, with 3 worked examples (flow, MLP, system architecture). Verify: paste into a fresh Claude/GPT, ask for a diagram, get valid JSON.
- [ ] **31.** Add a "custom component" section to the prompt explaining the escape hatch with one example. Verify: LLM produces a valid `custom` node when asked for a shape we don't support.
- [ ] **32.** Add a `prompt` subcommand: `python diagrammer.py prompt` prints the snippet to stdout. So you can `pbcopy` it instantly. Verify: command outputs the same content as `prompt.md`.

## Phase 9 — Packaging

- [ ] **33.** Move `diagrammer.py` into `src/diagrammer/__init__.py`. Add `pyproject.toml` with `[project.scripts] diagrammer = "diagrammer:cli"`. Verify: `pip install -e .` then `diagrammer mlp.json > out.svg` works from any directory.
- [ ] **34.** Add `README.md` (now justified — it's a published package). Sections: install, 30-second example, spec reference, prompt link, custom components.
- [ ] **35.** Add `LICENSE` (MIT).
- [ ] **36.** Add `examples/` dir with 5–10 worked specs covering each component.

## Phase 10 — Distribution interfaces

Each interface is a thin wrapper over `render()`. Don't duplicate logic.

- [ ] **37.** **Claude Skill.** Create `skill/SKILL.md` describing what it does and when to invoke. Skill body shells out to `python -m diagrammer`. Verify: install locally, ask Claude to draw something, SVG appears.
- [ ] **38.** **MCP server.** `mcp_server.py` using the official Python MCP SDK. Exposes one tool: `render_diagram(spec) -> svg_string`. Verify: configure in Claude Desktop, ask for a diagram, server returns SVG.
- [ ] **39.** **Custom CLI front-end** (interactive). `diagrammer chat`: REPL that pipes user prompts to a configured LLM, parses the JSON reply, renders, opens in default viewer. Verify: type "draw a 3-layer transformer," see SVG open.
- [ ] **40.** **Web playground (optional).** Single HTML page using Pyodide so the same Python code runs client-side. Textarea for spec, live SVG preview. No backend. Verify: `open playground.html`, edit spec, see live updates.

## Phase 11 — Publish

- [ ] **41.** Push to GitHub. CI: GitHub Action runs `python -m unittest` on push.
- [ ] **42.** `pip install build twine`; build wheel + sdist; `twine upload` to PyPI. Verify: fresh machine `pipx install diagrammer` works.
- [ ] **43.** Tag `v0.1.0`, draft GitHub release with changelog.
- [ ] **44.** Submit Skill to Anthropic's Skill registry (if/when public). Submit MCP server to the MCP registry.
- [ ] **45.** Write the launch blog post — *use the tool itself for every diagram in the post.* Verify: post ships with embedded SVGs from the library, end-to-end loop proven on a real workload.

## Phase 12 — Beyond

Whatever comes from real use. Likely candidates:
- Animation (SVG `<animate>` for step-through diagrams)
- Export to PNG/PDF via headless tooling
- VS Code extension with live preview
- Figma plugin export (probably not — defeats the point)

Don't build these speculatively. Wait until a blog post needs them.

---

## Definition of done (v1.0)

The end state, in one sentence: *I can describe a diagram in plain English to an LLM, get a valid JSON spec, run one command, and drop a clean SVG into a blog post — and so can anyone else who installs the package.*
