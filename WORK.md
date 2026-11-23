---
this_file: WORK.md
---

# 0.1.0 release checks

On 2026-11-23 the baseline had 40 passing tests and 28 failures because the
current Fly checkout had removed `group_margin_figures()`. The parent of its
removal commit, `29f882097424964e79c5429848c2764c3962cb57`, supplied the 28
golden outputs. All matched the package byte for byte with the Fly class names
and stayed identical on a second pass. Fly's current plugin calls
`group_figures()` directly.

The timing test groups 1,000 top-level figures and leaves 1,000 nested figures
in place. On the same machine it took 1.87 seconds before the change and
0.0067 seconds afterward. The 8,000-group workload took 0.0505 seconds.

- The editable install passed all 53 tests on Python 3.13.18.
- Fresh wheel installations passed all 53 tests on each of Python 3.12.12,
  3.13.18 and 3.14.10, including Markdown discovery by the new name.
- Ruff lint and formatting, strict mypy and actionlint passed.
- `uv build` produced a source distribution and built the wheel from it.
  Both passed `twine check --strict`. Archive inspection confirmed the typed
  marker and generated version module in both, and all seven classifiers and
  the renamed entry point in wheel metadata.

Hatch derives the release version from Git. These checks used the untagged
development build. The first tagged build, PyPI upload and trusted publisher
registration remain release-owner steps documented in the README.
