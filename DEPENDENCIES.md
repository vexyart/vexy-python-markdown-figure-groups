---
this_file: DEPENDENCIES.md
---

# Dependencies

| Dependency | Purpose |
| --- | --- |
| Markdown >=3.5 | Provides the extension and postprocessor API. The HTML grouping function uses the Python standard library. |
| hatchling | Builds the wheel and source distribution. |
| hatch-vcs | Derives the version from Git and writes the version module at build time. |
| pytest | Runs the HTML, Markdown and reference parity tests. |
| pytest-cov | Measures test coverage. |
| ruff | Lints and formats the source and tests. |
| mypy | Checks the package in strict mode. |
| types-Markdown | Supplies Markdown type annotations for mypy. |
