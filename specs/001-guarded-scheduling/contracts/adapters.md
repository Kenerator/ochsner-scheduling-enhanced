# Adapter contracts

Updated: 2026-10-08. Supplied API wire contract unchanged; authority lives in core.

## Model interpretation

Input: safe scheduling-language projection, validated non-identifying public preferences/state and supported vocabulary. Exclude raw history, phone/DOB/ZIP including alternate encodings, patient records/IDs, booking IDs, request query/body, exceptions and secrets. Local extraction precedes projection; uncertain separation suppresses request. Dates/choice indexes stay local. Never debug/trace raw requests.

Output: intent enum provider_lookup/book/appointment_lookup/human_help/medical_advice/unsupported/clarify; nullable specialty/location suggestions; clear_specialty/clear_location booleans. Every key required, strict schema, no extra properties. Unsupported preference must become unsupported, never silently map to supported value. Invalid/unknown suggestions clarify. No identity/IDs/tools/confirmed/outcome fields. No model-generated factual patient/provider/slot narrative.

Responses REST: configured model, sanitized input, store:false, no tools, text.format json_schema strict:true, bounded time/output. Refusal/incomplete/missing/malformed/wrong keys/types/unavailable output is interpretation failure, no write. Validate independently. Credential/model are environment configuration with separate actual generation qualification; model listing is insufficient. Primary documentation linked in research.

## Scheduling port

| Operation | Wire contract | Guard/result |
|---|---|---|
| Providers | GET /providers; optional specialty/location | No identity/search; valid returned facts only |
| Patient search | GET /patients/search; phone/dob | Private fields; returned matches local; no ZIP query |
| Availability | GET /availability; patientId/specialty, optional location/startDate/endDate | Verified patient, valid ordered dates; returned available/context-bound slots only |
| Booking | POST /appointments; patientId/slotId/confirmed:true | Current consumed consent; valid 201 bound to patient/provider/specialty/location/time/status |
| Appointments (optional) | GET /patients/{patientId}/appointments | Verified patient; only returned patient-bound records |
| Handoff (optional) | POST /handoffs; reason/summary, optional patientId | Minimized template summary; optional ID only verified/needed; queue requires valid 201 |

Response schemas are permissive; application validates required display/authority fields and types. Duplicate IDs, foreign context/patient, invalid time/date or wrong shape never become facts. Preserve exact returned fixed offset. Appointment response has no slotId; bind patient/provider/specialty/location/time/status against selected proposal. Never consult fixture-only conflict/eligibility data.

Allowed handoff reasons: user_requested/identity_unclear/unsupported_request/medical_advice/api_failure/no_availability/other. Reason/source inspection maps only supplied policy sections, no invented rules. Baseline assistance needs no POST.

Reads: bounded timeout/body size, no background retry loops; explicit fresh read allowed. Writes: zero transport/library automatic retries. Valid supplied rejection 400/409 or injected pre-effect 503 is rejected. Unexpected 5xx, transport loss after possible dispatch, truncated/malformed/unbound 201 is unresolved. Provably undispatched may be reported not submitted; otherwise preserve uncertainty. No URL-bearing exception logging. Loopback base URL; separate test ports. X-Mock-Scenario:api_failure is explicit test/demo config propagated to every request including handoff, never model-controlled.

## Diagnostics and mock runner

Allowlisted random session ID, normalized intent/state/route, status, reason/source, milliseconds. No identity/keys/raw path IDs/query/body/prompt/transcript/model output/exception repr. Programmer defects remain visible through sanitized error class/location without captured locals.

Runner uses explicit Python 3.11+ executable and owned local server process, stdout/stderr DEVNULL, no --log-file. Check process and public providers readiness; report sanitized failures, suppression alone is not success. Stop only owned process. Restart resets isolated synthetic store, never reconciles transactions. Tests use separate stores/processes/ephemeral ports; avoid shared Handler.store class state for simultaneous in-process servers.
