---
this_file: AGENTS.md
---

# Development

The package lives in `src/vexy_markdown_figure_groups/`. Keep the grouping
rules in `group_figures()` so the Markdown postprocessor and callers with
rendered HTML produce the same result.

Run from the project root on Python 3.13.

```sh
uv sync --all-extras --python 3.13
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv build
```

The tests cover grouping, option validation and the installed Markdown entry
point. The parity tests compare output with golden HTML from the original Fly
theme. The wheel must include the `vexy_figure_groups` entry point in
`markdown.extensions`, the generated `__version__.py` and the `py.typed` marker.
