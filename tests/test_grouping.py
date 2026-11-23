# this_file: tests/test_grouping.py
"""Golden HTML examples remain runnable without the theme checkout."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from vexy_markdown_figure_groups import group_figures

REFERENCE = Path(
    "/Users/adam/Developer/vcs3/github.fontlab/fontlab-www-docstheme.fly/theme/fly_january/markup.py"
)
SMALL = '<figure class="img-small"><img/></figure>'
TALL = '<figure class="img-tall"><img/></figure>'
CUT = '<figure class="img-cut"><img/></figure>'
IMAGE = '<figure class="img-small"><img src="s.png"/></figure>'
A = "<p>a</p>"
B = "<p>b</p>"
C = "<p>c</p>"
D = "<p>d</p>"
DEPTH_PREFIX = '<div data-x="a/>"><!-- <div> </li> --><script>"</div>"</script><p>'


def wrapper(inner: str, rows: int, *, cut: bool = False) -> str:
    cls = "fly-aside fly-cut" if cut else "fly-aside"
    return f'<div class="{cls}" style="--rows: {rows}">{inner}</div>'


# Each tuple is (description, original HTML, expected HTML). None means byte-for-byte unchanged.
REFERENCE_CASES = [
    (
        "small figure after inline markup",
        f"{A}\n<p>b <em>x</em></p>\n{IMAGE}\n<h2>H</h2>",
        A + "\n" + wrapper("<p>b <em>x</em></p>\n" + IMAGE, 1) + "\n<h2>H</h2>",
    ),
    (
        "following paragraphs count as rows",
        f"{A}{TALL}\n{B}\n{C}<ul><li>x</li></ul>",
        wrapper(f"{A}{TALL}\n{B}\n{C}", 3) + "<ul><li>x</li></ul>",
    ),
    ("wide figure", f'{B}<figure class="img-wide"><img/></figure>', None),
    ("heading without a following paragraph", f"<h3>H</h3>{SMALL}", None),
    (
        "paragraph with its own figure",
        f"{A}{SMALL}{B}{C}{TALL}{D}",
        wrapper(f"{A}{SMALL}{B}", 2) + wrapper(f"{C}{TALL}{D}", 2),
    ),
    ("list item", f"<ul><li>{A}{SMALL}{B}</li></ul>", None),
    ("admonition", f'<div class="admonition note">{A}{SMALL}</div>', None),
    ("details", f"<details><summary>s</summary>{A}{SMALL}</details>", None),
    (
        "paragraph after a closed list",
        f"<ul><li>x</li></ul>{A}{SMALL}",
        "<ul><li>x</li></ul>" + wrapper(A + SMALL, 1),
    ),
    (
        "heading followed by figure and paragraphs",
        f"<h3>H</h3>\n{TALL}\n{A}\n{B}<h3>I</h3>",
        "<h3>H</h3>\n" + wrapper(f"{TALL}\n{A}\n{B}", 2) + "<h3>I</h3>",
    ),
    (
        "outer figure containing a figure",
        f'{A}<figure class="img-small"><figure><img/></figure><figcaption>c</figcaption></figure>',
        None,
    ),
    ("paragraph inside a figure", f"<figure>{A}{SMALL}</figure>", None),
    ("table", f"<table><tr><td>{A}{SMALL}</td></tr></table>", None),
    ("comment", f"<!-- {A}{SMALL} -->", None),
    ("pre", f"<pre>{A}{SMALL}</pre>", None),
    ("closing div in comment", f'<div class="admonition"><!-- </div> -->{A}{SMALL}</div>', None),
    (
        "cut moves before its paragraph",
        f"{A}\n{CUT}\n{B}\n<h2>H</h2>",
        wrapper(f"{CUT}\n{A}\n{B}", 2, cut=True) + "\n<h2>H</h2>",
    ),
    (
        "cut after heading",
        f"<h3>H</h3>\n{CUT}\n{B}",
        "<h3>H</h3>\n" + wrapper(f"{CUT}\n{B}", 1, cut=True),
    ),
    ("depth prefix", DEPTH_PREFIX, None),
]

EXTRA_CASES = [
    (tag, f"<{tag}>{A}{SMALL}</{tag}>", None)
    for tag in ("script", "style", "textarea", "ol", "dl", "blockquote")
] + [
    ("opaque content between blocks", f"{A}<!-- intervening comment -->{SMALL}", None),
    (
        "depth through quoted attributes and opaque regions",
        f"{DEPTH_PREFIX}nested</p>{SMALL}</div>{B}{SMALL}",
        f"{DEPTH_PREFIX}nested</p>{SMALL}</div>" + wrapper(B + SMALL, 1),
    ),
    (
        "mixed-case HTML and multiple classes",
        '<P>a</P>\t<FIGURE CLASS="photo IMG-CUT lead">x</FIGURE>',
        wrapper('<FIGURE CLASS="photo IMG-CUT lead">x</FIGURE>\t<P>a</P>', 1, cut=True),
    ),
]

CASES = REFERENCE_CASES + EXTRA_CASES
THEME_OPTIONS = {
    "figure_classes": ("img-small", "img-tall", "img-cut"),
    "cut_classes": ("img-cut",),
    "group_class": "fly-aside",
    "cut_class": "fly-cut",
}


@pytest.mark.parametrize("html,expected", [(h, e) for _, h, e in CASES], ids=[c[0] for c in CASES])
def test_group_figures_when_given_article_blocks_then_preserves_or_groups_them(
    html: str, expected: str | None
) -> None:
    first = group_figures(html, **THEME_OPTIONS)
    assert first == (html if expected is None else expected)
    assert group_figures(first, **THEME_OPTIONS) == first


@pytest.fixture(scope="module")
def reference() -> ModuleType:
    if not REFERENCE.is_file():
        pytest.skip(f"Theme reference module is absent: {REFERENCE}")
    spec = importlib.util.spec_from_file_location("theme_reference_markup", REFERENCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(sys, "dont_write_bytecode", True)
        spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("html", [c[1] for c in CASES], ids=[c[0] for c in CASES])
def test_group_figures_when_using_theme_classes_then_matches_reference_bytes(
    html: str, reference: ModuleType
) -> None:
    assert (
        group_figures(html, **THEME_OPTIONS).encode()
        == reference.group_margin_figures(html).encode()
    )


def test_group_figures_when_using_defaults_then_emits_default_classes() -> None:
    assert group_figures(A + CUT) == (
        f'<div class="figure-group figure-group-cut" style="--rows: 1">{CUT}{A}</div>'
    )
    assert group_figures(A + SMALL) == (
        f'<div class="figure-group" style="--rows: 1">{A}{SMALL}</div>'
    )


def test_group_figures_when_class_has_nonbreaking_space_then_matches_whole_token() -> None:
    name = "map\u00a0side"
    html = f'{A}<figure class="{name}">Map</figure>'
    assert group_figures(html, figure_classes=("side",)) == html
    assert group_figures(html, figure_classes=(name,)) == (
        f'<div class="figure-group" style="--rows: 1">{html}</div>'
    )


def test_group_figures_when_classes_are_empty_then_disables_requested_rule() -> None:
    assert group_figures(A + SMALL, figure_classes=()) == A + SMALL
    assert group_figures(A + CUT, cut_classes=()) == (
        f'<div class="figure-group" style="--rows: 1">{A}{CUT}</div>'
    )


@pytest.mark.parametrize(
    "options",
    [
        {"figure_classes": ("img-small", "x|y")},
        {"figure_classes": ("9bad",)},
        {"cut_classes": ("tiny image",)},
        {"group_class": 'g" onclick="bad'},
        {"cut_class": ""},
        {"rows_property": "--rows; color:red"},
    ],
)
def test_group_figures_when_option_is_invalid_then_raises_value_error(options: dict) -> None:
    with pytest.raises(ValueError):
        group_figures("", **options)
