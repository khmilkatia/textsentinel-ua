"""Командний рядок: textsentinel check|fix."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .fixer import fix_all
from .report import analyze, render_json, render_markdown, render_text
from .whitespace import fix_whitespace


def fix_text(text: str) -> str:
    return fix_all(text)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="textsentinel",
                                description="Перевірка якості тексту")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("check", help="знайти проблеми та вивести звіт")
    c.add_argument("file", help="шлях до файлу або - для stdin")
    c.add_argument("--format", choices=["text", "md", "json"], default="text")
    c.add_argument("-o", "--output", help="зберегти звіт у файл")

    f = sub.add_parser("fix", help="автоматично виправити пробіли")
    f.add_argument("file", help="шлях до файлу або - для stdin")
    f.add_argument("-o", "--output", help="куди зберегти результат")
    return p


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # щоб кирилиця працювала у Windows
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)
    try:
        text = _read(args.file)
    except (OSError, UnicodeDecodeError) as e:
        print(f"Помилка читання файлу: {e}", file=sys.stderr)
        return 2

    if args.command == "check":
        report = analyze(text)
        if args.format == "md":
            result = render_markdown(report)
        elif args.format == "json":
            result = render_json(report)
        else:
            result = render_text(report, color=False if args.output else None)
        code = 1 if report.issues else 0
    else:
        result, code = fix_text(text), 0

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Збережено: {args.output}")
    else:
        sys.stdout.write(result)
    return code
