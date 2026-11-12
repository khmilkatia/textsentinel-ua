"""Спільний контракт між модулями: усі перевірки повертають list[Issue]."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Issue:
    rule: str                      # наприклад "double_space"
    line: int                      # номер рядка (з 1)
    column: int                    # номер колонки (з 1)
    fragment: str                  # фрагмент тексту навколо проблеми
    message: str                   # людський опис
    severity: str = "warning"      # "error" | "warning" | "info"
    suggestion: str | None = None  # що зробити


def context(line: str, start: int, end: int, pad: int = 12) -> str:
    """Повертає фрагмент рядка навколо знайденої проблеми."""
    return line[max(0, start - pad): min(len(line), end + pad)]
