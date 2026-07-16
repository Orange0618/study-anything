# Progress and learning-review contract

`学习进度表.md` is the authoritative global index. Module documents and review files provide detail, but status changes must be reflected in the progress table.

## Required sections

1. Current status.
2. Learning goals.
3. Module status.
4. Task progress.
5. Learning-review index.
6. Deferred scope.

The bundled scripts rely on markers:

```markdown
<!-- MODULES_START -->
<!-- MODULES_END -->
<!-- TASKS_START -->
<!-- TASKS_END -->
<!-- REVIEWS_START -->
<!-- REVIEWS_END -->
```

Keep these markers when customizing headings.

## Separation rule

- Module teaching audits belong in `modules/<module>/审查/`.
- Learner progress, assessment, blocker, and scope-change reviews belong in root `reviews/`.

Do not mix them.

## Atomic learning update

Every meaningful learning-status change creates one event-driven learning review. Each changed task row links that review. Reviews are not required to follow weekly or monthly periods.

A task can become complete only when evidence exists and the learning review records the acceptance result.

## Relative links

Use forward-slash repository-relative paths in the progress table. Module README links are relative to the module directory. Avoid machine-specific absolute paths.

## Existing workspaces

If a customized progress file lacks standard markers, preserve its structure and enforce the same contract manually. Never replace a customized file merely to make a script convenient.
