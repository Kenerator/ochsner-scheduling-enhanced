# Persona, story and test index

Updated: 2026-10-12. Reviewed baseline:
`164312722b33e55c382b500cf97a26f6ee41aa39`; additive launcher uses reviewed runtime
`b7875452`/delivery `6e894645`. The candidate's114-test suite passed on Mac ARM,
including15 consumer launcher checks. SM independent review passed and
[PR1](https://github.com/Kenerator/ochsner-scheduling-enhanced/pull/1) integrated
the selected candidate as `ee1a68c` on2026-10-13. Exact hypothesis pins and ancestor constraints remain in
[Personas](../product/personas.md); they supply no permissions or real-user proof.
[Native stories](../../specs/001-guarded-scheduling/spec.md) own acceptance;
[tasks](../../specs/001-guarded-scheduling/tasks.md) own implementation progress.

| Pinned constraint | Native story/design/source | Evidence and limit |
|---|---|---|
| Sam-Rae AGENT QA, `poc-template-seed-v1:98e1dcd5-8ee9-4b2b-b7fe-2045d389b9b4@1`: reproducible setup and truthful capability evidence | US6 / FR-021; [launch design](../../specs/001-guarded-scheduling/plan.md#launch-only-l4-increment--2026-10-12); existing [model adapter](../../src/guarded_scheduling/model_adapter.py) | [Launcher tests](../../tests/test_runtime_launcher.py) pass using actual constructors/fake HTTPS, manifest hashes, doctor/errors and real owned-process cleanup. Not live AI or browser execution evidence. |
| Morgan-Rae support, `poc-template-seed-v1:657aedfe-4a4a-4ec4-83c0-52614111f07c@1`: known/missing/unknown outcomes and no false delivery | US3/US5; [core](../../src/guarded_scheduling/core.py), [UI boundary](../../src/guarded_scheduling/ui_adapter.py); launch-only errors must preserve those boundaries | [Uncertainty](../../tests/test_scheduling_uncertainty.py), [handoff](../../tests/test_scheduling_handoff.py) and [UI](../../tests/test_scheduling_ui.py) tests pass in the114-test candidate suite; launcher invalid configuration/occupied listener/cancellation tests pass. No admin console or human delivery adopted. |
| Sam-Rae: replay/uncertain effects cannot authorize retry | US2/US3; core proposal/unknown lock remains unchanged by L4 | [Consent](../../tests/test_scheduling_consent.py) and UI replay/unknown tests passed in baseline; [UAT](uat.md#rc-2-and-focused-persona-evidence) records historical RC-2 application evidence. No new end-to-end launch qualification yet. |
| Jules, Ellie-Rae, Billy-June, Nina-Jean and Amy-Lou patient interaction constraints | Existing [pinned mappings](../product/personas.md) and native US1–US4 | [RC-2 evidence](uat.md#rc-2-and-focused-persona-evidence) retained. No new patient behavior is adopted by launch-only L4; existing guard regressions passed in the candidate suite. |

No copied persona card or scaffold check establishes application, live-model,
accessibility or browser behavior. Real-user validation remains pending; the
launcher does not add basic-phone service or production authentication.
