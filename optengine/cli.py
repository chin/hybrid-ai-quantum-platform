import os
import sys
import textwrap
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass


__all__ = [
    "BANNER_WIDTH",
    "Block",
    "banner",
    "blank",
    "block",
    "detail",
    "failure",
    "footer",
    "heading",
    "item",
    "progress",
    "result",
    "section",
    "step",
    "success",
    "tool_block",
    "tool_result",
    "value",
]


BANNER_WIDTH = 72
DETAIL_LABEL_WIDTH = 16

_PASS_GREEN = "\033[32m"
_FAIL_RED = "\033[31m"

_RESET = "\033[0m"
_GREEN = "\033[38;2;118;185;0m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_DIM = "\033[2m"

_BLOCK_VALUE_COLORS = {
    "decision": _YELLOW,
    "artifact": _CYAN,
    "output": _CYAN,
}


@dataclass(frozen=True)
class Block:
    name: str
    value: object
    ok: bool = False


def _color_enabled() -> bool:
    if os.getenv("NO_COLOR") is not None:
        return False

    if os.getenv("FORCE_COLOR") is not None:
        return True

    return sys.stdout.isatty()


def _colorize(message: str, color: str | None) -> str:
    if color is None or not _color_enabled():
        return message

    return f"{color}{message}{_RESET}"


def _block_value_color(name: str) -> str | None:
    short_name = name.rsplit(".", maxsplit=1)[-1]
    return _BLOCK_VALUE_COLORS.get(short_name)


def banner(title: str) -> None:
    line = "━" * BANNER_WIDTH
    print()
    print(line)
    print(_colorize(title.center(BANNER_WIDTH), _GREEN))
    print(line)
    print()


def heading(title: str) -> None:
    """Render a human-readable runtime section heading."""

    print(_colorize(title, _MAGENTA))
    print(_colorize("─" * min(BANNER_WIDTH, max(18, len(title) + 4)), _DIM))


def step(name: str, *, color: str | None = None) -> None:
    print(_colorize(f"> {name}", color), flush=True)


def detail(
    label: str,
    message: object,
    *,
    indent: int = 2,
    color: str | None = None,
) -> None:
    """Render an aligned, terminal-width-aware label/value pair."""

    prefix = " " * indent
    continuation = " " * (indent + DETAIL_LABEL_WIDTH)
    width = max(24, BANNER_WIDTH - indent - DETAIL_LABEL_WIDTH)
    source_lines = str(message).splitlines() or [""]
    lines: list[str] = []
    for source in source_lines:
        lines.extend(
            textwrap.wrap(
                source,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
        )

    first = f"{prefix}{label:<{DETAIL_LABEL_WIDTH}}{lines[0]}"
    print(_colorize(first, color))
    for line in lines[1:]:
        print(_colorize(f"{continuation}{line}", color))


def item(marker: str, message: object, *, indent: int = 2) -> None:
    """Render one compact list entry with aligned wrapped continuation."""

    prefix = " " * indent
    marker_width = 5
    continuation = " " * (indent + marker_width)
    width = max(24, BANNER_WIDTH - indent - marker_width)
    lines = textwrap.wrap(
        str(message),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    print(f"{prefix}{marker:<{marker_width}}{lines[0]}")
    for line in lines[1:]:
        print(f"{continuation}{line}")


def progress(message: str = "Processing ...") -> None:
    """Render a flushed progress marker before synchronous work begins."""

    print(_colorize(f"  … {message}", _CYAN), flush=True)


def result(message: object, *, ok: bool = True) -> None:
    """Render a compact terminal result line."""

    marker = "✓" if ok else "✗"
    color = _PASS_GREEN if ok else _FAIL_RED
    print(_colorize(f"  {marker} {message}", color))


def success(message: str = "complete") -> None:
    print(_colorize(f"✓ {message}", _PASS_GREEN))


def failure(message: str = "failed") -> None:
    print(_colorize(f"✗ {message}", _FAIL_RED))


def value(message: object, *, color: str | None = None) -> None:
    print(_colorize(str(message), color))


def blank() -> None:
    print()


def block(name: str, message: object, *, ok: bool = False) -> None:
    step(name)

    if ok:
        success(str(message))
    else:
        value(message, color=_block_value_color(name))

    blank()


@contextmanager
def tool_block(name: str) -> Iterator[None]:
    """Render a compact development-tool invocation."""
    step(name, color=_CYAN)

    try:
        yield
    except Exception:
        failure(f"{name} failed")
        blank()
        raise
    else:
        success(f"{name} passed")
        blank()


def tool_result(name: str, message: str = "passed") -> None:
    """Render the result of a grouped development command."""
    step(name, color=_CYAN)
    success(f"{name} {message}")
    blank()


def footer(title: str) -> None:
    line = "━" * BANNER_WIDTH
    print(line)
    print(title.center(BANNER_WIDTH))
    print(line)
    print()


def section(
    title: str,
    blocks: Iterable[Block],
    *,
    footer_title: str | None = None,
) -> None:
    banner(title)

    for item in blocks:
        block(item.name, item.value, ok=item.ok)

    if footer_title:
        footer(footer_title)
