#!/usr/bin/env python3
"""
svg_outline.py

Pretty-print an SVG into a stable, indentation-based outline for diffing.
- Attributes printed under their element, sorted for determinism
- Numeric values formatted to fixed precision (default 4 dp) even inside strings
- points=... parsed into one point per line for polyline/polygon

Usage:
  python svg_outline.py input.svg > input.out
  python svg_outline.py a.svg > a.out
  python svg_outline.py b.svg > b.out
  diff -u a.out b.out

Options:
  --precision 4
  --no-text          (omit element text nodes)
  --no-tail          (omit tail text)

- With Fondest Regards, ChatGPT
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from typing import Iterable, List, Optional, Tuple


# Matches floats/ints including scientific notation.
_NUM_RE = re.compile(
    r"""
    (?<![A-Za-z0-9_])          # not preceded by word-ish char
    [-+]?                      # sign
    (?:
        (?:\d+\.\d*)|          # 12. or 12.34
        (?:\.\d+)|             # .34
        (?:\d+)                # 12
    )
    (?:[eE][-+]?\d+)?          # optional exponent
    (?![A-Za-z0-9_])           # not followed by word-ish char
    """,
    re.VERBOSE,
)
# Matches floats/ints including scientific notation, with optinal units
_NUM_WITH_UNIT_RE = re.compile(
    r"""
    (?<![A-Za-z0-9_])                          # don't start inside an identifier
    (?P<num>[-+]?(?:\d+\.\d*|\.\d+|\d+)
        (?:[eE][-+]?\d+)?)
    (?P<unit>%|[A-Za-z]+)?                     # optional unit suffix (px, em, %, etc.)
    """,
    re.VERBOSE,
)

_WS_RE = re.compile(r"\s+")


def strip_ns(tag: str) -> str:
    """{namespace}local -> local"""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def format_float(x: float, precision: int) -> str:
    return f"{x:.{precision}f}"


def format_numbers_in_string(s: str, precision: int) -> str:
    def repl(m: re.Match) -> str:
        num_txt = m.group("num")
        unit = m.group("unit") or ""
        try:
            val = float(num_txt)
        except ValueError:
            return m.group(0)
        return f"{val:.{precision}f}{unit}"

    return _NUM_WITH_UNIT_RE.sub(repl, s)


def parse_points(points_value: str) -> List[Tuple[float, float]]:
    """
    SVG points grammar is basically: x,y x,y ... with commas optional.
    We'll extract numbers in order and pair them.
    """
    nums = [float(m.group(0)) for m in _NUM_RE.finditer(points_value)]
    pts: List[Tuple[float, float]] = []
    for i in range(0, len(nums) - 1, 2):
        pts.append((nums[i], nums[i + 1]))
    return pts


def norm_space(s: str) -> str:
    return _WS_RE.sub(" ", s.strip())


def parse_style(style_value: str) -> List[Tuple[str, str]]:
    """
    Parse a CSS style attribute into (property, value) pairs.
    Ignores empty entries and preserves order.
    """
    items = []
    for part in style_value.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            k, v = part.split(":", 1)
            items.append((k.strip(), v.strip()))
        else:
            items.append((part.strip(), ""))
    return items


def emit_element(
    el: ET.Element,
    out: List[str],
    indent: int,
    precision: int,
    include_text: bool,
    include_tail: bool,
) -> None:
    ind = "  " * indent
    tag = strip_ns(el.tag)
    out.append(f"{ind}{tag}")

    # Attributes: stable ordering
    attrs = sorted(el.attrib.items(), key=lambda kv: kv[0])

    # Print attributes
    for k, v in attrs:
        k_local = strip_ns(k)
        if k_local == "points":
            out.append(f"{ind}  @points:")
            pts = parse_points(v)
            for (x, y) in pts:
                out.append(f"{ind}    - {format_float(x, precision)}, {format_float(y, precision)}")

        elif k_local == "style":
            out.append(f"{ind}  @style:")
            for sk, sv in sorted(parse_style(v)):
                sv_fmt = format_numbers_in_string(sv, precision)
                sv_fmt = norm_space(sv_fmt)
                out.append(f"{ind}    - {sk}: {sv_fmt}")
        else:
            vv = format_numbers_in_string(v, precision)
            vv = norm_space(vv)
            out.append(f"{ind}  @{k_local}: {vv}")

    # Optional: element text (trimmed)
    if include_text and el.text and el.text.strip():
        txt = norm_space(el.text)
        out.append(f"{ind}  #text: {txt}")

    # Children
    for child in list(el):
        emit_element(child, out, indent + 1, precision, include_text, include_tail)
        if include_tail and child.tail and child.tail.strip():
            tail = norm_space(child.tail)
            out.append(f"{ind}  #tail: {tail}")


def outline_svg(svg_str: str, precision: int, include_text: bool, include_tail: bool) -> str:
    root = ET.fromstring(svg_str)

    out: List[str] = []
    emit_element(root, out, indent=0, precision=precision, include_text=include_text, include_tail=include_tail)
    return "\n".join(out) + "\n"


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Print an SVG as an indented outline for diffing.")
    ap.add_argument("svg", help="Input SVG file")
    ap.add_argument("--precision", type=int, default=4, help="Decimal places for numeric values (default 4)")
    ap.add_argument("--no-text", action="store_true", help="Omit element .text nodes")
    ap.add_argument("--no-tail", action="store_true", help="Omit child .tail text")
    args = ap.parse_args(list(argv) if argv is not None else None)

    sys.stdout.write(
        outline_svg(
            args.svg,
            precision=args.precision,
            include_text=not args.no_text,
            include_tail=not args.no_tail,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
