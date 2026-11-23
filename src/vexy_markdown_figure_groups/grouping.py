# this_file: src/vexy_markdown_figure_groups/grouping.py
"""Group margin figures in rendered article HTML while preserving the original markup."""

import re
from collections.abc import Sequence

DEFAULT_FIGURE_CLASSES = ("img-small", "img-tall", "img-cut")
DEFAULT_CUT_CLASSES = ("img-cut",)

_IDENTIFIER = re.compile(r"(?:--|-?(?:[A-Za-z_]|[^\x00-\x7f]))(?:[A-Za-z0-9_-]|[^\x00-\x7f])*")
_ATTRS = r"""(?:[^>"']|"[^"]*"|'[^']*')*"""
_OPAQUE = re.compile(r"<!--.*?-->|<(script|style|pre|textarea)\b.*?</\1\s*>", re.I | re.S)
_NESTING = re.compile(
    rf"<(/?)(li|ul|ol|dl|div|details|blockquote|table|figure)(?=[\s>/])({_ATTRS})>", re.I
)
_PARA = r"<p\b[^>]*>(?:(?!</p>).)*</p>"
_FIGURE_CLASS = r'<figure\b[^>]*\bclass="[^"]*'


def _identifier(name: str, option: str) -> str:
    if not isinstance(name, str) or not _IDENTIFIER.fullmatch(name):
        raise ValueError(f"{option} requires a literal CSS identifier, got {name!r}")
    return name


def _class_pattern(names: Sequence[str], option: str) -> str:
    if not isinstance(names, Sequence) or isinstance(names, (str, bytes, bytearray)):
        raise ValueError(f"{option} requires a sequence of CSS class names")
    alternatives = []
    for name in names:
        literal = re.escape(_identifier(name, option))
        # Keep the theme's word-boundary matching for its original class names.
        if name in DEFAULT_FIGURE_CLASSES:
            alternatives.append(rf"\b{literal}\b")
        else:
            alternatives.append(rf'(?<=[" \t\n\f\r]){literal}(?=[" \t\n\f\r])')
    return "(?:" + "|".join(alternatives) + ")" if alternatives else "(?!)"


def _depth_at(masked: str, end: int) -> int:
    """Count open containers before a match, excluding self-closing tags."""
    return sum(
        -1 if tag[1] else 1 for tag in _NESTING.finditer(masked, 0, end) if not tag[3].endswith("/")
    )


def group_figures(
    html: str,
    *,
    figure_classes: Sequence[str] = DEFAULT_FIGURE_CLASSES,
    cut_classes: Sequence[str] = DEFAULT_CUT_CLASSES,
    group_class: str = "figure-group",
    cut_class: str = "figure-group-cut",
    rows_property: str = "--rows",
) -> str:
    """Wrap top-level margin figures with adjacent paragraphs and count their rows.

    Start with the figure's preceding paragraph, or with the figure itself after a
    heading. Stop at the next non-paragraph or paragraph with its own figure. Cut
    figures move before their paragraph so text can flow around a floated figure.
    """
    selected = _class_pattern(figure_classes, "figure_classes")
    cut = re.compile(_FIGURE_CLASS + _class_pattern(cut_classes, "cut_classes"), re.I)
    _identifier(group_class, "group_class")
    _identifier(cut_class, "cut_class")
    if not _identifier(rows_property, "rows_property").startswith("--") or len(rows_property) == 2:
        raise ValueError("rows_property requires a custom property name starting with '--'")

    figure = rf'{_FIGURE_CLASS}{selected}[^"]*"[^>]*>.*?</figure>'
    following = rf"((?:\s*{_PARA}(?!\s*{figure}))*)"
    groups = re.compile(
        rf"({_PARA})(\s*)({figure}){following}"
        rf"|(?<=</h[1-6]>)(\s*)({figure})(?=\s*<p\b){following}",
        re.I | re.S,
    )

    masked = _OPAQUE.sub(lambda m: " " * len(m[0]), html)
    parts: list[str] = []
    last = 0
    for match in groups.finditer(masked):
        paragraph, gap, after_paragraph, tail, leading, after_heading, rest = match.groups()
        fig = after_paragraph or after_heading
        if (
            html[match.start() : match.end()] != match[0]
            or _depth_at(masked, match.start())
            or len(re.findall(r"<figure\b", fig, re.I)) != 1
        ):
            continue
        is_cut = cut.match(fig)
        cls = f"{group_class} {cut_class}" if is_cut else group_class
        if paragraph is None:
            rows = len(re.findall(r"<p\b", rest, re.I))
            inner = fig + rest
        else:
            rows = 1 + len(re.findall(r"<p\b", tail, re.I))
            inner = (fig + gap + paragraph if is_cut else paragraph + gap + fig) + tail
        parts.extend((html[last : match.start()], leading or ""))
        parts.append(f'<div class="{cls}" style="{rows_property}: {rows}">{inner}</div>')
        last = match.end()
    return "".join(parts) + html[last:]
