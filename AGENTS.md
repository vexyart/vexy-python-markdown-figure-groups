---
this_file: AGENTS.md
---

# Development

The package lives in `src/vexy_markdown_figure_groups/`. Keep the grouping
rules in `group_figures()` so the Markdown postprocessor and callers with
rendered HTML produce the same result.

Run from the project root on Python 3.13.

```sh
uv venv --python 3.13
uv pip install -e ".[dev]"
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv build
```

The tests cover grouping, option validation and the installed Markdown entry
point. The parity tests also compare output with the original Fly theme when
its checkout is available. The wheel must include the `figure_groups` entry
point in `markdown.extensions` and the generated `__version__.py`.
