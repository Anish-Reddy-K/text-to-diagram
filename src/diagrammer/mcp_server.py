from mcp.server.fastmcp import FastMCP

from diagrammer import render

mcp = FastMCP("diagrammer")


@mcp.tool()
def render_diagram(spec: dict) -> str:
    """Render a diagrammer JSON spec to an SVG string.

    The spec format mirrors the CLI: top-level `nodes` and `edges`, plus
    optional `direction`, `router`, `col_gap`, `row_gap`, `margin`, `defs`.
    Built-in node types: box, circle, text, database, stack, group, note,
    custom. See `diagrammer prompt` for the full reference and examples.
    """
    return render(spec)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
