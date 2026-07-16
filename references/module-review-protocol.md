# Teaching-module review protocol

Every new module must be independently reviewed after the main agent drafts it and before the module becomes `可学习`.

## Roles

### Main agent: author

- derive the module goal from research and progress;
- write explanation, practice, tests, evidence expectations, and acceptance;
- mark the module `待审查`;
- invoke the reviewer;
- address each finding and record its disposition;
- invoke a fresh reviewer after blocker or major findings;
- synchronize module and global status.

### Review subagent: reviewer

- act independently and read only the supplied learner context, research, prerequisites, goal, module files, environment, and rubric;
- do not edit teaching files;
- run examples and tests when tools permit;
- report actionable findings with evidence;
- write only the audit report if the host allows shared output, otherwise return the report for the main agent to save unchanged.

## Review dimensions

1. Goal alignment.
2. Factual, mathematical, or technical correctness.
3. Source authority and freshness where relevant.
4. Missing prerequisites.
5. Difficulty gradient and cognitive load.
6. Explanation-to-practice alignment.
7. Executability and reproducibility.
8. Test coverage and failure handling.
9. Acceptance validity.
10. Evidence clarity.
11. Safety, cost, privacy, permission, or hardware risk.

## Severity

- `Blocker`: unsafe, fundamentally wrong, or not executable. Prohibits learning.
- `Major`: materially harms understanding, practice, or assessment. Requires revision and fresh re-audit.
- `Minor`: affects clarity or experience. Requires disposition; re-audit is optional.
- `Suggestion`: optional improvement.

## Decisions

- `通过`: no unresolved Blocker or Major finding.
- `修改后通过`: only Minor or Suggestion findings remain and the main agent records their disposition.
- `不通过`: one or more Blocker or Major findings remain.

## Audit files

Store inside the module:

```text
审查/
├─ YYYY-MM-DD_初审报告.md
├─ YYYY-MM-DD_修订记录.md
└─ YYYY-MM-DD_复审报告.md
```

Never store these reports in root `reviews/`.

## Independent-review fallback

If native subagents are unavailable, prepare the reviewer input as a standalone task for a fresh independent session or another agent tool. Keep the module `待审查` until that report returns. A same-context self-review may find defects but cannot be labeled independent review or unlock `可学习`.
