"""Модуль 2: розділові знаки, дужки, лапки."""
from __future__ import annotations

import re

from .models import Issue, context

LETTERS = "A-Za-zА-Яа-яІіЇїЄєҐґ"
_ABBR = re.compile(rf"^(?:[{LETTERS}]{{1,2}}\.){{2,}}$")            # т.д., т.п.
_URLISH = re.compile(r"://|@|www\.|\.(?:com|org|net|ua|edu|gov|io)\b", re.I)
_REPEATED = re.compile(r"([!?,;:])\1+|(?<!\.)\.{2}(?!\.)|\.{4,}")
_PAIRS = {")": "(", "]": "[", "}": "{", "»": "«"}
_OPENERS = set(_PAIRS.values())


def find_space_before_punct(text: str, marks: str = ".,;:!?") -> list[Issue]:
    """Пробіл перед розділовим знаком: «Привіт ,»."""
    pat = re.compile(rf"(?<=\S)( +)([{re.escape(marks)}])")
    issues = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in pat.finditer(line):
            issues.append(Issue(
                "space_before_punct", n, m.start() + 1, context(line, m.start(), m.end()),
                f"Пробіл перед знаком «{m.group(2)}»", "warning", "Приберіть пробіл"))
    return issues


def find_missing_space_after(text: str, marks: str = ".,;:!?") -> list[Issue]:
    """Немає пробілу після знака. Числа (3,14), URL і скорочення (т.д.) ігноруються."""
    pat = re.compile(rf"([{re.escape(marks)}])(?=[{LETTERS}])")
    issues = []
    for n, line in enumerate(text.splitlines(), 1):
        for tok in re.finditer(r"\S+", line):
            word = tok.group()
            if _URLISH.search(word) or _ABBR.match(word.rstrip(",;:!?")):
                continue
            for m in pat.finditer(word):
                col = tok.start() + m.start()
                issues.append(Issue(
                    "missing_space_after", n, col + 1, context(line, col, col + 2),
                    f"Немає пробілу після «{m.group(1)}»", "warning", "Додайте пробіл"))
    return issues


def find_repeated_punct(text: str) -> list[Issue]:
    """Повтори знаків: «!!!», «??», «..» (багатокрапка «...» дозволена)."""
    issues = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in _REPEATED.finditer(line):
            frag = m.group()
            fix = ("..." if len(frag) >= 4 else ".") if frag[0] == "." else frag[0]
            issues.append(Issue(
                "repeated_punct", n, m.start() + 1, context(line, m.start(), m.end()),
                f"Повтор знака «{frag}»", "warning", f"Замініть на «{fix}»"))
    return issues


def find_unbalanced_brackets(text: str) -> list[Issue]:
    """Парність (), [], {}, «» через стек."""
    issues, stack = [], []
    for n, line in enumerate(text.splitlines(), 1):
        for c, ch in enumerate(line, 1):
            if ch in _OPENERS:
                stack.append((ch, n, c))
            elif ch in _PAIRS:
                # нумерація списків типу «1)» або «а)» пропускаємо
                if ch == ")" and re.fullmatch(rf"\s*(\d+|[{LETTERS}])", line[:c - 1]):
                    continue
                if stack and stack[-1][0] == _PAIRS[ch]:
                    stack.pop()
                else:
                    issues.append(Issue("unbalanced_bracket", n, c, context(line, c - 1, c),
                                        f"Зайва закрита дужка «{ch}»", "error",
                                        "Видаліть її або додайте відкриту"))
    for ch, n, c in stack:
        issues.append(Issue("unbalanced_bracket", n, c, ch,
                            f"Не закрито «{ch}»", "error", "Додайте закриваючу дужку"))
    return sorted(issues, key=lambda i: (i.line, i.column))


def check_quote_style(text: str, style: str = "«»") -> list[Issue]:
    """Прямі лапки \" замість українських «»."""
    if style == '"' or len(style) != 2:
        return []
    issues, is_open = [], True
    for n, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'"', line):
            repl = style[0] if is_open else style[1]
            issues.append(Issue("quote_style", n, m.start() + 1,
                                context(line, m.start(), m.end()),
                                'Прямі лапки замість «»', "info", f"Замініть на «{repl}»"))
            is_open = not is_open
    return issues


def fix_space_before_punct(text: str, marks: str = ".,;:!?") -> str:
    """Прибирає пробіл перед розділовими знаками."""
    return re.sub(rf"(?<=\S) +([{re.escape(marks)}])", r"\1", text)
