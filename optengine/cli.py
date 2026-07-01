from collections.abc import Iterable
from dataclasses import dataclass


BANNER_WIDTH = 62


@dataclass(frozen=True)
class Block:
    name: str
    value: object
    ok: bool = False


def banner(title: str) -> None:
    line = "━" * BANNER_WIDTH
    print()
    print(line)
    print(title.center(BANNER_WIDTH))
    print(line)
    print()


def step(name: str) -> None:
    print(f"> {name}")


def success(message: str = "complete") -> None:
    print(f"✓ {message}")


def value(message: object) -> None:
    print(message)


def blank() -> None:
    print()


def block(name: str, message: object, *, ok: bool = False) -> None:
    step(name)
    if ok:
        success(str(message))
    else:
        value(message)
    blank()


def footer(title: str) -> None:
    line = "━" * BANNER_WIDTH
    print(line)
    print(title.center(BANNER_WIDTH))
    print(line)
    print()


def section(
    title: str, blocks: Iterable[Block], *, footer_title: str | None = None
) -> None:
    banner(title)

    for item in blocks:
        block(item.name, item.value, ok=item.ok)

    if footer_title:
        footer(footer_title)
