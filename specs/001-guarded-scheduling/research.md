# Research: Guarded scheduling

Updated: 2026-10-08. Phase 0 design decisions; no credential/API generation test, implementation qualification or service launch occurred.

## Local identity and fail-closed model projection

**Decision**: Apply explicit answer B. Collect phone/DOB and duplicate ZIP in private local controls/prompts. Extract recognized identity spans before interpretation and construct minimized model requests from approved scheduling-language fragments and validated public preference labels. Remove numeric fragments, number-word identity encodings and identity labels/spans; local date/choice controls handle numbers. If safe separation is uncertain, skip the model call and ask for private identity entry plus scheduling-only reformulation. Never interpolate raw messages, patient records, private fields, endpoint queries or exception text into prompts. Model context is newly built each turn, not raw history. Test serialized requests at the transport boundary, including mixed input/corrections/duplicates and alternate formats. Known identity values must also be excluded from any projected preference collision. Discard raw text after local processing; never retain it in evidence.

**Rationale**: Privacy precedes interpretation. Regex replacement alone cannot establish unrestricted free-text privacy; constrained public projection and suppression under ambiguity create a testable prototype boundary. Separate events retain multi-turn context while genuine model interpretation recognizes intent from scheduling language. Disclose local identity processing and AI scheduling interpretation. Production privacy remains unqualified.

**Alternatives considered**: Raw identity to model (explicitly rejected); model-led redaction (already sends sensitive input); regex-only transcript masking (unsafe ambiguity); removing AI (violates FR-001).

## Genuine interpretation without tool authority

**Decision**: Small stdlib HTTPS adapter calls Responses REST with `store: false`, no tools, strict `text.format` JSON schema and explicit environment model. Rebuild sanitized input each turn. Independently validate output; refusal, incomplete response, unknown keys/types or unavailable model produce useful clarification and no effect. No model repair loop, credential assumption or default readiness claim. Explicit model is configured during separately authorized capability qualification.

**Rationale**: Structured output constrains shape, not intent accuracy or consent. Deterministic validation remains necessary. Stateless requests reduce history reuse; disabled storage is not compliance certification. Primary sources fetched 2026-10-08: [Responses migration](https://developers.openai.com/api/docs/guides/migrate-to-responses), [structured output guide](https://developers.openai.com/api/docs/guides/structured-outputs).

**Alternatives considered**: Autonomous tool agent (unneeded authority); SDK with tracing/retry (more controls/dependency); keyword-only assistant (test double, not genuine AI qualification). Reviewer uses ordinary environment configuration, no vault dependency. No credentials accessed during Plan.

## Identity, consent and effect uncertainty

**Decision**: Serialize local session events. Exactly one returned patient establishes prototype verification; duplicate ZIP filters returned candidates locally. Proposal binds patient/verification generation, preference generation, returned catalog generation and selected slot. Confirmation is an explicit separate local event, never model output. Consume consent and mark submitting before one POST. Changes invalidate dependent state; uncertain submission locks further booking pending human reconciliation.

**Rationale**: API has no idempotency/reconciliation endpoint. Successful server booking mutates state before sending its response. Lost/malformed/unbound success is unresolved, not failed. Validate patient/provider/specialty/location/time/status against proposal before reporting booked; response has no slotId to validate. In-memory replay protection is not restart/distributed once-only guarantee.

**Alternatives considered**: Model confirmed flag; selection as consent; blind retry/reset; replacement backend/database; invented reconciliation endpoint (all rejected).

## Supplied scheduling semantics

**Decision**: Use existing unchanged `vendor/reference/mock-api/server.py` with relative fixtures and [OpenAPI](../../vendor/reference/openapi/scheduling-api.yaml). Specialties: primary_care/dermatology; locations: downtown/uptown/lakeside. Preserve returned time strings and fixed -05:00; fixture dates materialize relative to server host date. Validate calendar dates/range locally because server compares strings. Never inspect fixture-only fields, infer eligibility from establishedPatient, add ZIP queries or special-case conflict IDs. Failure header is demo/test transport configuration, not model output.

**Rationale**: The actual supplied behavior is scheduling authority. Valid 409 is rejected; injected pre-effect outage applies to all requests including handoffs. Independent read-only research inspected server/API/policies; supplied fixture README confirms hidden fields and fixed offset.

**Alternatives considered**: Schema-generated/replacement mocks (lower fidelity); DST reinterpretation (alters authoritative time); invented patient/slot facts (invalid).

## Diagnostics and unchanged mock launch

**Decision**: Allowlisted random session ID, workflow state, normalized route/intent, status/outcome/reason and latency. Suppress mock stdout/stderr through thin subprocess runner using DEVNULL, no --log-file. Check process and public providers readiness. Normalize appointment path to `/patients/{patientId}/appointments`. Never log URLs/queries, request/response bodies, model debug/output, transcript or exception text. Expose programmer defects via sanitized class/location labels, no locals/state dump.

**Rationale**: Reference audit includes patient path IDs; error bodies can echo identifiers or exception strings. Existing [provenance](../../vendor/reference/PROVENANCE.md) directs suppression/private handling, requiring no source change. An output-suppressed process still needs real readiness verification.

**Alternatives considered**: Raw stdout/file evidence (leak); editing reference logger (breaks unchanged boundary); silently hiding every defect (misleading).

## Optional Enhanced UI and scope

**Decision**: CLI remains baseline. Thin local Marimo is incremental after mandatory verification; pin/test isolated extra at adoption. Explicit selection/confirmation events invoke core authority; reruns never write. Optional lookup, handoff and typo suggestions use returned facts and explicit adoption status. Policy/ZEN, Lab/nxusKit transfer and multi-candidate launch stay deferred.

**Rationale**: Optional UI must not block required core or duplicate effects. [Marimo run button documentation](https://docs.marimo.io/api/inputs/run_button/) fetched 2026-10-08 describes triggered computation/reset; core still owns replay safety.

**Alternatives considered**: Coupled UI-first core; UI controls as sole consent authority; mandatory framework dependencies.

## Qualification limits

All design unknowns needed for Phase 1 are resolved. Named Persona pinning is explicitly deferred. Account/model capability, optional UI version, production authentication and actual delivery remain unqualified. Plan creates neither tasks nor implementation evidence and does not certify assignment timing compliance.
