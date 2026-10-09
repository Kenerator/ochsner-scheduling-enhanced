# Feature Specification: Guarded AI Appointment Scheduling

**Feature Branch**: `main` (existing local branch; no Git extension or new branch)

**Created**: 2026-10-08

**Status**: Draft — specified for planning; no launch or implementation qualification

**Input**: Operator's Common acceptance contract v1, supplied [client requirements index](../../docs/product/RFP/README.md), and [background stories](../../docs/product/user-stories.md).

## Clarifications

### Session 2026-10-08

- Q: May phone, DOB, ZIP or returned patient records be included in model requests? → A: B: Keep phone, DOB, ZIP and returned patient records outside model requests; collect identity locally and redact messages before model interpretation.

## User Scenarios & Testing *(mandatory)*

Story wording below is **inferred** from the cited supplied requirements/scenarios, rather than verbatim supplied user stories. Origin is distinct from scope: required capabilities remain required. All scenarios use synthetic data. Exact named hypothesis personas were adopted2026-10-09 in [Personas](../../docs/product/personas.md), with retained pins/ancestors. Focused constraints map below; real-user validation remains follow-on and pins confer no permissions.

### User Story 1 - Find providers without identity collection (Priority: P1)

As **Jules / Ellie-Rae, with Billy-June, Nina-Jean and Amy-Lou constraints (hypotheses)**, I want to ask naturally about providers and refine my request across turns, so I can explore care scheduling options without supplying patient identity.

**Origin/basis**: INFERRED wording from assignment Required 1–3 and supplied `provider_lookup` scenario. **Scope**: accepted mandatory.

**Why this priority**: Delivers useful public information and establishes genuine conversational intent recognition without unnecessary identity collection.

**Independent Test**: Run a fresh conversational provider search and compare displayed providers with the actual provider response; no patient search or identity prompt occurs.

**Acceptance Scenarios**:

1. **Given** an unverified user, **When** they ask which primary care providers serve downtown, **Then** genuine model-backed interpretation recognizes provider lookup, the provider service is queried, and only returned provider facts are shown without requesting phone or DOB.
2. **Given** a partial or ambiguous provider request, **When** the user supplies a missing preference in a later turn, **Then** the assistant asks only useful clarifying questions and retains valid prior preferences; omitted optional filters do not require patient identification.
3. **Given** an unsupported specialty or location, **When** lookup cannot satisfy it, **Then** the assistant explains the supported boundary and a truthful human next step without inventing providers or silently substituting preferences.

---

### User Story 2 - Book the exact appointment I confirm (Priority: P1)

As **Jules / Ellie-Rae, with Billy-June, Nina-Jean and Amy-Lou constraints (hypotheses)**, I want to supply missing information gradually, choose a real available appointment, and explicitly confirm the exact proposal, so the assistant books only the appointment I currently intend.

**Origin/basis**: INFERRED wording from assignment Required 1, 2, 4, policies Identity and Booking, and `happy_path_booking`. **Scope**: accepted mandatory.

**Why this priority**: This is the assignment's consequential end-to-end outcome; optional features must not delay it.

**Independent Test**: With reset synthetic state, identify one patient, retrieve available slots, select and confirm one, and verify the actual created appointment. Exercise missing fields and corrections in separate runs.

**Acceptance Scenarios**:

1. **Given** an incomplete booking request, **When** the user converses across turns, **Then** the assistant asks for missing phone, DOB, specialty and slot choice as needed, preserves valid supplied information, and verifies identity before patient-specific output or availability lookup.
2. **Given** exactly one phone+DOB match, **When** valid specialty and optional location/date bounds are available, **Then** only service-returned available slots and their returned times are shown; fixture times retain their fixed offset semantics.
3. **Given** a selected returned slot, **When** the assistant presents its exact patient-bound proposal, **Then** selection alone does not book; only an explicit current user confirmation bound to that proposal permits the booking request.
4. **Given** such confirmation, **When** the service returns a valid created appointment, **Then** the assistant reports booking using that returned result rather than a model prediction or local assumption.
5. **Given** an outstanding proposal or prior confirmation, **When** identity, specialty, location, dates or choice changes, **Then** old proposal and consent become invalid, applicable identity/results are refreshed, and fresh proposal confirmation is required. An ambiguous “yes” or repeated stale confirmation causes no write.
6. **Given** malformed, unavailable or adversarial model output, **When** it proposes fabricated IDs, a slot, or consent, **Then** deterministic validation prevents that output from granting authority or causing a consequential effect; a useful explanation or follow-up replaces guessing.

---

### User Story 3 - Receive a private, truthful failure and next step (Priority: P1)

As **Jules / Ellie-Rae, with Billy-June, Nina-Jean and Amy-Lou constraints (hypotheses)**, I want unresolved identity, unavailable scheduling and unsupported requests explained plainly, so I can seek real help without disclosure or false assurance.

**Origin/basis**: INFERRED wording from assignment Required 5, all supplied policies and failure scenarios. **Scope**: no-match baseline mandatory; duplicate, medical advice, conflict and outage guards accepted mandatory by Operator contract. Other policy boundaries always apply, even when optional scenario coverage is deferred.

**Why this priority**: A truthful failure is part of the minimum; privacy and effect boundaries apply to every supported path.

**Independent Test**: Use no-match synthetic input and verify no patient-specific disclosure or booking, with a concrete user-initiated human next step. Independently exercise each guard below.

**Acceptance Scenarios**:

1. **Given** no patient match, **When** a booking lookup completes, **Then** no patient/appointment data is revealed or guessed, the assistant offers private correction of submitted details or contact with the scheduling team, and it does not claim a handoff was queued.
2. **Given** duplicate phone+DOB matches, **When** identity is unresolved, **Then** the assistant asks privately for ZIP without displaying candidate names, ZIPs or records; ZIP filters only already-returned matches. Zero or still-multiple matches lead to a truthful human next step, not availability or booking.
3. **Given** a medical-advice request, request for a human, or unsupported scheduling request, **When** interpreted, **Then** the assistant gives no clinical advice or triage and explains the human-help boundary. It does not invent contact details or promise delivery.
4. **Given** a confirmed choice, **When** booking returns a slot conflict, **Then** the assistant does not report booked, invalidates the old proposal/consent, and offers another returned option with fresh confirmation or a human next step.
5. **Given** empty availability or scheduling outage, **When** the service returns that result, **Then** the assistant states the actual issue and a usable next step, never fabricated slots, bookings or queue success; retry loops are avoided.
6. **Given** a booking request whose result cannot be determined, **When** its response is lost, times out or cannot establish success, **Then** the assistant labels the outcome unresolved, warns against repeating the booking before reconciliation, and supplies a human reconciliation step without blind write retry or false success/failure certainty.

---

### User Story 4 - Refine preferences and inspect existing appointments (Priority: P2)

As **Jules / Ellie-Rae, with Billy-June, Nina-Jean and Amy-Lou constraints (hypotheses)**, I want clear corrections, optional date filters and my verified existing appointment details, so I can make an informed scheduling choice.

**Origin/basis**: INFERRED wording from assignment Good-to-have, `multiple_patient_matches` lookup example, and Operator Enhanced lane preference. **Scope**: Enhanced target; appointment lookup and provider typo suggestions are optional relative to the assignment minimum. Preference corrections that invalidate consent are already mandatory in Story 2.

**Why this priority**: Improves review usability without blocking the required slice.

**Independent Test**: Retrieve appointments for a verified synthetic patient; separately revise filters and confirm that changed choices require fresh consent.

**Acceptance Scenarios**:

1. **Given** an appointment lookup request, **When** identity is verified, **Then** only that patient's returned appointments are shown; before verification none are disclosed.
2. **Given** valid date bounds, **When** availability is requested, **Then** the supported bounds are used; invalid or reversed dates prompt correction, not a misleading empty result.
3. **Given** a misspelled provider preference, **When** suggestions are offered, **Then** suggestions derive from returned provider data, require user selection, and do not fabricate a provider search parameter or silently change a booking choice.

---

### User Story 5 - Understand recovery context without sensitive transcripts (Priority: P2)

As **Morgan-Rae — human support hypothesis**, I want factual outcome and reason context, so I can distinguish attempted, completed and unknown actions and help safely.

**Origin/basis**: INFERRED background Support/Admin story reconciled with policies Observability and Human Handoff. **Scope**: minimal privacy-safe diagnostic/documentation coverage required; queued handoff is Enhanced target/assignment optional. No admin console, new access permissions or live delivery capability is implied.

**Why this priority**: Reviewers and support need truthful evidence, especially for failed or uncertain effects.

**Independent Test**: Inspect sanitized diagnostics for successful, rejected and unknown outcomes; optionally test an actual mock handoff response.

**Acceptance Scenarios**:

1. **Given** any tested scheduling outcome, **When** a permitted diagnostic is inspected, **Then** workflow state, normalized route, outcome/reason and latency explain what happened without identity, credentials or conversation text.
2. **Given** optional handoff support, **When** a handoff is requested, **Then** its allowed reason and factual minimized summary contain no raw identity/transcript; queued is claimed only on a successful created handoff response.
3. **Given** injected scheduling outage, **When** handoff is also attempted, **Then** outage injection remains active, the handoff failure is reported truthfully, and the assistant gives an actual user-initiated contact/retry-later step without claiming a queue or delivery.

---

### User Story 6 - Reproduce and judge the PoC honestly (Priority: P2)

As **Sam-Rae — AGENT QA hypothesis**, I want declared setup, bounded demonstrations and inspectable source-based decisions, so I can reproduce the behavior and understand its limitations.

**Origin/basis**: INFERRED wording from assignment What To Submit, Operator lane preferences, and Constitution V–VII. **Scope**: reproduction/disclosure required; the Enhanced candidate is authorized and adopted; other candidate lanes have independent owners.

**Why this priority**: A working mandatory slice must be reviewable independently of optional candidates.

**Independent Test**: A reviewer follows only declared clone/setup/run/reset instructions and observes the provider, booking and no-match flows; specialized variants are evaluated only if actually adopted.

**Acceptance Scenarios**:

1. **Given** fresh authenticated private GitHub clones on both Mac ARM and Minty Linux, **When** the reviewer follows README instructions, **Then** the supplied mock and assistant run with documented prerequisites, test commands and reset steps, without a developer credential vault dependency.
2. **Given** preparation or deterministic doubles only, **When** evidence is presented, **Then** it is labeled accordingly; live AI qualification requires actual model generation behavior and credential capability evidence, not a model-listing response.
3. **Given** a completed video, **When** reviewed, **Then** its duration is at most five minutes and it includes actual provider lookup, confirmed booking, one failure, authority boundaries, architecture and limitations without exposing credentials or overstating timing compliance.
4. **Given** specialized Policy or Lab-inspired candidate evidence, **When** inspected, **Then** policy decisions cite supplied sources/reasons, proposed effects remain deterministically validated, evidence is redacted, and optional dependencies do not prevent the baseline from running.

### Edge Cases

- Partial identity, invalid calendar dates, reversed bounds, omitted optional filters, unknown specialties/locations, and ambiguous slot references require useful clarification or a policy-based human next step.
- Identity corrections clear verification and all dependent results; preference or selection corrections invalidate the proposal and consent. Previously consumed consent never authorizes another write.
- Duplicate ZIP filtering must end in exactly one already-returned patient; no disclosure of alternatives or invented server parameter is permitted.
- A currently available slot may conflict at booking; the assistant cannot anticipate conflicts using fixture internals or IDs reserved by the test setup.
- Empty/malformed API responses and malformed/unavailable model results must not produce invented data or authoritative state changes. An untrusted booking response after a possible write is unresolved.
- A timeout after submission is different from a definite rejection. Restart/reset is a synthetic test operation, not proof that an uncertain booking failed.
- A scheduling outage also affects handoffs. A queued mock record is not a delivered human response.
- The supplied mock's appointment-route audit includes patient path IDs; privacy requirements apply to mock output as well as assistant/model/transport logs. Planning must provide safe log handling without replacing the backend or silently modifying source assets.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The assistant MUST use genuine model-backed text interpretation for provider lookup and booking across multiple turns, ask useful missing-information questions, preserve valid context and disclose AI interaction (Stories 1–2).
- **FR-002**: Provider lookup MUST call `GET /providers` with supported optional specialty/location filters, present only returned facts and never require patient identity (Story 1).
- **FR-003**: Booking MUST verify identity through phone+DOB `GET /patients/search`. Exactly one match is required; no-match MUST permit private correction or human assistance without data disclosure. Duplicate matches MUST use private ZIP filtering over returned matches, never a server ZIP query or candidate disclosure. Phone, DOB and ZIP MUST be collected locally; these values and returned patient records MUST remain outside all model requests. User messages MUST be redacted before model interpretation, including messages that mix identity with scheduling preferences (Stories 2–3).
- **FR-004**: No patient-specific output or action, including availability or appointment details, MUST occur before verification. Mock matching MUST be described as prototype verification, not production authentication (Stories 2–4).
- **FR-005**: Availability MUST call `GET /availability` with verified `patientId` and supported `specialty`, optionally valid `location`, `startDate`, `endDate`; bounds MUST be calendar-valid and ordered. Only returned available slots and their returned `startTime` MUST be offered, preserving fixed `-05:00` fixture semantics without DST reinterpretation (Stories 2, 4).
- **FR-006**: Deterministic code MUST own identity, authoritative IDs, available choices, proposal state, consent and effects. Model output MUST NOT invent IDs/slots, grant authoritative consent, or bypass validation. Missing/invalid/unavailable model results MUST cause no consequential effect (Story 2).
- **FR-007**: Before booking, the assistant MUST display an exact proposal tied to the verified patient and selected returned slot, including specialty, location and returned time. Explicit current user confirmation MUST bind that proposal; intent, slot selection or model-supplied `confirmed` MUST NOT suffice (Story 2).
- **FR-008**: Changes to identity, preferences or choice MUST invalidate stale proposals/consent and dependent results as applicable. Consumed, ambiguous or stale confirmation MUST cause no booking; changed proposals require fresh explicit confirmation (Story 2).
- **FR-009**: `POST /appointments` with `patientId`, selected `slotId`, `confirmed: true` MUST occur only after FR-003–008. “Booked” MUST derive only from an actual `201` with a valid appointment result bound to that request, never local prediction (Story 2).
- **FR-010**: `409` MUST be reported as not booked and clear stale consent; other returned options require fresh confirmation. An unknown write outcome MUST remain unresolved, with reconciliation before any new attempt; no blind POST retry or idempotency guarantee is allowed because the API provides no idempotency keys (Story 3).
- **FR-011**: No-match is the required demonstration failure. The assistant MUST also guard duplicates, medical advice, conflicts and outages; explain empty availability truthfully; and supply concrete recovery/human next steps without fabricated data or promises. Assistant logic MUST NOT inspect fixture-only conflict flags or special-case trap IDs (Story 3).
- **FR-012**: All supplied policy handoff boundaries MUST apply: human request, unsupported scope/specialty/location/appointment type, unresolved identity, downstream unavailability and medical advice. No clinical advice or triage, invented established-patient eligibility or clinical rules, or unsupported reschedule/cancel operation is allowed. Human escalation can be a truthful user-initiated next step when queue support is absent (Story 3).
- **FR-013**: If appointment lookup is adopted, it MUST use verified identity and `GET /patients/{patientId}/appointments`, expose only returned details, and retain the same correction/privacy boundaries. This is an Enhanced target, not an assignment-minimum prerequisite (Story 4).
- **FR-014**: If queued handoff is adopted, `POST /handoffs` MUST use one of the supplied reason values and a factual minimized summary without raw transcript/identity. Optional `patientId` MUST be verified and used only when necessary. Queued MUST be claimed only from actual `201`; `X-Mock-Scenario: api_failure` MUST remain on every affected request including handoff (Story 5).
- **FR-015**: Diagnostics MUST whitelist normalized routes with patient path IDs redacted, random non-identifying session IDs, workflow state/normalized intent, status/reason and latency. Phone, DOB, ZIP, keys, raw query/body/prompt/transcript MUST NOT enter logs, exception traces, model SDK debug output or retained reviewer evidence. Supplied server output needs equivalent handling when appointment lookup is enabled (Story 5).
- **FR-016**: The supplied standard-library server and synthetic fixtures MUST be used without a replacement backend/DB. Candidate lanes MUST have independent mock processes/resettable state and separate roots/native stage state. Reset MUST be documented and never represented as transaction reconciliation (Story 6).
- **FR-017**: README MUST document clone → supplied mock → assistant, prerequisites, configurable standard environment key/model, exact tests/demos/reset, AI/mock disclosure, architecture/decisions/assumptions/tradeoffs, limitations and linked next steps. Clean reproduction evidence MUST be labeled honestly. Private selective vendoring of server/data/OpenAPI is approved for reviewer reproducibility; whole intake/email/credentials MUST be excluded, and sharing originals requires a separate grant (Story 6).
- **FR-018**: Live AI/demo qualification MUST require an actual credential-capability and generation/behavior test, not deterministic doubles or models-list HTTP 200. Model choice MUST be explicit/configurable after qualification; no subscription entitlement assumption or secret in prompt/log/README/Git/local credential copy is allowed. Reviewers MUST NOT require Bitwarden at runtime (Story 6).
- **FR-019**: The eventual video MUST be no longer than five minutes and show provider lookup, booking, at least one truthful failure and boundaries. The required assignment three-hour statement MUST appear only if supported by actual timing evidence; unsupported compliance MUST be recorded honestly, not asserted (Story 6).
- **FR-020**: Enhanced MUST remain independently runnable and accurately disclose adopted components and lane differences. Policy/Lab implementations belong to separate candidate owners; no component or engine may be represented as adopted merely because preparation succeeded (Story 6).

### Key Entities *(include if feature involves data)*

- **Conversation session**: Random identifier, current intent, supplied preferences, unresolved fields and authoritative workflow state; identity is private and not diagnostic content.
- **Patient verification**: Phone+DOB search result and optional private duplicate ZIP clarification; exactly one returned patient identifier grounds patient-specific work. Identity values and returned patient records remain local to the deterministic workflow and scheduling adapter, outside model requests.
- **Provider**: Returned identifier, name, specialty, locations and modalities; public lookup facts, not clinical recommendations.
- **Available slot**: Returned identifier, provider, specialty, location, available state and exact returned time associated with the verified search.
- **Booking proposal and consent**: Exact patient/slot choice and current preference context plus explicit user confirmation; invalidated by changes and consumed by submission.
- **Appointment outcome**: Actual returned appointment/result or definite rejection versus unresolved submission; uncertainty is distinct from both booked and failed.
- **Handoff/recovery context**: Supported reason, minimized factual summary and actual queue result if adopted; otherwise user-initiated next step without delivery claims.
- **Diagnostic evidence**: Whitelisted non-identifying event fields and measured latency, with source/reason identifiers when specialized inspection is adopted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In every required provider test, users receive only returned provider facts and zero identity prompts or patient searches.
- **SC-002**: In the synthetic booking acceptance flow, users can provide at least two missing fields across separate turns, choose a returned option and explicitly confirm it; exactly one matching created appointment is reported.
- **SC-003**: Across all no-confirmation, stale-confirmation, changed-identity/preference/choice and malformed/unavailable-model cases, zero unauthorized bookings or patient disclosures occur.
- **SC-004**: Every no-match, unresolved duplicate, medical-advice, conflict and outage case presents an accurate outcome and concrete next step, with zero invented patient/slot data, clinical advice or false queued/booked claims.
- **SC-005**: Every unknown booking outcome remains labeled unresolved and results in zero blind booking retries; users are told to reconcile before repeating the action.
- **SC-006**: A reviewer can reproduce provider, confirmed booking and no-match flows and reset synthetic state using only declared prerequisites and instructions; all reviewed logs/evidence contain zero excluded identity, credential or conversation fields. Across initial, mixed identity/preference, correction and duplicate-resolution turns, every inspected model request contains zero phone, DOB, ZIP or returned patient records.
- **SC-007**: The recorded demonstration lasts at most five minutes, includes all three required flows and explains authority boundaries and limitations. Every live-AI, optional-adoption or time-window claim has corresponding evidence or an explicit unqualified/deferred status.
- **SC-008**: Useful acknowledgement targets 400 ms where feasible; measure feedback and completion separately for the required flows, recording environment/load and misses rather than claiming unmeasured compliance. A pending model/service response must remain distinguishable from completion.

## Assumptions

### Source reconciliation and dependencies

- Precedence is the supplied assignment and policies (retained locally under the private intake index), summarized as accepted requirements in this specification, and the approved vendored [OpenAPI](../../vendor/reference/openapi/scheduling-api.yaml), with Operator constraints preserving the minimum and adding privacy/effect guards. All eleven manifest text entries were read, including reference server and synthetic data. Suggested scenario priorities do not promote optional appointment lookup or queued handoff into assignment minimum.
- The supplied `api_failure` scenario suggests creating a queued handoff, but the server returns `503` for every request under the injected outage, including handoffs. FR-014 and Story 5 require truthful failure rather than claiming an impossible queued result.
- Fixture internal dates/times/conflict flags belong only to the server. The returned fixed-offset time is authoritative. The presence of `establishedPatient` does not impose eligibility rules.
- Assignment external effort budget is three hours from full-package receipt, with video due thirty minutes after the coding deadline and the last authorized pushed commit used for review. The recorded receipt anchor is 2026-10-08 22:41 America/Chicago; compliance must be supported by actual execution evidence. The Operator owns budget compliance/tradeoffs; agents report timing without independently shrinking/stopping work. No deadline, push or timing certification is inferred from this stage.
- Supplied temporary-key guidance is superseded operationally by the explicit eventual Operator credential preference. Application calls uses an ordinary environment API key at runtime. The authorized development qualification uses a trusted local credential helper into process-local environment; this document contains no credential. Actual generation qualification is separate from model listing. Reviewer configuration remains ordinary environment key/model.
- `.DS_Store` is the sole manifest attachment and was identified as Apple desktop metadata, not interpreted as requirements. No material non-text client requirement is known from the manifest; no claim is made that its binary contents were reviewed.
- Exact hypothesis persona selection/pinning is recorded in [personas](../../docs/product/personas.md); real-user validation remains pending. Named persona demographics, validated preferences and permissions are not inferred. Predictable correction, minimal identity collection, useful error recovery and support evidence are current source-backed needs.
- Existing scaffold decisions describe generic mechanisms, not supplied scheduling implementation or cross-process idempotency. This spec's unknown-outcome and consent requirements govern the candidate; legacy “hands off” wording is not proof of a queue.

### Candidate scope and launch boundary

- This invocation creates **one native feature**, representing the Enhanced candidate and the common acceptance baseline. Four candidate tasks are launched independently under the current Operator grant; this spec neither creates four products nor executes other native stages.
- **MVP**: simplest genuine AI, guarded core and conversational CLI; a thin prepared Marimo form where practical. **Enhanced**: user-centered Marimo, preferences/corrections, authoritative provider typo suggestions, appointment lookup and truthful handoff. **Policy**: inspectable source/reason decisions, prepared ZEN tables only if useful. **Lab-inspired**: selected standalone event/submission validation and redacted inspection patterns, with provenance/licenses; no full SDK-dependent Lab import. Detailed implementation choices remain for Plan.
- Enhanced Marimo, RapidFuzz suggestions, appointment lookup and truthful handoff are explicitly adopted; remaining optional targets can be incrementally adopted with explicit status; they never gate a working mandatory slice or require all four candidates to finish. Required consent corrections and policy/privacy guards cannot be deferred as UX extras.
- If two or more consumers benefit, an isolated component owner may define pure decision/API-helper fields, errors and source/reason IDs. Reviewed named source commits transfer separately into local imports without sibling dependency/shared mutable code. Each candidate retains consent, effects and uncertain-outcome boundaries; component readiness is not consumer adoption. No optional component transfer is executed here.
- No replacement backend, production identity authentication, clinical eligibility/triage, invented reschedule/cancel endpoint, live delivery service, new admin console, external publication or deployment is accepted by this specification.
- Tests-first implementation, independent safe work ownership, required success/failure verification and near-final source-reviewed as-built docs belong in Plan/Tasks. Stubs and unresolved persona selection do not block implementation; this Specify checklist measures requirement quality only.
