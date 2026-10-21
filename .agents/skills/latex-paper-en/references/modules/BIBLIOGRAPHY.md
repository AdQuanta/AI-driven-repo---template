# Module: Bibliography

**Trigger**: bib, bibliography, 参考文献, citation

## Commands

```bash
python -B .agents/skills/latex-paper-en/scripts/verify_bib.py references.bib
python -B .agents/skills/latex-paper-en/scripts/verify_bib.py references.bib --tex main.tex
python -B .agents/skills/latex-paper-en/scripts/verify_bib.py references.bib --standard gb7714
python -B .agents/skills/latex-paper-en/scripts/verify_bib.py references.bib --tex main.tex --json
```

## Details
Checks: required fields, duplicate keys, missing citations, unused entries.
Key output fields: `missing_in_bib`, `unused_in_tex`.
Skill-layer response: convert the raw verification results into `% BIBLIOGRAPHY ...` style findings when presenting them to the user.

See also: [CITATION_VERIFICATION.md](../CITATION_VERIFICATION.md) for API-based verification.

