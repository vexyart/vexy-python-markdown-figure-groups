---
this_file: README.md
---

# vexy-python-markdown-figure-groups

Place a figure beside the paragraphs it illustrates. The package wraps the figure
and its text in one HTML block and gives your stylesheet a paragraph count.

## Install

Requires Python 3.12 or later. From this checkout, run the following command in
the environment used to render your site.

```sh
uv pip install .
```

## Before and after

Put the figure immediately after the paragraph it illustrates. Use a double-quoted
`class` attribute on the figure.

```html
<p>The crossbar sits below the centre of the A.</p>
<figure class="img-small"><img src="a.svg" alt="A with a low crossbar"></figure>
<p>This leaves room for the counter above.</p>
```

The two paragraphs give the figure two grid rows to span.

```html
<div class="figure-group" style="--rows: 2"><p>The crossbar sits below the centre of the A.</p>
<figure class="img-small"><img src="a.svg" alt="A with a low crossbar"></figure>
<p>This leaves room for the counter above.</p></div>
```

Consecutive paragraphs join the group until another block intervenes or a
paragraph has a figure of its own. A figure immediately after a heading groups
with the paragraphs that follow it. A cut figure moves ahead of its paragraph
so text can wrap around a float.

Grouping applies to top-level article content. It skips lists, divs, details,
blockquotes, tables and nested figures. It preserves comments and the contents
of `script`, `style`, `pre` and `textarea`. Running it twice keeps a single wrapper.

## Use with Python-Markdown

Enable the `figure_groups` extension to group figures in Markdown's final HTML,
after the renderer restores raw HTML blocks.

```python
import markdown

text = """The crossbar sits below the centre of the A.

<figure class="img-small"><img src="a.svg" alt="A with a low crossbar"></figure>

This leaves room for the counter above."""
html = markdown.markdown(text, extensions=["md_in_html", "attr_list", "figure_groups"])
```

Pass options through `extension_configs`, for example
`extension_configs={"figure_groups": {"group_class": "margin-note"}}`.

## Use with rendered HTML

If a site creates figures after Markdown rendering, call the public
`group_figures()` function from your own plugin after the figures exist.
For example, a MkDocs plugin that creates figures in `on_page_content` can
return `group_figures(html)` at the end of that hook.

```python
from vexy_markdown_figure_groups import group_figures

html = '<p>Check the crossbar.</p><figure class="img-cut"><img src="a.svg" alt="A"></figure>'
grouped = group_figures(html, group_class="fly-aside", cut_class="fly-cut")
```

## Options

The extension and the function accept the same options. Pass the function's
options by keyword. Use lists or tuples for class collections and literal CSS
identifiers for class names. Invalid names raise `ValueError`.

| Option | Default | Meaning |
| --- | --- | --- |
| `figure_classes` | `("img-small", "img-tall", "img-cut")` | Figure classes eligible for grouping. |
| `cut_classes` | `("img-cut",)` | Classes that move an eligible figure ahead of its paragraph. |
| `group_class` | `"figure-group"` | Class added to every wrapper. |
| `cut_class` | `"figure-group-cut"` | Additional wrapper class for cut figures. |
| `rows_property` | `"--rows"` | CSS custom property holding the paragraph count. Its name starts with `--`. |

## Layout

On wide screens, give the figure a margin column spanning the paragraph rows.
Cut figures can float into the text instead.

```css
@media (min-width: 48rem) {
  .figure-group {
    display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 16rem); column-gap: 2rem;
  }
  .figure-group > p { grid-column: 1; }
  .figure-group > figure { grid-column: 2; grid-row: 1 / span var(--rows); margin: 0; }
  .figure-group img { max-width: 100%; height: auto; }
  .figure-group-cut { display: flow-root; }
  .figure-group-cut > figure { float: right; width: 35%; margin: 0 0 1rem 1.5rem; }
}
```

Licensed under Apache-2.0.
