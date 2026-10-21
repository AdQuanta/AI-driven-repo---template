"""Convert text to a URL slug."""

import re


def slugify(text: str) -> str:
    slug = text.lower().replace(" ", "-").replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")
