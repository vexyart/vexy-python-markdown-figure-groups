# this_file: src/vexy_markdown_figure_groups/grouping.py
"""Group margin figures in rendered article HTML while preserving the original markup."""

import re
from collections.abc import Sequence
from functools import lru_cache

DEFAULT_FIGURE_CLASSES = ("img-small", "img-tall", "img-cut")
DEFAULT_CUT_CLASSES = ("img-cut",)

_IDENTIFIER = re.compile(r"(?:--|-?(?:[A-Za-z_]|[^\x00-\x7f]))(?:[A-Za-z0-9_-]|[^\x00-\x7f])*")
_ATTRS = r"""(?:[^>"']|"[^"]*"|'[^']*')*"""
_OPAQUE = re.compile(r"<!--.*?-->|<(script|style|pre|textarea)\b.*?</\1\s*>", re.I | re.S)
_NESTING = re.compile(
    rf"<(/?)(li|ul|ol|dl|div|details|blockquote|table|figure)(?=[\s>/])({_ATTRS})>", re.I
)
_PARA = r"<p\b[^>]*>(?:(?!</p>).)*</p>"
_SPACE = r" \t\n\f\r"
_FIGURE_CLASS = rf'<figure(?=[{_SPACE}]){_ATTRS}[{_SPACE}]class="[^"]*'
_FIGURE_START = re.compile(r"<figure\b", re.I)
_PARA_START = re.compile(r"<p\b", re.I)


def _identifier(name: str, option: str) -> str:
    if not isinstance(name, str) or not _IDENTIFIER.fullmatch(name):
        raise ValueError(f"{option} requires a literal CSS identifier, got {name!r}")
    return name


def _class_names(names: Sequence[str], option: str) -> tuple[str, ...]:
    if not isinstance(names, Sequence) or isinstance(names, (str, bytes, bytearray)):
        raise ValueError(f"{option} requires a sequence of CSS class names")
    return tuple(names)


def _class_pattern(names: tuple[str, ...], option: str) -> str:
    if not names:
        return "(?!)"
    choices = "|".join(re.escape(_identifier(name, option)) for name in names)
    return rf'(?<=["{_SPACE}])(?:{choices})(?=["{_SPACE}])'


@lru_cache
def _patterns(
    figure_classes: tuple[str, ...],
    cut_classes: tuple[str, ...],
    group_class: str,
    cut_class: str,
    rows_property: str,
) -> tuple[re.Pattern[str], re.Pattern[str]]:
    selected = _class_pattern(figure_classes, "figure_classes")
    cut = re.compile(_FIGURE_CLASS + _class_pattern(cut_classes, "cut_classes"), re.I)
    _identifier(group_class, "group_class")
    _identifier(cut_class, "cut_class")
    if not _identifier(rows_property, "rows_property").startswith("--") or len(rows_property) == 2:
        raise ValueError("rows_property requires a custom property name starting with '--'")

    figure = rf'{_FIGURE_CLASS}{selected}[^"]*"{_ATTRS}>.*?</figure>'
    following = rf"((?:\s*{_PARA}(?!\s*{figure}))*)"
    groups = re.compile(
        rf"({_PARA})(\s*)({figure}){following}"
        rf"|(?<=</h[1-6]>)(\s*)({figure})(?=\s*<p\b){following}",
        re.I | re.S,
    )
    return groups, cut


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
    try:
        groups, cut = _patterns(
            _class_names(figure_classes, "figure_classes"),
            _class_names(cut_classes, "cut_classes"),
            group_class,
            cut_class,
            rows_property,
        )
    except TypeError as exc:
        # Unhashable option values cannot enter the configuration cache.
        raise ValueError("class names and rows_property must be strings") from exc

    masked = _OPAQUE.sub(lambda m: " " * len(m[0]), html)
    parts: list[str] = []
    containers = _NESTING.finditer(masked)
    tag = next(containers, None)
    depth = 0
    last = 0
    for match in groups.finditer(masked):
        while tag is not None and tag.end() <= match.start():
            if not tag[3].endswith("/"):
                depth += -1 if tag[1] else 1
            tag = next(containers, None)
        paragraph, gap, after_paragraph, tail, leading, after_heading, rest = match.groups()
        fig = after_paragraph or after_heading
        if (
            html[match.start() : match.end()] != match[0]
            or depth
            or len(_FIGURE_START.findall(fig)) != 1
        ):
            continue
        is_cut = cut.match(fig)
        cls = f"{group_class} {cut_class}" if is_cut else group_class
        if paragraph is None:
            rows = len(_PARA_START.findall(rest))
            inner = fig + rest
        else:
            rows = 1 + len(_PARA_START.findall(tail))
            inner = (fig + gap + paragraph if is_cut else paragraph + gap + fig) + tail
        parts.extend((html[last : match.start()], leading or ""))
        parts.append(f'<div class="{cls}" style="{rows_property}: {rows}">{inner}</div>')
        last = match.end()
    return "".join(parts) + html[last:]
