# this_file: src/vexy_markdown_figure_groups/extension.py
"""Run figure grouping after Python-Markdown restores raw HTML."""

from markdown import Markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

from .grouping import DEFAULT_CUT_CLASSES, DEFAULT_FIGURE_CLASSES, group_figures


class _FigureGroupsPostprocessor(Postprocessor):
    def __init__(self, md: Markdown, extension: Extension) -> None:
        super().__init__(md)
        self.extension = extension

    def run(self, text: str) -> str:
        return group_figures(text, **self.extension.getConfigs())


class FigureGroupsExtension(Extension):
    """Group figures in the final HTML using the options accepted by group_figures."""

    def __init__(self, **kwargs: object) -> None:
        self.config = {
            "figure_classes": [DEFAULT_FIGURE_CLASSES, "Classes that identify margin figures."],
            "cut_classes": [DEFAULT_CUT_CLASSES, "Classes that move a figure ahead of its text."],
            "group_class": ["figure-group", "Class for each group wrapper."],
            "cut_class": ["figure-group-cut", "Additional wrapper class for cut figures."],
            "rows_property": ["--rows", "CSS custom property holding the paragraph count."],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.postprocessors.register(_FigureGroupsPostprocessor(md, self), "vexy_figure_groups", -100)


def makeExtension(**kwargs: object) -> FigureGroupsExtension:
    """Create an extension instance for Python-Markdown."""
    return FigureGroupsExtension(**kwargs)
