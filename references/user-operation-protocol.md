# Six-command operation protocol

Parse `Study Anything: <Command> [arguments]` and `Study Anything：<Command> [arguments]` case-insensitively. The public commands are exactly `Setup`, `Master`, `Status`, `Continue`, `Record`, and `Assess`.

## Setup

Purpose: research a learning topic, help the user choose a meaningful depth, confirm scope, and create a new workbench.

Sequence:

1. Research before asking the user to define an abstract level.
2. Present two or three capability-based depth options.
3. Gather only personal context that changes the design.
4. Confirm capabilities, constraints, boundary, minimum completion line, and final artifact.
5. Confirm or infer the workbench location.
6. Scaffold the base workbench.
7. Write the research and source ledger.
8. Write goals and first tasks into the progress table.
9. Create a learning review for goal confirmation.
10. If the user wants to begin immediately, author the first module and run the module-review protocol before marking it learnable.

Do not create a roadmap. Do not create many empty modules in advance.

## Master

Purpose: let a new agent take over an existing learning workbench.

Read, in order:

1. `使用文档.md`;
2. `学习进度表.md`;
3. the current module README;
4. that module's latest audit report;
5. the latest relevant learning review;
6. referenced evidence and validation output.

Then report the current goal, module, module state, verified evidence, unresolved inconsistency or blocker, and one next action. Do not change files unless takeover reveals an inconsistency that the user authorized the agent to repair.

## Status

Purpose: provide a read-only current-state report.

Read the progress table and current module README. Report current goal, module state, last verified result, blocker, and next action. Do not create reviews or modify files.

## Continue

Purpose: select and execute the next valid action from persistent state.

Dispatch by module state:

- no module exists: author the next required module, invoke independent review, revise, and make it learnable only after passing;
- `待审查`: invoke an independent reviewer;
- `待修订`: revise from the latest audit report;
- `复审中`: invoke a fresh reviewer;
- `可学习`: change to `学习中` and begin the next learning unit;
- `学习中`: resume the next unfinished practice or explanation;
- `已阻塞`: explain the recorded recovery condition and work only on that blocker;
- `已学习`: move to the next prerequisite-satisfied task or module;
- all required modules learned: propose or continue the capstone.

Keep a single next action. Do not skip audit, prerequisite, or acceptance gates.

## Record

Purpose: persist learning progress, insight, failure, blocker, or scope change.

Derive or request only missing details for target task, actual result, evidence, problem, insight, and next action. Create a root learning review, update the task table, and synchronize the module README when its state changes.

If evidence is absent, do not mark a task complete. A blocker may be recorded without completion evidence, but must include a recovery condition.

## Assess

Purpose: assess the current or specified module against its saved acceptance criteria.

1. Confirm the module passed teaching audit.
2. Read its acceptance criteria.
3. Run available tests and inspect evidence.
4. Ask only the understanding questions that cannot be checked from files.
5. Decide pass or not-yet-pass with concrete evidence.
6. Create a root assessment review.
7. On pass, set the module to `已学习`; otherwise keep it `学习中` or `已阻塞` and create one recovery task.
8. Synchronize the module README and progress table.

Never pass a module from note count, time spent, or course completion alone.
