from pathlib import Path

from textsentinel.cli import main

DATA = Path(__file__).parent / "data"


def test_check_dirty_returns_1(capsys):
    assert main(["check", str(DATA / "dirty_sample.txt")]) == 1
    assert "Оцінка якості" in capsys.readouterr().out


def test_check_clean_returns_0():
    assert main(["check", str(DATA / "clean_sample.txt")]) == 0


def test_fix_writes_file(tmp_path):
    out = tmp_path / "clean.txt"
    assert main(["fix", str(DATA / "dirty_sample.txt"), "-o", str(out)]) == 0
    fixed = out.read_text(encoding="utf-8")
    assert "  " not in fixed and " ," not in fixed


def test_missing_file_returns_2():
    assert main(["check", "no_such_file.txt"]) == 2
