"""Автовиправлення: усе, що можна виправити безпечно."""
from __future__ import annotations

import re

from .punctuation import LETTERS, _ABBR, _URLISH
from .whitespace import fix_whitespace

MARKS = ".,;:!?"


def fix_repeated_punct(text: str) -> str:
    """«!!!» -> «!», «..» -> «.», «....» -> «...»."""
    text = re.sub(r"([!?,;:])\1+", r"\1", text)
    text = re.sub(r"(?<!\.)\.{2}(?!\.)", ".", text)
    return re.sub(r"\.{4,}", "...", text)


def fix_space_before(text: str) -> str:
    """Прибирає пробіл перед знаком (багатокрапку «...» не чіпає)."""
    return re.sub(rf"(?<=\S) +([{re.escape(MARKS)}])(?!\.\.)", r"\1", text)


def fix_missing_space_after(text: str) -> str:
    """Додає пробіл після знака. Числа, URL і скорочення не чіпає."""
    pat = re.compile(rf"([{re.escape(MARKS)}])(?=[{LETTERS}])")

    def fix_token(m: re.Match) -> str:
        tok = m.group()
        if _URLISH.search(tok) or _ABBR.match(tok.rstrip(",;:!?")):
            return tok
        return pat.sub(r"\1 ", tok)

    return re.sub(r"\S+", fix_token, text)


def fix_quotes(text: str) -> str:
    """Прямі лапки -> «ялинки» (лише якщо їх парна кількість)."""
    if text.count('"') % 2:
        return text
    out, opened = [], False
    for ch in text:
        if ch == '"':
            out.append("»" if opened else "«")
            opened = not opened
        else:
            out.append(ch)
    return "".join(out)


def fix_repeated_words(text: str) -> str:
    """«це це» -> «це»."""
    pat = re.compile(rf"(?<![{LETTERS}])([{LETTERS}]{{2,}})[ \t]+\1(?![{LETTERS}])", re.I)
    prev = None
    while prev != text:
        prev, text = text, pat.sub(r"\1", text)
    return text


def fix_all(text: str) -> str:
    """Застосовує всі безпечні виправлення. Порядок важливий."""
    text = fix_repeated_punct(text)
    text = fix_space_before(text)
    text = fix_missing_space_after(text)
    text = fix_quotes(text)
    text = fix_repeated_words(text)
    return fix_whitespace(text)
