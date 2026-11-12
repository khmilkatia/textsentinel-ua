from textsentinel.whitespace import (find_double_spaces, find_empty_lines,
                                     find_excessive_newlines, find_trailing_spaces,
                                     fix_whitespace)


def test_double_spaces_found():
    issues = find_double_spaces("a  b")
    assert len(issues) == 1
    assert issues[0].rule == "double_space"
    assert issues[0].column == 2


def test_indentation_is_ignored():
    assert find_double_spaces("    відступ") == []


def test_trailing_spaces():
    issues = find_trailing_spaces("abc  \nxyz")
    assert len(issues) == 1 and issues[0].line == 1 and issues[0].column == 4


def test_empty_lines():
    rules = {i.rule for i in find_empty_lines("\n\nabc\n   \nx")}
    assert rules == {"empty_line_edge", "whitespace_only_line"}


def test_excessive_newlines():
    assert len(find_excessive_newlines("a\n\n\n\nb")) == 1
    assert find_excessive_newlines("a\n\n\n\nb", max_consecutive=3) == []
    assert find_excessive_newlines("a\n\nb") == []


def test_fix_whitespace():
    assert fix_whitespace("a  b   \n\n\n\nc  \n") == "a b\n\nc\n"
