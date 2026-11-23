# this_file: tests/test_extension.py
"""Exercise the installed Python-Markdown entry point with rendered and raw HTML."""

from importlib.metadata import distribution

import markdown

from vexy_markdown_figure_groups import FigureGroupsExtension, group_figures, makeExtension


def test_figure_groups_when_installed_then_extension_is_discoverable() -> None:
    entries = distribution("vexy-python-markdown-figure-groups").entry_points
    (entry,) = entries.select(group="markdown.extensions")
    assert entry.name == "vexy_figure_groups"
    assert isinstance(entry.load()(), FigureGroupsExtension)
    assert isinstance(makeExtension(), FigureGroupsExtension)


def test_figure_groups_when_markdown_restores_raw_figure_then_groups_rendered_paragraphs() -> None:
    figure = '<figure class="img-small">Diagram</figure>'
    source = f"A *line*.\n{{: .lead}}\n\n{figure}\n\nAnother line."
    html = markdown.markdown(source, extensions=["md_in_html", "attr_list", "vexy_figure_groups"])
    assert html.startswith('<div class="figure-group" style="--rows: 2"><p class="lead">')
    assert "<em>line</em>" in html
    assert figure in html
    assert html.endswith("<p>Another line.</p></div>")


def test_figure_groups_when_configured_then_matches_custom_function_options() -> None:
    figure = '<figure class="-inset">Diagram</figure>'
    source = f"Text.\n\n{figure}"
    options = {
        "figure_classes": ["-inset"],
        "cut_classes": ["-inset"],
        "group_class": "_box",
        "cut_class": "cut-2",
        "rows_property": "--line-count",
    }
    expected = f'<div class="_box cut-2" style="--line-count: 1">{figure}\n<p>Text.</p></div>'
    assert group_figures(f"<p>Text.</p>\n{figure}", **options) == expected
    assert (
        markdown.markdown(
            source,
            extensions=["vexy_figure_groups"],
            extension_configs={"vexy_figure_groups": options},
        )
        == expected
    )
