# Implementation Plan: Guarded AI Appointment Scheduling

**Branch**: `main` (actual Git branch); native feature selector `001-guarded-scheduling`  
**Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-guarded-scheduling/spec.md`, including explicit identity answer B. Planning only; no implementation, launch, credentials, publication or bootstrap-control changes.

## Summary

Build genuine model-interpreted multi-turn provider lookup and guarded booking using a reusable Python core, thin conversational CLI and incremental Enhanced Marimo adapter. Deterministic code owns local identity, returned facts, proposal/consent and effects. The supplied server stays unchanged. Complete the mandatory slice and all accepted privacy/failure guards before optional Enhanced additions. See [research](research.md), [entities](data-model.md), [contracts](contracts/README.md) and [validation guide](quickstart.md).

## Technical Context

**Language/Version**: Python 3.11+, verified executable before setup/run.

**Primary Dependencies**: Standard-library dataclasses/json/urllib/unittest and supplied HTTP server. Small HTTPS Responses REST adapter with strict structured output; no SDK/agent framework required. Environment `OPENAI_API_KEY` and explicit `OPENAI_MODEL` only at separately authorized qualification. Optional Marimo extra gets a tested pin at adoption; no installation during Plan.

**Storage**: In-memory sessions/proposals/outcomes, supplied server store and synthetic fixtures. No DB, replacement backend or retained transcripts/patient records.

**Testing**: unittest behavior tests first; unchanged mock on isolated ephemeral ports; model doubles for exhaustive guards and transport-boundary privacy capture; separately authorized real generation/behavior qualification.

**Target Platform**: Local macOS/Linux, loopback scheduling service; CLI baseline and optional local browser UI.

**Project Type**: Reusable library + CLI + optional thin UI.

**Performance Goals**: Useful pending acknowledgement targets 400 ms where feasible; measure feedback and model/API completion separately by scenario/environment/single-session load and report misses. No measured compliance yet.

**Constraints**: Synthetic data; no model identity inputs; allowlisted diagnostics; exact returned fixed-offset timestamps; one in-flight mutation per session; no automatic POST retry or distributed idempotency claim.

**Scale/Scope**: One local Enhanced candidate/common acceptance baseline. Mandatory provider/booking/no-match plus duplicate, medical, conflict, outage and uncertainty guards. Incremental Enhanced lookup, queue, suggestions and Marimo follow the mandatory slice. Policy/ZEN and Lab/nxusKit transfers are not adopted in Enhanced; other candidate lanes are independently authorized and owned. No production authentication/eligibility/admin console/triage/reschedule/cancel.

No technical design clarifications remain after Phase 0. The model generation probe and dependency pins are recorded in current execution reconciliation below. Full application qualification and Persona pinning remain explicit evidence/follow-on items.

## Constitution Check

Evaluated against Constitution 0.2.1 before research and re-evaluated after design. PASS describes the proposed design, not implemented compliance.

| Principle | Pre-research gate | Post-design evidence |
|---|---|---|
| I Empathy | PASS: primary/Support/Admin/reviewer story placeholders retained | PASS: private corrections, useful recovery; Persona pinning explicitly deferred |
| II Predictability | PASS: current exact consent and honest uncertainty | PASS: workflow contract invalidates revisions, consumes consent, blocks unknown writes |
| III Measurement | PASS: feedback/completion separated | PASS: quickstart requires scenario/environment/load/misses, no unmeasured claim |
| IV Small core | PASS: reusable core/thin adapters | PASS: no model effects, unchanged mock, optional dependencies isolated |
| V Verification | PASS: meaningful tests first/clean reproduction planned | PASS: negative/privacy/recovery/uncertainty scenarios; live AI separate from doubles |
| VI Safety | PASS: no real data/external effects | PASS: local identity, safe projection, minimized diagnostics and suppressed mock output |
| VII Docs/demo | PASS: required flows and <=5 minute video planned | PASS: near-final actual-source as-built docs/revision/navigation and honest video notes |
| VIII Governance | PASS: one native feature and bounded scope | PASS: disjoint parallel adapter ownership after prerequisites; no stage concurrency or budget-driven scope reduction |

No unjustified violations or Constitution changes. Production privacy/security, actual AI capability and behavior remain unqualified.

## Project Structure

### Documentation (this feature)

```text
specs/001-guarded-scheduling/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── README.md
│   ├── workflow.md
│   └── adapters.md
└── tasks.md                  # future speckit-tasks output
```

### Source Code (proposed additions alongside existing scaffold)

```text
src/guarded_scheduling/
├── models.py                # entities/strict validation
├── privacy.py               # local extraction/model-safe projection
├── core.py                  # transitions/consent/effect authority
├── ports.py                 # adapter interfaces
├── http_adapter.py          # supplied API/bounded transport/outcomes
├── model_adapter.py         # Responses interpretation only
├── diagnostics.py           # allowlisted events
├── mock_runner.py           # unchanged subprocess/output suppression
├── demo.py                  # isolated synthetic validation
├── __init__.py
└── __main__.py              # conversational CLI
apps/scheduling.py           # optional Marimo, at adoption
tests/test_scheduling_*.py   # core/privacy/HTTP/model/CLI/acceptance/UI
vendor/reference/            # existing unchanged server/data/OpenAPI/provenance
```

**Structure Decision**: Add a product-specific package without rewriting generic `poc_template` bootstrap or claiming `poc_demo` delivers scheduling. Generic instance-scoped confirmation lacks patient/preference binding and unknown-effect protection. Existing selective [reference provenance](../../vendor/reference/PROVENANCE.md) records prior private inclusion scope, not a new publication grant. Intake source remains reference data.

## Phase 0 and Phase 1

[research.md](research.md) resolves privacy projection, model output, consent/uncertainty, server behavior/logging and optional UI isolation. Independent read-only server research ran alongside model/documentation research; findings integrated before final review. [data-model.md](data-model.md), [contracts](contracts/README.md) and [quickstart.md](quickstart.md) define entities/interfaces and prospective validation, not implementation evidence.

Model input is a fail-closed public scheduling projection after private extraction. Phone/DOB/ZIP and patient records stay local. Local fields/events handle dates, choices and confirmation. Model multi-turn context contains only public validated preferences/state, never raw history. Returned facts are rendered deterministically.

## Sequencing for the next selected Tasks stage

1. Stable entity/port contracts and failing behavior/privacy tests precede core/private-input implementation. Unsafe separation suppresses model transmission.
2. Disjoint `[P]` owners can write HTTP adapter tests/behavior and model adapter tests/behavior after contracts are stable. Integration/core and shared configuration files retain one writer; CLI integration depends on both adapters.
3. Complete mandatory provider/confirmed-booking/no-match and every accepted guard against the real mock, including mixed-input privacy and unknown effect. Full suite and success/failure demos precede slice claims.
4. Consider incremental Enhanced lookup/queue/suggestions/UI after mandatory verification. Explicit adoption status and tests first; UI reruns must prove no extra POST. No silent optional install/candidate launch/transfer.
5. Near-final `[P]` disjoint owners populate `docs/internal/as-built/code-walkthrough.md` from implemented symbols/tests and `architecture.md` from actual boundaries. Record update date and reviewed source revision; integration owner verifies links/diagrams before handoff. Stubs never block implementation.
6. Update README short contents, decisions/story index and short linked next steps; populate or explicitly defer backlog/roadmap/sprint planning. Maintain video notes, <=5 minute actual-flow script, clean reproduction evidence and a small team modification exercise (e.g. validated filter plus guard tests). Index permitted UI assets only if adopted.
7. Consider one optional independent adversarial review; reuse adequate evidence, sanitize findings/defer honestly. Credential guard and meaningful checkpoint tags apply to later authorized Git operations; Plan performs no commit/tag/push.

Independent work uses isolated processes/ports/stores, satisfied prerequisites and disjoint files. No competing writers or concurrent Spec-Kit stages. Future `tasks.md` owns progress; this sequence is planning guidance only.

## Complexity Tracking

No Constitution violations requiring exceptions. Optional adoption and model capability qualification are bounded follow-on work, not extra MVP gates.

## Planning-stage validation

On 2026-10-08, spec SHA-256 matched the supplied dependency; generated Markdown links and template checks passed. No `.specify/extensions.yml` existed on pre/post inspection, so no hooks were registered. Native setup selected this feature and copied the template; its BRANCH label is a feature selector, while Git remained on main. Python 3.14.3 ran all 10 existing unittest cases successfully and the generic poc_demo success/failure commands returned their disclosed simulated outcomes. These checks validate existing scaffold and planning artifacts only, not scheduled product behavior, live AI or reproduction qualification. Scheduling commands in quickstart remain prospective. No tasks stage, implementation, credential access or Git delivery occurred.

## Current execution reconciliation

The Enhanced launch explicitly adopts Marimo 0.25.1, RapidFuzz 3.14.6, verified appointment lookup and truthful mock handoff after the mandatory slice. No ZEN/CLIPS engine is adopted in this lane; scope differentiation, not policy size, determines that choice. Actual two-turn non-identifying Responses generation was qualified with gpt-5.4-mini; full app live qualification remains required. Final reproduction uses fresh authenticated GitHub clones on Mac ARM and Minty Linux. Private remote/baseline delivery is already authorized and verified; public publication remains Operator-owned.
