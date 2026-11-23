# this_file: tests/test_grouping.py
"""Golden HTML examples remain runnable without the theme checkout."""

from time import perf_counter

import pytest

from vexy_markdown_figure_groups import group_figures

SMALL = '<figure class="img-small"><img/></figure>'
TALL = '<figure class="img-tall"><img/></figure>'
CUT = '<figure class="img-cut"><img/></figure>'
IMAGE = '<figure class="img-small"><img src="s.png"/></figure>'
A = "<p>a</p>"
B = "<p>b</p>"
C = "<p>c</p>"
D = "<p>d</p>"
DEPTH_PREFIX = '<div data-x="a/>"><!-- <div> </li> --><script>"</div>"</script><p>'


# Expected HTML from group_margin_figures in fontlab-www-docstheme.fly,
# commit 29f882097424964e79c5429848c2764c3962cb57, theme/fly_january/markup.py.
# Each tuple is (description, original HTML, expected HTML). None means byte-for-byte unchanged.
CASES = [
    (
        "small figure after inline markup",
        f"{A}\n<p>b <em>x</em></p>\n{IMAGE}\n<h2>H</h2>",
        '<p>a</p>\n<div class="fly-aside" style="--rows: 1"><p>b <em>x</em></p>\n'
        '<figure class="img-small"><img src="s.png"/></figure></div>\n<h2>H</h2>',
    ),
    (
        "following paragraphs count as rows",
        f"{A}{TALL}\n{B}\n{C}<ul><li>x</li></ul>",
        '<div class="fly-aside" style="--rows: 3"><p>a</p><figure class="img-tall"><img/>'
        "</figure>\n<p>b</p>\n<p>c</p></div><ul><li>x</li></ul>",
    ),
    ("wide figure", f'{B}<figure class="img-wide"><img/></figure>', None),
    ("heading without a following paragraph", f"<h3>H</h3>{SMALL}", None),
    (
        "paragraph with its own figure",
        f"{A}{SMALL}{B}{C}{TALL}{D}",
        '<div class="fly-aside" style="--rows: 2"><p>a</p><figure class="img-small"><img/>'
        '</figure><p>b</p></div><div class="fly-aside" style="--rows: 2"><p>c</p>'
        '<figure class="img-tall"><img/></figure><p>d</p></div>',
    ),
    ("list item", f"<ul><li>{A}{SMALL}{B}</li></ul>", None),
    ("admonition", f'<div class="admonition note">{A}{SMALL}</div>', None),
    ("details", f"<details><summary>s</summary>{A}{SMALL}</details>", None),
    (
        "paragraph after a closed list",
        f"<ul><li>x</li></ul>{A}{SMALL}",
        '<ul><li>x</li></ul><div class="fly-aside" style="--rows: 1"><p>a</p>'
        '<figure class="img-small"><img/></figure></div>',
    ),
    (
        "heading followed by figure and paragraphs",
        f"<h3>H</h3>\n{TALL}\n{A}\n{B}<h3>I</h3>",
        '<h3>H</h3>\n<div class="fly-aside" style="--rows: 2"><figure class="img-tall">'
        "<img/></figure>\n<p>a</p>\n<p>b</p></div><h3>I</h3>",
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
    (
        "closing div in comment",
        f'<div class="admonition"><!-- </div> -->{A}{SMALL}</div>',
        None,
    ),
    (
        "cut moves before its paragraph",
        f"{A}\n{CUT}\n{B}\n<h2>H</h2>",
        '<div class="fly-aside fly-cut" style="--rows: 2"><figure class="img-cut"><img/>'
        "</figure>\n<p>a</p>\n<p>b</p></div>\n<h2>H</h2>",
    ),
    (
        "cut after heading",
        f"<h3>H</h3>\n{CUT}\n{B}",
        '<h3>H</h3>\n<div class="fly-aside fly-cut" style="--rows: 1">'
        '<figure class="img-cut"><img/></figure>\n<p>b</p></div>',
    ),
    ("depth prefix", DEPTH_PREFIX, None),
    *(
        (tag, f"<{tag}>{A}{SMALL}</{tag}>", None)
        for tag in ("script", "style", "textarea", "ol", "dl", "blockquote")
    ),
    ("opaque content between blocks", f"{A}<!-- intervening comment -->{SMALL}", None),
    (
        "depth through quoted attributes and opaque regions",
        f"{DEPTH_PREFIX}nested</p>{SMALL}</div>{B}{SMALL}",
        '<div data-x="a/>"><!-- <div> </li> --><script>"</div>"</script><p>nested</p>'
        '<figure class="img-small"><img/></figure></div>'
        '<div class="fly-aside" style="--rows: 1"><p>b</p><figure class="img-small"><img/>'
        "</figure></div>",
    ),
    (
        "mixed-case HTML and multiple classes",
        '<P>a</P>\t<FIGURE CLASS="photo IMG-CUT lead">x</FIGURE>',
        '<div class="fly-aside fly-cut" style="--rows: 1">'
        '<FIGURE CLASS="photo IMG-CUT lead">x</FIGURE>\t<P>a</P></div>',
    ),
]

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
    assert first.encode() == (html if expected is None else expected).encode()
    assert group_figures(first, **THEME_OPTIONS) == first


def test_group_figures_when_using_defaults_then_emits_default_classes() -> None:
    assert group_figures(A + CUT) == (
        f'<div class="figure-group figure-group-cut" style="--rows: 1">{CUT}{A}</div>'
    )
    assert group_figures(A + SMALL) == (
        f'<div class="figure-group" style="--rows: 1">{A}{SMALL}</div>'
    )


@pytest.mark.parametrize(
    "attrs",
    [
        'class="not-img-small"',
        'class="img-small-x"',
        'class="img-tall.other"',
        'data-class="img-small" class="photo"',
        """class="photo" title='uses class="img-small"'""",
    ],
)
def test_group_figures_when_class_token_is_absent_then_preserves_html(attrs: str) -> None:
    html = f"{A}<figure {attrs}>Map</figure>"
    assert group_figures(html) == html


@pytest.mark.parametrize(
    "classes", ["img-cut photo lead", "photo\timg-cut\nlead", "lead photo img-cut"]
)
def test_group_figures_when_cut_class_occurs_anywhere_then_moves_figure(classes: str) -> None:
    fig = f'<figure class="{classes}">Map</figure>'
    assert group_figures(A + fig) == (
        f'<div class="figure-group figure-group-cut" style="--rows: 1">{fig}{A}</div>'
    )


def test_group_figures_when_cut_class_is_partial_then_keeps_order() -> None:
    html = f'{A}<figure class="not-img-cut img-small img-cut-x">Map</figure>'
    assert group_figures(html) == f'<div class="figure-group" style="--rows: 1">{html}</div>'


def test_group_figures_when_class_list_changes_then_uses_current_options() -> None:
    html = A + SMALL
    classes = ["img-small"]
    assert group_figures(html, figure_classes=classes) == group_figures(html)
    classes[0] = "small"
    assert group_figures(html, figure_classes=classes) == html


def test_group_figures_when_grouping_a_thousand_figures_then_finishes_within_a_second() -> None:
    separator = f"<blockquote>{A}{SMALL}</blockquote>"
    html = (A + SMALL + separator) * 1000
    start = perf_counter()
    grouped = group_figures(html)
    elapsed = perf_counter() - start
    assert (
        grouped
        == (f'<div class="figure-group" style="--rows: 1">{A}{SMALL}</div>' + separator) * 1000
    )
    assert elapsed < 1, f"Grouping 1,000 figures took {elapsed:.3f}s"


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
        {"figure_classes": "tiny"},
        {"figure_classes": [["img-small"]]},
        {"cut_classes": ("tiny image",)},
        {"group_class": 'g" onclick="bad'},
        {"cut_class": ""},
        {"rows_property": "--rows; color:red"},
    ],
)
def test_group_figures_when_option_is_invalid_then_raises_value_error(options: dict) -> None:
    with pytest.raises(ValueError):
        group_figures("", **options)
