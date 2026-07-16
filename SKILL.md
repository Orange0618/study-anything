---
name: study-anything
description: >-
  Build, take over, continue, record, and assess a traceable practice-driven
  learning workbench for any field. Use this skill whenever the user explicitly
  writes Study Anything commands such as Setup, Master, Status, Continue,
  Record, or Assess, and whenever they want an agent to research an unfamiliar
  field, create or maintain a learning project, generate reviewed teaching
  modules, continue from saved progress, or verify learning with evidence.
  Research before confirming scope, keep the progress table authoritative, and
  require independent subagent review before a new teaching module becomes
  learnable.
compatibility: Works with file-capable agent tools on Windows, macOS, and Linux. Native subagents are preferred for independent module review. Python 3.9+ is optional for bundled automation; agents without Python can follow the Markdown protocols manually.
---

# Study Anything

Build and maintain a learning workbench where domain research informs the goal, teaching modules are independently reviewed, practice produces evidence, and another agent can reliably take over later.

## Six-command interface

Recognize either an English or Chinese colon, optional spaces, and case-insensitive command names:

```text
Study Anything: Setup <learning topic and optional constraints>
Study Anything: Master [workbench path]
Study Anything: Status
Study Anything: Continue
Study Anything: Record [optional progress, insight, or blocker]
Study Anything: Assess [optional module ID]
```

These are the only public commands. Module planning, authoring, independent review, revision, re-review, state synchronization, and capstone preparation are internal workflows invoked by these commands.

After identifying a command, read `references/user-operation-protocol.md` and execute that command's contract. If no explicit command is present but the request clearly matches this skill, infer the nearest command and state the interpretation.

## Platform-neutral operation

Use ordinary files, relative Markdown links, and standard Markdown as the interoperability layer. Do not require a particular agent product, shell, editor, browser, memory system, or proprietary directive.

Bundled Python scripts are conveniences. When Python or command execution is unavailable, create the same files and enforce the same rules manually. When native subagents are unavailable, read `references/module-review-protocol.md` and use its independent-session fallback; do not claim that an unreviewed module passed independent review.

Read `references/platform-portability.md` when adapting paths, commands, or review execution to the host agent.

## Authoritative traceability

Keep this chain:

`Goal -> Module -> Task -> Acceptance -> Evidence -> Learning Review -> Status -> Next action`

Use `学习进度表.md` as the authoritative global index. Do not create a roadmap file or `roadmap/` directory.

Separate two kinds of records:

- `modules/<module>/审查/`: teaching-content audit reports, author revision records, and re-audits.
- `reviews/`: reviews of the learner's actual progress, assessment, blocker, insight, or scope change.

Whenever learning progress changes, create a learning review and link it from the progress table. Do not mark a learning task complete without evidence and a learning review.

## Research before goal confirmation

Users often do not know what a field contains or how deeply to learn it. Before confirming scope:

1. Inspect supplied local materials and any existing workspace.
2. Research the field using authoritative or primary sources when information is current, specialized, safety-sensitive, or not covered locally.
3. Identify core knowledge, prerequisites, tools, representative practice, plausible depth options, professional or project outcomes, and common passive-learning traps.
4. Explain two or three concrete learning-depth options through observable capabilities and evidence.
5. Then gather the user's background, purpose, available time, deadline, environment, constraints, existing materials, and desired final artifact.
6. Confirm final capabilities, current boundary, deferred topics, minimum completion line, and acceptance criteria.

Do not scaffold a full workspace merely from a vague topic. Give the user enough researched context to make an informed choice first. Read `references/research-first-workflow.md` for the full protocol.

## Workbench contract

The default workbench contains:

```text
学习主题/
├─ README.md
├─ 使用文档.md
├─ 学习进度表.md
├─ 调研/
│  ├─ 领域调研.md
│  └─ 资料来源.md
├─ 环境/
│  ├─ README.md
│  └─ 验证.md
├─ modules/
│  └─ 01-主题/
│     ├─ README.md
│     ├─ notes/
│     ├─ practice/
│     ├─ tests/
│     ├─ evidence/
│     └─ 审查/
├─ reviews/
├─ capstone/
└─ .gitignore
```

`使用文档.md` explains architecture, file meanings, state rules, and agent handoff. It does not contain the six command prompts; those belong to this skill.

Use `scripts/scaffold_workbench.py` to create missing base files without overwriting existing content. Add ecosystem manifests only when relevant.

For an existing workbench, inspect conventions and version-control state, preserve existing terminology, and add only missing pieces. Read `references/workbench-handoff-protocol.md` before taking over.

## Module lifecycle

Each module README must show one current state:

```text
规划中 -> 编写中 -> 待审查 -> 待修订 -> 复审中 -> 可学习 -> 学习中 -> 已学习
```

Optional exceptional states are `已阻塞` and `已暂停`.

Every new teaching module follows the examiner-and-reviewer pattern:

1. The main agent authors the module and marks its README `待审查`.
2. The main agent invokes an independent subagent with only the learner context, research findings, module goal, prerequisites, module files, and audit rubric.
3. The reviewer does not edit teaching files. It returns a structured report; save it under the module's `审查/` directory.
4. The main agent addresses every finding and writes a revision record under the same `审查/` directory.
5. If the audit found a blocker or major issue, invoke a fresh reviewer after revision and save a re-audit report.
6. Only a module with an independent passing audit and no unresolved blocker or major issue may become `可学习`.
7. Synchronize the module README and the module-status table in `学习进度表.md`.

Read `references/module-review-protocol.md` before authoring or reviewing a module. Use `scripts/update_module_status.py` and `scripts/validate_module_review.py` when their standard markers are present.

## Learning loop

For each learnable module:

1. Start with a question or capability, not a resource list.
2. Explain the minimum theory needed for practice.
3. Ask the learner to predict, derive, design, or state an expectation when appropriate.
4. Run the smallest meaningful practice.
5. Change an input, variable, assumption, or scenario so the learner must reason rather than copy.
6. Test objectively where possible; otherwise use an explicit rubric.
7. Save durable evidence.
8. Use `Record` or `Assess` to create a learning review and synchronize status.
9. Give one clear next action.

Evidence may be code, tests, structured results, plots, measurements, corrected exercises, derivations, design artifacts, demonstrations, or explanation notes. Read `references/evidence-guidelines.md` before defining acceptance or declaring completion.

## Progress and learning reviews

Learning reviews are event-driven, not calendar-driven. Create one for meaningful progress, assessment, failure, blocker, insight, scope change, or learning decision.

Use `scripts/update_progress.py` when the standard task table is present. It creates a learning review under root `reviews/`, updates the task row, links the evidence and review, and rejects completed tasks whose evidence is missing.

Never put teaching audit reports in root `reviews/`. Never put learning-progress reviews in a module's `审查/` directory.

Read `references/progress-review-contract.md` before changing progress formats.

## Completion and handoff

A module is `已学习` only when:

1. its teaching content passed independent review;
2. the learner applied the acceptance criterion;
3. evidence exists;
4. a learning review records the result and next action;
5. the module README and progress table agree.

A capstone may start only after its prerequisite modules are `已学习`. Apply the same author-reviewer pattern to its teaching and assessment design.

At the end of an invocation, report the verified current state, changed files, unresolved assumptions or blockers, and one recommended next action. Link files when the host supports it; otherwise report portable relative paths.

## Bundled resources

- `references/user-operation-protocol.md`: exact behavior of the six public commands.
- `references/workbench-handoff-protocol.md`: reliable takeover of an existing workbench.
- `references/module-review-protocol.md`: independent reviewer rubric and revision loop.
- `references/research-first-workflow.md`: field research and informed depth selection.
- `references/domain-adaptation.md`: evidence and structure across different fields.
- `references/evidence-guidelines.md`: evidence quality and acceptance design.
- `references/progress-review-contract.md`: global progress and learning-review rules.
- `references/platform-portability.md`: cross-agent and cross-platform fallbacks.
- `scripts/scaffold_workbench.py`: safe base-workbench creation.
- `scripts/update_progress.py`: learning review plus task-progress update.
- `scripts/update_module_status.py`: module README plus global module-status synchronization.
- `scripts/validate_module_review.py`: module audit and state validation.
- `scripts/validate_workbench.py`: full structural and traceability validation.
