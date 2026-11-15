from textsentinel.punctuation import (check_quote_style, find_missing_space_after,
                                      find_repeated_punct, find_space_before_punct,
                                      find_unbalanced_brackets, fix_space_before_punct)


def test_space_before_punct():
    assert len(find_space_before_punct("Привіт , світе")) == 1
    assert find_space_before_punct("Привіт, світе") == []


def test_missing_space_after():
    assert len(find_missing_space_after("Привіт,світе")) == 1


def test_missing_space_after_exceptions():
    assert find_missing_space_after("число 3,14") == []
    assert find_missing_space_after("сайт https://a.com/x і example.com") == []
    assert find_missing_space_after("і т.д. і т.п.") == []


def test_repeated_punct():
    assert len(find_repeated_punct("Що!!! Ну.. так... добре")) == 2


def test_brackets():
    assert len(find_unbalanced_brackets("(текст")) == 1
    assert len(find_unbalanced_brackets("текст)")) == 1
    assert find_unbalanced_brackets("(a) [b] «c»") == []
    assert find_unbalanced_brackets("1) пункт") == []


def test_quote_style():
    issues = check_quote_style('Слово "цитата" тут')
    assert len(issues) == 2
    assert "«" in issues[0].suggestion and "»" in issues[1].suggestion


def test_fix_space_before_punct():
    assert fix_space_before_punct("Привіт , світе !") == "Привіт, світе!"


def test_space_before_question_mark():
    assert len(find_space_before_punct("Що це ?")) == 1


def test_ellipsis_with_space_is_not_error():
    assert find_space_before_punct("Ну ... так") == []