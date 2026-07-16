# Platform portability

The skill is a filesystem protocol, not a product-specific automation.

## Required capability

The host agent needs only the ability to read and write text files. Everything else has a fallback.

## Optional capabilities and fallbacks

| Capability | Preferred use | Fallback |
| --- | --- | --- |
| Internet search | Verify current or specialized domain knowledge | Use local sources, label limits, list claims requiring later verification |
| Python 3.9+ | Run bundled scaffold, update, and validation scripts | Create files from templates and apply the progress-review contract manually |
| Shell | Execute scripts and reproducibility checks | Give portable commands for the user or another agent to run |
| Browser/GUI | Preview Markdown or dashboards | Keep all status readable in plain Markdown |
| Git | Preserve history and inspect changes | Avoid overwriting files and report a plain file-change summary |

## Path rules

- Store repository links as forward-slash relative paths.
- Do not embed machine-specific absolute paths in generated workbenches.
- Quote shell paths according to the active shell only in execution examples.
- Keep the workbench itself usable after moving it to another computer.

## Product-neutral language

- Say “agent” or “host agent,” not a product name, unless discussing that product's actual setup.
- Do not emit proprietary UI directives in workbench files.
- Do not require a specific task manager, memory system, connector, or IDE.
- Package the skill as a normal directory headed by `SKILL.md`; additional archive formats are optional distribution conveniences.
