# Workbench handoff protocol

Persistent files, not conversation memory, are authoritative when an agent takes over.

## Reading order

1. `使用文档.md`: architecture, file roles, state rules, and maintenance contract.
2. `学习进度表.md`: current global state and traceability.
3. Current module `README.md`: local state, goal, audit, evidence, and learning review.
4. Latest module audit report under `审查/`.
5. Latest relevant root learning review under `reviews/`.
6. Referenced tests and evidence.

## Conflict priority

Use this evidence order:

`existing evidence and test output > progress table and module README after synchronization > audit and learning reviews > unsupported conversational claims`

When files disagree, do not silently choose one. Identify the conflict, inspect evidence and timestamps, correct both status surfaces together, and create a learning review if learner progress changes.

## Takeover output

Report:

- the confirmed learning purpose;
- current module and state;
- latest verified evidence;
- latest audit conclusion;
- active blocker or inconsistency;
- one next action.

Do not immediately create a new module during takeover.
