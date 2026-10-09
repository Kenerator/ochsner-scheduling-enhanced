# Key decisions

Updated: 2026-10-08.

- Reusable guarded_scheduling core; thin stdlib HTTP/Responses adapters and CLI/Marimo surfaces. Supplied reference backend remains unchanged.
- Explicitly adopt Enhanced appointment lookup, truthful mock handoff, RapidFuzz authoritative provider/vocabulary suggestions and Marimo. Integrate after mandatory safety verification; no fresh approval gate.
- Identity stays local. Only fail-closed public scheduling projections and non-identifying state reach the model; no raw history, patient records or identifiers.
- A choice creates an opaque patient/context-bound proposal. Only separate current confirmation consumes consent and permits one POST; unknown outcome locks booking until human reconciliation.
- gpt-5.4-mini passed a two-turn non-identifying generation probe; full application live qualification remains pending. Model remains configurable via OPENAI_MODEL; reviewers use ordinary OPENAI_API_KEY.
- Required internal-audience Ochsner assets are local and indexed in [UI assets](../internal/ui-assets.md).
- ZEN/CLIPS are not adopted by Enhanced: inspectable rule-engine policy behavior belongs to the separate Policy candidate. This is scope differentiation, not a claim that small rules cannot benefit from engines.
- Final setup qualification requires fresh private clones on Mac ARM and Minty Linux; mock matching is not production authentication, and mock handoff is not delivered human help.

[Native specification](../../specs/001-guarded-scheduling/spec.md) owns accepted details; [tasks](../../specs/001-guarded-scheduling/tasks.md) owns completion.
