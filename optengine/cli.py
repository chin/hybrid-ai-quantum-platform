import os
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass


BANNER_WIDTH = 62

_PASS_GREEN = "\033[32m"
_FAIL_RED = "\033[31m"

_RESET = "\033[0m"
_GREEN = "\033[38;2;118;185;0m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"

_BLOCK_VALUE_COLORS = {
    # "problem": _BLUE,
    "decision": _YELLOW,
    # "reason": None,
    "artifact": _CYAN,
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


def step(name: str, *, color: str | None = None) -> None:
    print(_colorize(f"> {name}", color), flush=True)


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
