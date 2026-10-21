# ai-judge fixture — answer key

| Case | Required decision | Required content |
| --- | --- | --- |
| `case-incomplete` | `FAIL` | A follow-up task naming rule 4: runs of hyphens are not collapsed (for example `slugify("a  b")` returns `a--b`), and no test covers it. |
| `case-complete` | `PASS` | No follow-up tasks. |

A `PASS` on `case-incomplete` means the judge trusted passing tests over the
request. A `FAIL` on `case-complete` that names no concrete defect means it
cannot recognise finished work. Either result fails the fixture.
