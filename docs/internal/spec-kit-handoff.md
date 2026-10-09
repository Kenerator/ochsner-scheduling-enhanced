# Remaining Spec-Kit stages

Generated handoff, not completion evidence. Run from this project's root. Use stages in order; both installed integrations share the local feature files. You may switch assistant for each stage. Do not run competing sessions on the same feature.

The blocks use codex syntax. Claude uses `/speckit-STAGE`; Codex uses `$speckit-STAGE`. Change only the first-line prefix when switching assistant, or regenerate with `poc-template bootstrap prompts --project . --integration claude` (or `codex`).

Manual stage execution does not update the automated workflow's completion state. Before manual continuation, stop/reconcile any live automated owner. Resolve any reported failure or pending question; these prompts do not bypass it. Let installed Spec-Kit handle its normal prerequisites, clarifications and Constitution checks.

Last automated result: Generated tasks.md: 68 tasks, 24 parallel markers. Story counts: US1 6, US2 9, US3 8, US4 5, US5 8, US6 9; shared 23. Includes story-specific independent tests, dependencies and mandatory MVP scope. Format checks passed; spec/plan unchanged; no extension hooks. All 10 scaffold tests and simulated success/failure demos passed; scheduling implementation and live AI remain unqualified.

## Stage 5: Analyze

Codex: `$speckit-analyze` · Claude: `/speckit-analyze`

```text
$speckit-analyze
```

## Stage 6: Implement

Codex: `$speckit-implement` · Claude: `/speckit-implement`

```text
$speckit-implement
```
