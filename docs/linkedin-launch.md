# LinkedIn Launch Draft

Image: `docs/img/launch.png`

Post:

I built `diagrammer`: a Claude Code skill for making quick technical diagrams.

Install it, ask Claude for a diagram, and it gives you a clean SVG you can drop into a README, blog post, design doc, or PR.

Examples:
- "draw a request flow from browser to API to Postgres"
- "diagram this system architecture"
- "make a simple transformer block diagram"

Under the hood, the skill writes a small JSON spec and renders it with a tiny Python CLI. No design tool, no dragging boxes around, no heavyweight diagramming app.

Install:
`pipx install diagrammer`
`/plugin marketplace add Anish-Reddy-K/diagrammer`
`/plugin install diagrammer@diagrammer-tools`

The image below was generated with `diagrammer`.

GitHub: https://github.com/Anish-Reddy-K/diagrammer
