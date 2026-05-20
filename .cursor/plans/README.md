# Cursor plans — raw archive

> Audit trail of the AI-generated implementation plans that drove each
> major phase of the build. **For curated, reviewer-ready narratives,
> read [../../artifacts/planning/](../../artifacts/planning/) instead.**

These files are the raw output of Cursor's plan mode — the agent's
working notes, in the order they were produced. They are preserved
verbatim so the assessment reviewer can see how planning was actually
done, but they are intentionally not edited or polished.

## What's in here

| Plan | Drove |
|---|---|
| [incubyte_cursor_setup_f53f25a7.plan.md](incubyte_cursor_setup_f53f25a7.plan.md) | Cursor workspace bootstrap — rules, skills, agents |
| [salary_mgmt_execution_plan_4021925a.plan.md](salary_mgmt_execution_plan_4021925a.plan.md) | Phases 1–13 of the main build (backend → frontend → hardening → deploy) |
| [backend_frontend_logging_implementation_7a69693d.plan.md](backend_frontend_logging_implementation_7a69693d.plan.md) | Logging + observability (JSON formatter, request-id, ErrorBoundary) |
| [salary-mgmt_bugs_and_analytics_2c8dd4b6.plan.md](salary-mgmt_bugs_and_analytics_2c8dd4b6.plan.md) | Bug fixes + advanced HR analytics (compa-ratio, payroll, NTILE outliers) |
| [insights-polish-ux-pass_c3887b4e.plan.md](insights-polish-ux-pass_c3887b4e.plan.md) | UX polish — `<AnalyticsSection>`, `<InfoHint>`, Title-Case sweep |
| [seed-10k-perf-validate_dcbc7a0c.plan.md](seed-10k-perf-validate_dcbc7a0c.plan.md) | Seed performance validation at 10k |
| [address-review-warnings_864a30e2.plan.md](address-review-warnings_864a30e2.plan.md) | Review-warnings batch (W1–W4 + I1–I2) + QA pass |

## Where to read instead

For each plan, the curated, reorganized narrative now lives in
[../../artifacts/planning/](../../artifacts/planning/):

| Raw plan | Curated home |
|---|---|
| `incubyte_cursor_setup_*` | [ai-assisted-workflow.md](../../artifacts/planning/ai-assisted-workflow.md) |
| `salary_mgmt_execution_plan_*` | [implementation-phases.md](../../artifacts/planning/implementation-phases.md) + [roadmap.md](../../artifacts/planning/roadmap.md) |
| `backend_frontend_logging_implementation_*` | [backend-architecture.md](../../artifacts/planning/backend-architecture.md) §Logging |
| `salary-mgmt_bugs_and_analytics_*` | [analytics-strategy.md](../../artifacts/planning/analytics-strategy.md) |
| `insights-polish-ux-pass_*` | [ui-ux-decisions.md](../../artifacts/planning/ui-ux-decisions.md) |
| `seed-10k-perf-validate_*` | [seed-performance-strategy.md](../../artifacts/planning/seed-performance-strategy.md) |
| `address-review-warnings_*` | [implementation-phases.md](../../artifacts/planning/implementation-phases.md) §Phase 12 |
