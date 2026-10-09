# User Stories — native specification index

Updated: 2026-10-08. This index describes source and scope, not implementation completion. Native `spec.md` owns reconciled stories/acceptance; [native tasks](../../specs/001-guarded-scheduling/tasks.md) owns progress.

## Supplied sources

- [Reconciled native requirements](../../specs/001-guarded-scheduling/spec.md)
- [Client requirements index](RFP/README.md)

## Native specification index

The [Guarded AI Appointment Scheduling specification](../../specs/001-guarded-scheduling/spec.md) reconciles supplied assignment, policies, suggested scenarios, reference API/server/data and Operator contract.

| Native story | Origin/basis | Scope | Persona mapping |
| --- | --- | --- | --- |
| [1 — Provider lookup](../../specs/001-guarded-scheduling/spec.md#user-story-1---find-providers-without-identity-collection-priority-p1) | Inferred wording from required provider flow | Mandatory | Primary scheduling user — unresolved placeholder |
| [2 — Confirmed booking](../../specs/001-guarded-scheduling/spec.md#user-story-2---book-the-exact-appointment-i-confirm-priority-p1) | Inferred wording from required booking and policy boundaries | Mandatory | Primary scheduling user — unresolved placeholder |
| [3 — Private failure/recovery](../../specs/001-guarded-scheduling/spec.md#user-story-3---receive-a-private-truthful-failure-and-next-step-priority-p1) | Inferred wording from required failure, policies and Operator guards | No-match baseline and specified guards mandatory | Primary scheduling user — unresolved placeholder |
| [4 — Preferences/appointment lookup](../../specs/001-guarded-scheduling/spec.md#user-story-4---refine-preferences-and-inspect-existing-appointments-priority-p2) | Inferred wording from optional assignment/Enhanced targets | Adopted Enhanced; consent corrections mandatory | Primary scheduling user — unresolved placeholder |
| [5 — Support/Admin context](../../specs/001-guarded-scheduling/spec.md#user-story-5---understand-recovery-context-without-sensitive-transcripts-priority-p2) | Inferred teammate seed reconciled with observability/handoff policies | Minimal diagnostics/docs required; truthful mock handoff adopted | Support/Admin teammate — unresolved placeholder |
| [6 — Reviewer reproduction](../../specs/001-guarded-scheduling/spec.md#user-story-6---reproduce-and-judge-the-poc-honestly-priority-p2) | Inferred wording from submission/reproduction requirements and candidate preferences | Reproduction/disclosure required; other candidate lanes independently owned | Developer/reviewer — unresolved placeholder |

## Persona follow-on

Select and pin named primary and Support/Admin personas in [Personas](personas.md), validate their constraints, and update native story mappings. Placeholders do not gate implementation or confer permissions. Origin remains inferred even where the underlying capability is explicitly required.
