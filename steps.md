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

**Current state.** Phases 0–4 (steps 1–20) are done. `diagrammer.py` exports `render(spec)` and `register_component(name, fn, default_w, default_h)`. Built-in node types: `box`, `circle`, `text`, `database`, `stack`, `group`, `note`, `custom`. Edges support labels (with auto-widened column gaps for breathing room), `style` (dashed/solid), `weight` (thin/thick), self-loops, and `router: "ortho"` for right-angle bends. Layout supports `direction` (LR/TB), per-spec `col_gap`/`row_gap`/`margin`, vertical centering of columns, and a 30%-from-source bend bias for ortho. Spec accepts a top-level `defs` string for shared SVG defs (gradients, custom markers, filters) referenced from `custom` nodes. Edges are drawn behind nodes so stacks visually emerge from behind their back layers. CLI reads JSON from a path or stdin.

**Layout.**
```
diagrammer.py        # the library + CLI entry point
CLAUDE.md            # behavioral guidelines
steps.md             # this file
test_registry.py     # demo of register_component (Python API)
examples/            # JSON specs the CLI reads (mlp, ortho, transformer, grouped, note, custom, defs, …)
scratch/             # early phase-0 verification scripts (test1–4); kept for reference
```

To run an example: `python3 diagrammer.py examples/mlp.json > out.svg && open out.svg`.

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

## Phase 5 — LLM workflow

- [x] **21.** `validate(spec)` and wire into `render`: check required keys, edge endpoints exist, no duplicate ids; on invalid spec raise with all errors at once. Verify: spec missing `nodes[0].type` and with a dangling edge reports both.
- [ ] **22.** Write `prompt.md` — one-page snippet teaching the spec format, with 3 worked examples (flow, MLP, system architecture) and a section on the `custom` escape hatch. Verify: paste into a fresh Claude/GPT, ask for a diagram, get valid JSON; ask for an unsupported shape, get a `custom` node.
- [ ] **23.** Add a `prompt` subcommand: `python diagrammer.py prompt` prints `prompt.md` to stdout. Verify: output matches the file.

## Phase 6 — Tests

- [ ] **24.** Set up `tests/` with `unittest` (stdlib). One snapshot per built-in component (box, circle, text, database, stack, group, note, custom) comparing rendered SVG to a checked-in `.svg` file. Verify: `python -m unittest` passes; regressions in any component break a single test.

## Phase 7 — Packaging

- [ ] **25.** Move `diagrammer.py` into `src/diagrammer/__init__.py`. Add `pyproject.toml` with `[project.scripts] diagrammer = "diagrammer:cli"`. Verify: `pip install -e .` then `diagrammer mlp.json > out.svg` works from any directory.
- [ ] **26.** Add `README.md`: install, 30-second example, spec reference, prompt link, custom components.
- [ ] **27.** Add `LICENSE` (MIT).

## Phase 8 — Distribution

Each interface is a thin wrapper over `render()`. Don't duplicate logic.

- [ ] **28.** **Claude Skill.** Create `skill/SKILL.md` describing what it does and when to invoke. Skill body shells out to `python -m diagrammer`. Verify: install locally, ask Claude to draw something, SVG appears.
- [ ] **29.** **MCP server.** `mcp_server.py` using the official Python MCP SDK. Exposes one tool: `render_diagram(spec) -> svg_string`. Verify: configure in Claude Desktop, ask for a diagram, server returns SVG.

## Phase 9 — Publish

- [ ] **30.** Push to GitHub. CI: GitHub Action runs `python -m unittest` on push.
- [ ] **31.** Build wheel + sdist; `twine upload` to PyPI; tag `v0.1.0` and draft GitHub release. Verify: fresh machine `pipx install diagrammer` works.
- [ ] **32.** Write the launch blog post — *use the tool itself for every diagram in the post.* Verify: post ships with embedded SVGs from the library, end-to-end loop proven on a real workload.

## Phase 10 — Beyond

Add steps here only when real use demands them. No speculative roadmap.

---

## Definition of done (v1.0)

The end state, in one sentence: *I can describe a diagram in plain English to an LLM, get a valid JSON spec, run one command, and drop a clean SVG into a blog post — and so can anyone else who installs the package.*
