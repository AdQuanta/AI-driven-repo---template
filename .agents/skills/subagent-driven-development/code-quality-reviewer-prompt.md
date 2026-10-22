# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer. Dispatch it as a
general-purpose subagent; it is a prompt template, not a named agent. The review
instructions below are complete; no other reviewer file is needed.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Subagent (general-purpose):
  description: "Code quality review for Task N"
  prompt: |
    You are reviewing the code changes for one task. Do not edit files.

    WHAT_WAS_IMPLEMENTED: [from implementer's report]
    PLAN_OR_REQUIREMENTS: Task N from [plan-file]
    BASE: [commit or recorded diff base before the task]
    HEAD: [current commit, or "working tree"]
    DESCRIPTION: [task summary]

    Inspect the diff between BASE and HEAD. Check correctness, test quality,
    error handling, naming, duplication, and whether the change follows the
    surrounding code's conventions. Also check:
    - Does each file have one clear responsibility with a well-defined interface?
    - Are units decomposed so they can be understood and tested independently?
    - Is the implementation following the file structure from the plan?
    - Did this change create new files that are already large, or significantly
      grow existing files? (Don't flag pre-existing file sizes.)

    Return: Strengths; Issues grouped as Critical / Important / Minor, each
    with file:line and a concrete fix; and an Assessment (approve, or changes
    needed).
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment
