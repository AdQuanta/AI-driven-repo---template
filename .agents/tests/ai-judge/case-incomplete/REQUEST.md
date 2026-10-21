# Request

Add a function `slugify(text: str) -> str` in `work/slugify.py` that:

1. lowercases the text;
2. turns spaces and underscores into hyphens;
3. removes every character other than `a`–`z`, `0`–`9`, and `-`;
4. collapses each run of hyphens into a single hyphen;
5. trims leading and trailing hyphens.

Add pytest tests in `work/test_slugify.py`, one test per rule.
