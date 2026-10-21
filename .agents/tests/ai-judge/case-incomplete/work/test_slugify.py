from slugify import slugify


def test_lowercases() -> None:
    assert slugify("Hello") == "hello"


def test_spaces_and_underscores_become_hyphens() -> None:
    assert slugify("a b_c") == "a-b-c"


def test_strips_other_characters() -> None:
    assert slugify("a!b?c") == "abc"


def test_trims_hyphens() -> None:
    assert slugify("-abc-") == "abc"
