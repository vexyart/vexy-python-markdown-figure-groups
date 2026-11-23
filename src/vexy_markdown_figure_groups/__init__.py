# this_file: src/vexy_markdown_figure_groups/__init__.py
"""Group a margin figure with its paragraphs in rendered HTML."""

from .extension import FigureGroupsExtension, makeExtension
from .grouping import group_figures

__all__ = ["FigureGroupsExtension", "__version__", "group_figures", "makeExtension"]

try:
    from .__version__ import __version__ as __version__
except ImportError:
    __version__ = "0.0.0"
