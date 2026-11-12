"""Модуль 1: пробіли, порожні рядки, переноси."""
from __future__ import annotations

import re

from .models import Issue, context

_DOUBLE = re.compile(r"(?<=\S)( {2,})(?=\S)")  # відступи на початку рядка ігноруються
_TRAILING = re.compile(r"[ \t]+$")


def find_double_spaces(text: str) -> list[Issue]:
    """Два і більше пробілів поспіль всередині рядка."""
    issues = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in _DOUBLE.finditer(line):
            issues.append(Issue(
                "double_space", n, m.start() + 1, context(line, m.start(), m.end()),
                f"Кілька пробілів поспіль ({len(m.group())})", "warning",
                "Залиште один пробіл"))
    return issues


def find_trailing_spaces(text: str) -> list[Issue]:
    """Пробіли або табуляції в кінці рядка."""
    issues = []
    for n, line in enumerate(text.splitlines(), 1):
        m = _TRAILING.search(line)
        if m and line.strip():
            issues.append(Issue(
                "trailing_space", n, m.start() + 1, context(line, m.start(), m.end()),
                "Зайві пробіли в кінці рядка", "info", "Видаліть пробіли в кінці"))
    return issues


def find_empty_lines(text: str) -> list[Issue]:
    """Рядки лише з пробілами та порожні рядки на початку/в кінці тексту."""
    lines = text.splitlines()
    blank = [not ln.strip() for ln in lines]
    lead = 0
    while lead < len(lines) and blank[lead]:
        lead += 1
    trail_start = len(lines)
    while trail_start > lead and blank[trail_start - 1]:
        trail_start -= 1
    issues = []
    for i, ln in enumerate(lines):
        if not blank[i]:
            continue
        if ln:  # порожній за змістом, але містить пробіли
            issues.append(Issue("whitespace_only_line", i + 1, 1, repr(ln),
                                "Рядок складається лише з пробілів", "warning",
                                "Зробіть рядок порожнім"))
        elif i < lead or i >= trail_start:
            issues.append(Issue("empty_line_edge", i + 1, 1, "",
                                "Порожній рядок на початку або в кінці тексту", "info",
                                "Видаліть зайвий порожній рядок"))
    return issues


def find_excessive_newlines(text: str, max_consecutive: int = 1) -> list[Issue]:
    """Серії порожніх рядків довші за max_consecutive."""
    issues = []
    run_start = None
    lines = text.splitlines() + ["x"]  # «вартовий» для завершення останньої серії
    for i, ln in enumerate(lines):
        if not ln.strip():
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start > max_consecutive:
                run = i - run_start
                issues.append(Issue(
                    "excessive_newlines", run_start + 1, 1, "",
                    f"{run} порожніх рядків поспіль (дозволено {max_consecutive})",
                    "warning", f"Залиште не більше {max_consecutive}"))
            run_start = None
    return issues


def fix_whitespace(text: str, collapse_spaces: bool = True,
                   strip_trailing: bool = True, max_blank_lines: int = 1) -> str:
    """Автоматично виправляє пробіли й надмірні порожні рядки."""
    out = []
    for line in text.splitlines():
        if strip_trailing:
            line = line.rstrip()
        if collapse_spaces:
            line = _DOUBLE.sub(" ", line)
        out.append(line)

    result, blank = [], 0
    for line in out:
        if not line.strip():
            blank += 1
            if blank > max_blank_lines:
                continue
        else:
            blank = 0
        result.append(line)
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result) + "\n" if result else ""
