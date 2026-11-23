---
this_file: CHANGELOG.md
---

# Changelog

## 0.1.0 — 2026-11-23

- Extracted margin-figure grouping from the Fly documentation theme as
  `group_figures()`, with configurable figure classes, wrapper classes and
  a CSS custom property for the paragraph count.
- Added the `vexy_figure_groups` Python-Markdown extension for figures available
  in the renderer's final HTML.
- Match whole class tokens for both grouping and cut figures. Track nesting
  in one pass and reuse compiled patterns across calls with the same options.
- Included `py.typed` in the package. Added CI for Python 3.12–3.14 and a
  tag-triggered PyPI release workflow.
- Captured 28 HTML examples from the original Fly implementation to test
  output bytes and idempotence without a theme checkout.
