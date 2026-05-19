# Tasks — Todo

Per `.cursor/rules/ai-workflow.mdc`, every session that touches code adds a dated entry here and moves it to `## Completed` when done.

## In Progress

_(none — add the next ticket/task here)_

## Backlog

_(seed with whatever the user hands you next; the implementation work is not started yet)_

## Completed

### 2026-05-20 — Artifact audit step + post-commit reminder hook
- [x] Add Step 9 (Artifact audit) to `.cursor/skills/incubyte-tdd-loop/SKILL.md` (renumbered Loop-back to Step 10)
- [x] Add `scripts/git-hooks/post-commit` reminder script (executable, no-op when nothing matches)
- [x] Add `scripts/git-hooks/README.md` with one-time install instructions (`git config core.hooksPath scripts/git-hooks`)
- **Status**: done
- **Summary**: TDD loop now ends with a 60s artifact-audit checkpoint; opt-in post-commit hook nags on `perf:` / `docs(stitch):` / `!:` / `tradeoff:|decision:|considered:` body. Smoke-tested against 8 trigger subjects + 5 silent ones.

### 2026-05-20 — Cursor workspace bootstrap
- [x] Created `.cursor/{rules,skills,agents,plans}` with Incubyte TDD-first + craftsmanship setup
- [x] Created `tasks/`, `artifacts/`, `AGENTS.md` companion files
- **Status**: done
- **Summary**: Cursor rules/skills/agents in place; ready to start the Salary Management build with TDD.

## Entry template

```
### YYYY-MM-DD — <ticket or title>
- [ ] Sub-task
- [ ] Sub-task
- **Status**: in-progress | done
- **Summary**: <one-line outcome when done>
```
