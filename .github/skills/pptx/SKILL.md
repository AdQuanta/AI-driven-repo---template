---
name: pptx
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file; editing, modifying, or updating existing presentations; combining or splitting slide files. Trigger whenever the user mentions 'deck,' 'slides,' 'presentation,' or references a .pptx filename."
author: skills.sh
source: "https://www.skills.sh/davila7/claude-code-templates/pptx"
---

# PPTX Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` |
| Edit existing presentation | Unpack XML → edit → repack |
| Create from scratch | Use pptxgenjs (Node) or python-pptx |

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx
```

---

## Creating from Scratch (python-pptx)

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
body = slide.placeholders[1]

title.text = "My Slide Title"
body.text = "First bullet\nSecond bullet\nThird bullet"

prs.save("presentation.pptx")
```

---

## Design Principles

- **Pick a bold color palette** specific to the topic.
- **Visual dominance**: one color 60-70%, one supporting, one sharp accent.
- **Every slide needs a visual element** — image, chart, icon, or shape.
- **Vary layouts** — don't repeat the same structure across all slides.
- **Left-align body text**; center only slide titles.
- **Font pairing**: a personality header font + clean body font.

---

## QA (Required)

```bash
# Content check
python -m markitdown output.pptx

# Check for placeholder leftovers
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum"
```

Convert to images for visual QA:
```bash
soffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

---

## Dependencies

```bash
pip install "markitdown[pptx]"   # text extraction
pip install python-pptx          # create/edit presentations
pip install Pillow               # thumbnail grids
```
